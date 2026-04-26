"""
收藏功能数据操作层（CRUD）

封装收藏相关的数据库操作，包括检查收藏状态、添加/删除收藏、获取收藏列表等。
所有函数均为异步函数，使用 SQLAlchemy 异步会话进行操作。
"""
# 检查收藏状态: 当前用户是否收藏了该新闻
from fastapi import Depends
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from cache.favorite_cache import (
    get_cached_favorite_status, 
    set_cached_favorite_status,
    delete_cached_favorite_status
)
from models.favorite import Favorite
from models.news import News

# ==================== 检查收藏状态 ====================
async def is_news_favorite(
    db: AsyncSession,
    user_id: int,
    news_id: int
):
    """
    检查用户是否已收藏指定新闻（优先从缓存读取）
    
    处理流程：
    1. 尝试从缓存获取收藏状态
    2. 如果缓存命中，直接返回
    3. 如果缓存未命中，查询数据库并写入缓存
    
    Args:
        db: 数据库会话对象
        user_id: 用户ID
        news_id: 新闻ID
    
    Returns:
        bool: 已收藏返回 True，未收藏返回 False
    """
    # 先尝试从缓存获取
    cached_status = await get_cached_favorite_status(user_id, news_id)
    if cached_status is not None:
        # 缓存命中，直接返回
        return cached_status == "1"
    
    # 缓存未命中，查询数据库
    query = select(Favorite).where(
        Favorite.user_id == user_id,
        Favorite.news_id == news_id
    )
    result = await db.execute(query)
    is_favorite = result.scalar_one_or_none() is not None
    
    # 写入缓存
    await set_cached_favorite_status(user_id, news_id, is_favorite)
    
    return is_favorite

# ==================== 添加收藏 ====================
async def add_news_favorite(
    db: AsyncSession,
    user_id: int,
    news_id: int
):
    """
    添加新闻收藏
    
    Args:
        db: 数据库会话对象
        user_id: 用户ID
        news_id: 新闻ID
    
    Returns:
        Favorite: 创建的收藏记录对象
    """
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)  # 刷新对象，获取生成的 ID
    
    # 清除收藏状态缓存
    await delete_cached_favorite_status(user_id, news_id)
    
    return favorite

# ==================== 取消收藏 ====================
async def remove_news_favorite(
    db: AsyncSession,
    user_id: int,
    news_id: int
):
    """
    取消新闻收藏
    
    Args:
        db: 数据库会话对象
        user_id: 用户ID
        news_id: 新闻ID
    
    Returns:
        bool: 删除成功返回 True，记录不存在返回 False
    """
    stmt = delete(Favorite).where(
        Favorite.user_id == user_id,
        Favorite.news_id == news_id
    )
    result = await db.execute(stmt)
    await db.commit()
    
    # 清除收藏状态缓存
    await delete_cached_favorite_status(user_id, news_id)
    
    return result.rowcount > 0  # rowcount > 0 表示有记录被删除

# ==================== 获取收藏列表（分页） ====================
async def get_favorite_list(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 10
):
    """
    获取用户的收藏列表（带分页）
    
    使用联表查询（JOIN）获取收藏的新闻信息和收藏时间。
    
    Args:
        db: 数据库会话对象
        user_id: 用户ID
        page: 页码，从1开始
        page_size: 每页数量
    
    Returns:
        tuple: (rows, total)
            - rows: 收藏记录列表，每项为 (新闻对象, 收藏时间, 收藏ID)
            - total: 收藏总数
    """
    # 获取收藏总数
    count_query = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 联表查询：获取收藏的新闻信息 + 收藏时间 + 收藏ID
    # 使用 label() 为字段设置别名
    query = (
        select(
            News,
            Favorite.created_at.label("favorite_time"),  # 收藏时间别名
            Favorite.id.label("favorite_id")  # 收藏ID别名
        )
        .join(Favorite, News.id == Favorite.news_id)  # 联表条件
        .where(Favorite.user_id == user_id)  # 过滤当前用户
        .order_by(Favorite.created_at.desc())  # 按收藏时间降序排序
        .offset(offset)  # 分页偏移
        .limit(page_size)  # 每页数量
    )

    result = await db.execute(query)
    rows = result.all()  # 返回所有结果
    return rows, total

# ==================== 清空收藏列表 ====================
async def remove_all_favorite(
    db: AsyncSession,
    user_id: int
):
    """
    清空用户的所有收藏记录
    
    Args:
        db: 数据库会话对象
        user_id: 用户ID
    
    Returns:
        int: 删除的记录数量
    """
    # 先获取该用户的所有收藏记录，用于清除缓存
    query = select(Favorite.news_id).where(Favorite.user_id == user_id)
    result = await db.execute(query)
    news_ids = [row[0] for row in result.all()]
    
    # 删除所有收藏记录
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    
    # 清除该用户所有新闻的收藏状态缓存
    for news_id in news_ids:
        await delete_cached_favorite_status(user_id, news_id)

    # 返回删除的记录数量（rowcount 为 0 时返回 0）
    return result.rowcount or 0