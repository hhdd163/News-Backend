from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.base import NewsItemBase

from cache.news_cache import (
    get_cached_categories, set_cached_categories, 
    get_cached_news_list, set_cached_news_list,
    get_cached_news_detail, set_cached_news_detail,
    get_cached_related_news, set_cached_related_news
)
from models.news import Category, News



# 获取新闻分类数据
async def get_categories(db: AsyncSession,skip: int = 0, limit: int = 100):
    # 先尝试从缓存中获取数据
    cached_categories =  await get_cached_categories()
    if cached_categories:
        return cached_categories

    # 先获取数据库里面新闻分类数据 -> 先定义模型类 -> 封装查询数据的方法
    stmt = select(Category).offset(skip).limit(limit)
    result = await  db.execute(stmt)
    categories = result.scalars().all()  #ORM

    # 写入缓存
    if categories:
        categories = jsonable_encoder(categories)
        await set_cached_categories(categories)
    # 返回数据
    return categories


# 获取新闻列表数据
async def get_news_list(db: AsyncSession, category_id: int, skip: int =0 , limit:int = 10):
    # 先尝试从缓存获取新闻列表
    # 跳过的数量 = (页码-1) * 每页数量 -> 页码 = 跳过的数量 // 每页数量 + 1
    page = skip // limit + 1
    cached_list = await get_cached_news_list(category_id,page,limit)
    if cached_list:
        # return cached_list  # 要的是 ORM
        return [News(**item) for item in cached_list]


    # 查询的是指定分类下的所有新闻
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()

    # 写入缓存
    if news_list:
        # 先把 ORM 数据 转换成字典才能写入缓存
        # 方式一:
        # 自动把 ORM 对象转成 JSON 字典
        # news_list = jsonable_encoder(news_list)
        # 方式二:
        # ORM 转成 Pydantic, 再转成字典
        # by_alias=False 不使用别名, 保存Python风格, 因为 Redis数据是给后端用的
        # jsonable_encoder = 快速转换，简单省事 ✅
        # model_validate + model_dump = 严谨规范，大型项目首选 ✅
        news_data = [NewsItemBase.model_validate(item).model_dump(mode="json",by_alias=False) for item in news_list]
        await set_cached_news_list(category_id,page,limit,news_data)
    return news_list



# 获取新闻列表数量
async def get_news_count(db: AsyncSession, category_id: int):
    """
    获取指定分类下的新闻总数
    
    Args:
        db: 数据库会话对象
        category_id: 分类ID
    
    Returns:
        int: 新闻总数
    """
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()

# 获取新闻详情（带缓存）
async def get_news_detail(db: AsyncSession, news_id: int):
    """
    获取新闻详情（优先从缓存读取）
    
    处理流程：
    1. 尝试从缓存获取新闻详情（包含所有字段）
    2. 如果缓存命中，使用缓存数据构造字典返回
    3. 如果缓存未命中，查询数据库并写入缓存
    
    Args:
        db: 数据库会话对象
        news_id: 新闻ID
    
    Returns:
        dict: 新闻详情数据（字典格式），不存在返回 None
    """
    # 先尝试从缓存获取
    cached_detail = await get_cached_news_detail(news_id)
    if cached_detail:
        # 缓存命中，实时查询当前浏览量并合并
        stmt = select(News.views).where(News.id == news_id)
        result = await db.execute(stmt)
        current_views = result.scalar_one()
        
        # 合并缓存数据和实时浏览量
        cached_detail['views'] = current_views
        return cached_detail  # 直接返回字典
    
    # 缓存未命中，查询数据库
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    news_detail = result.scalar_one_or_none()
    
    # 写入缓存（包含所有字段）
    if news_detail:
        # 转换为字典，包含所有必要字段
        news_data = {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "description": news_detail.description,
            "image": news_detail.image,
            "author": news_detail.author,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,  # 缓存时也保存 views，但会被实时值覆盖
            "publishTime": news_detail.publish_time.strftime("%Y-%m-%d %H:%M:%S") if news_detail.publish_time else None,
        }
        await set_cached_news_detail(news_id, news_data)
        return news_data  # 返回字典
    
    return None

# 增长新闻浏览量
async def increase_news_views(db: AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views = News.views + 1)
    result = await db.execute(stmt)
    await db.commit()

    # 更新 -> 检查数据库是否真的命中了数据 -> 命中了返回True
    return result.rowcount > 0


# 获取相关新闻
async def get_related_news(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    """
    获取相关新闻推荐（优先从缓存读取）
    
    处理流程：
    1. 尝试从缓存获取相关推荐
    2. 如果缓存命中，直接返回
    3. 如果缓存未命中，查询数据库并写入缓存
    
    Args:
        db: 数据库会话对象
        news_id: 当前新闻ID（需要排除）
        category_id: 分类ID
        limit: 返回数量，默认5条
    
    Returns:
        list: 相关新闻列表
    """
    # 先尝试从缓存获取
    cached_related = await get_cached_related_news(news_id)
    if cached_related:
        return cached_related
    
    # 缓存未命中，查询数据库
    stmt = select(News).where(
        News.category_id == category_id,
        News.id != news_id
    ).order_by(
        News.views.desc(),
        News.publish_time.desc()
    ).limit(limit)
    
    result = await db.execute(stmt)
    related_news = result.scalars().all()
    
    # 构建返回数据（只缓存必要字段）
    related_data = [{
        "id": news.id,
        "title": news.title,
        "content": news.content[:200] if news.content else "",  # 只缓存摘要
        "image": news.image,
        "author": news.author,
        "publishTime": news.publish_time.strftime("%Y-%m-%d %H:%M:%S") if news.publish_time else None,
        "categoryId": news.category_id,
        "views": news.views,
    } for news in related_news]
    
    # 写入缓存
    if related_data:
        await set_cached_related_news(news_id, related_data)
    
    return related_data
