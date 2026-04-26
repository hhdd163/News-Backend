"""
定时任务模块

处理需要定期执行的任务，如浏览量同步、缓存清理等。
"""
import asyncio
from datetime import datetime
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import AsyncSessionLocal
from cache.news_cache import (
    get_all_news_views_keys,
    get_news_views_from_cache,
    delete_news_views_cache,
    NEWS_VIEWS_PREFIX
)
from models.news import News


async def sync_views_to_database():
    """
    同步 Redis 中的浏览量增量到数据库
    
    执行流程：
    1. 获取所有有浏览量增量的新闻ID
    2. 批量更新数据库中的浏览量
    3. 清除已同步的 Redis 计数器
    
    建议执行频率：每 5-10 分钟执行一次
    """
    async with AsyncSessionLocal() as db:
        try:
            # 获取所有有浏览量增量的新闻
            keys = await get_all_news_views_keys()
            
            if not keys:
                print(f"[{datetime.now()}] 没有需要同步的浏览量数据")
                return
            
            print(f"[{datetime.now()}] 开始同步浏览量，共 {len(keys)} 条记录")
            
            # 批量更新
            for key in keys:
                # 提取新闻ID
                news_id = int(key.replace(NEWS_VIEWS_PREFIX, ""))
                
                # 获取增量
                increment = await get_news_views_from_cache(news_id)
                
                if increment > 0:
                    # 更新数据库
                    stmt = update(News).where(News.id == news_id).values(
                        views=News.views + increment
                    )
                    await db.execute(stmt)
                    
                    # 清除 Redis 计数器
                    await delete_news_views_cache(news_id)
            
            # 提交事务
            await db.commit()
            print(f"[{datetime.now()}] 浏览量同步完成")
            
        except Exception as e:
            print(f"[{datetime.now()}] 浏览量同步失败: {e}")
            await db.rollback()


async def start_scheduler():
    """
    启动定时任务调度器
    
    在应用启动时调用此函数
    """
    print("启动定时任务调度器...")
    
    while True:
        try:
            # 每 5 分钟执行一次同步
            await asyncio.sleep(300)  # 300秒 = 5分钟
            await sync_views_to_database()
        except Exception as e:
            print(f"定时任务执行异常: {e}")
            await asyncio.sleep(60)  # 异常后等待1分钟重试


# 如果直接运行此文件，启动调度器
if __name__ == "__main__":
    asyncio.run(start_scheduler())
