"""
新闻模块路由

提供新闻分类、列表、详情等相关 API 接口。
使用 Redis 缓存提升查询性能，减少数据库压力。
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud import news_cache
from utils.response import success_response

# ==================== 路由器配置 ====================
# 创建 APIRouter 实例
# prefix: 路由前缀，所有接口路径都会加上 /api/news
# tags: Swagger UI 中的分组标签，便于接口文档分类展示
router = APIRouter(prefix= "/api/news", tags=["news"])

# ==================== 接口实现流程说明 ====================
# 1. 模块化路由 -> API 接口规范文档（Swagger UI 自动生成）
# 2. 定义模型类 -> 数据库表（数据库设计文档）
# 3. 在 crud 文件夹里创建文件，封装操作数据库的方法
# 4. 在路由处理函数里面调用 crud 封装好的方法，返回结果

# ==================== 获取新闻分类 ====================
@router.get("/categories")
async def get_categories(
    skip: int = 0,  # 跳过记录数，用于分页
    limit: int = 100,  # 每页数量
    db: AsyncSession = Depends(get_db)  # 依赖注入数据库会话
):
    """
    获取新闻分类列表
    
    从缓存或数据库中获取新闻分类数据，优先使用缓存提升性能。
    
    Args:
        skip: 跳过的记录数，默认0
        limit: 每页数量，默认100
        db: 数据库会话对象
    
    Returns:
        dict: 包含 code、msg、data 的响应对象
    """
    # 从缓存或数据库获取新闻分类数据
    categories = await news_cache.get_categories(db, skip, limit)
    return success_response(message="获取新闻分类成功", data=categories)

# ==================== 获取新闻列表 ====================
@router.get("/list")
async def get_news_list(
    category_id: int = Query(..., alias="categoryId"),  # 分类ID，必填参数
    page: int = 1,  # 页码，默认第1页
    page_size: int = Query(10, alias="pageSize"),  # 每页数量，默认10条
    db: AsyncSession = Depends(get_db)  # 依赖注入数据库会话
):
    """
    获取指定分类下的新闻列表（带分页）
    
    根据分类ID查询新闻列表，支持分页功能。
    计算总数量和是否有更多数据，用于前端分页显示。
    
    Args:
        category_id: 新闻分类ID，必填
        page: 页码，从1开始
        page_size: 每页显示数量
        db: 数据库会话对象
    
    Returns:
        dict: 包含新闻列表、总数、是否有更多数据的响应对象
    """
    # 计算跳过的记录数：(当前页码 - 1) × 每页数量
    skip = (page - 1) * page_size
    # 从缓存或数据库获取新闻列表
    news_list = await news_cache.get_news_list(db, category_id, skip, page_size)
    # 获取该分类下的新闻总数
    total = await news_cache.get_news_count(db, category_id)
    # 判断是否还有更多数据：总数 > 已返回的数量
    has_more = total > skip + len(news_list)
    return success_response(
        message="获取新闻列表成功",
        data={
            "list": news_list,
            "total": total,
            "has_more": has_more
        }
    )

# ==================== 获取新闻详情 ====================
@router.get("/detail")
async def get_news_detail(
    news_id: int = Query(..., alias="id"),  # 新闻ID，必填参数
    db: AsyncSession = Depends(get_db)  # 依赖注入数据库会话
):
    """
    获取新闻详情（包含相关推荐）
    
    根据新闻ID获取详细信息，同时增加浏览量并返回相关新闻推荐。
    
    Args:
        news_id: 新闻ID，必填
        db: 数据库会话对象
    
    Returns:
        dict: 包含新闻详情和相关推荐的响应对象
    
    Raises:
        HTTPException: 当新闻不存在或更新失败时抛出404错误
    """
    # 获取新闻详情（带缓存）
    news_detail = await news_cache.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")
    
    # 增加浏览量（用户每次查看详情，浏览量+1）
    views_res = await news_cache.increase_news_views(db, news_detail['id'])
    if not views_res:
        raise HTTPException(status_code=404, detail="更新对象不存在")

    # 获取相关新闻推荐（同分类下，按浏览量和发布时间排序，带缓存）
    related_news = await news_cache.get_related_news(db, news_detail['id'], news_detail['categoryId'])

    return success_response(
        message="success",
        data={
            "id": news_detail['id'],
            "title": news_detail['title'],
            "content": news_detail['content'],
            "image": news_detail['image'],
            "author": news_detail['author'],
            "publishTime": news_detail['publishTime'],
            "categoryId": news_detail['categoryId'],
            "views": news_detail['views'],
            "relatedNews": related_news
        }
    )
