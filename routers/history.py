"""
浏览历史模块路由

提供浏览历史相关的 API 接口，记录用户浏览过的新闻。
使用 Token 进行身份验证，确保只有登录用户才能添加浏览记录。
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from models.users import User
from schemas.history import AddHistoryRequest, HistoryResponse
from crud import history
from utils.auth import get_current_user
from utils.response import success_response

# ==================== 路由器配置 ====================
router = APIRouter(prefix="/api/history", tags=["history"])

# ==================== 添加浏览记录 ====================
@router.post("/add")
async def add_history(
    data: AddHistoryRequest,  # 请求体参数，包含新闻ID
    user: User = Depends(get_current_user),  # 依赖注入：当前登录用户
    db: AsyncSession = Depends(get_db)  # 依赖注入：数据库会话
):
    """
    添加浏览历史记录
    
    处理流程：
    1. 验证用户身份（通过 Token）
    2. 调用 CRUD 层添加或更新浏览记录
    3. 返回浏览记录信息
    
    Args:
        data: 请求数据（包含新闻ID）
        user: 当前登录用户对象
        db: 数据库会话对象
    
    Returns:
        JSONResponse: 包含浏览记录的成功响应
    """
    # 调用 CRUD 层添加或更新浏览记录
    history_record = await history.add_history(
        db=db,
        user_id=user.id,
        news_id=data.news_id
    )
    
    # 返回标准化响应
    return success_response(
        message="添加成功",
        data=HistoryResponse.model_validate(history_record)
    )


@router.get("/list")
async def get_history_list(
    page: int = Query(1, ge=1, description="页码，默认为1"),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize", description="每页条数，默认为10，最大值为100"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取浏览历史列表
    
    处理流程：
    1. 验证用户身份（通过 Token）
    2. 调用 CRUD 层获取分页的浏览历史列表
    3. 构建响应数据，包含新闻信息和浏览时间
    4. 返回标准化响应
    
    Args:
        page: 页码，从1开始
        page_size: 每页显示数量
        user: 当前登录用户对象
        db: 数据库会话对象
    
    Returns:
        JSONResponse: 包含浏览历史列表的成功响应
    """
    # 调用 CRUD 层获取浏览历史列表
    rows, total = await history.get_history_list(
        db=db,
        user_id=user.id,
        page=page,
        page_size=page_size
    )
    
    # 构建新闻列表数据
    history_list = [{
        "id": news.id,
        "title": news.title,
        "description": news.description,
        "image": news.image,
        "author": news.author,
        "categoryId": news.category_id,
        "views": news.views,
        "publishTime": news.publish_time.strftime("%Y-%m-%d %H:%M:%S") if news.publish_time else None,
        "viewTime": view_time.strftime("%Y-%m-%d %H:%M:%S") if view_time else None,
    } for news, view_time in rows]
    
    # 判断是否还有更多数据
    has_more = total > page * page_size
    
    # 构建响应数据
    from schemas.history import HistoryListResponse
    data = HistoryListResponse(
        list=history_list,
        total=total,
        has_more=has_more
    )
    
    return success_response(
        message="success",
        data=data
    )


# ==================== 删除单条浏览记录 ====================
@router.delete("/delete/{history_id}")
async def delete_history(
    history_id: int,  # 路径参数：历史记录ID
    user: User = Depends(get_current_user),  # 依赖注入：当前登录用户
    db: AsyncSession = Depends(get_db)  # 依赖注入：数据库会话
):
    """
    删除单条浏览历史记录
    
    处理流程：
    1. 验证用户身份（通过 Token）
    2. 调用 CRUD 层删除指定的浏览记录
    3. 验证记录是否存在且属于当前用户
    4. 返回删除结果
    
    Args:
        history_id: 历史记录ID（路径参数）
        user: 当前登录用户对象
        db: 数据库会话对象
    
    Returns:
        JSONResponse: 删除成功的响应
    
    Raises:
        HTTPException: 当记录不存在或不属于该用户时抛出404错误
    """
    from fastapi import HTTPException
    from starlette import status
    
    # 调用 CRUD 层删除浏览记录
    success = await history.delete_history(
        db=db,
        user_id=user.id,
        history_id=history_id
    )
    
    # 调试信息：打印删除结果
    # print(f"删除记录 ID={history_id}, user_id={user.id}, 结果={success}")
    
    # 如果删除失败（记录不存在或不属于该用户），返回404错误
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="浏览记录不存在"
        )
    
    # 返回成功响应
    return success_response(
        message="删除成功",
        data=None
    )


# ==================== 清空浏览历史记录 ====================
@router.delete("/clear")
async def clear_history(
    user: User = Depends(get_current_user),  # 依赖注入：当前登录用户
    db: AsyncSession = Depends(get_db)  # 依赖注入：数据库会话
):
    """
    清空当前用户的所有浏览历史记录
    
    处理流程：
    1. 验证用户身份（通过 Token）
    2. 调用 CRUD 层清空该用户的所有浏览记录
    3. 返回清空结果
    
    Args:
        user: 当前登录用户对象
        db: 数据库会话对象
    
    Returns:
        JSONResponse: 清空成功的响应
    """
    # 调用 CRUD 层清空浏览记录
    count = await history.clear_history(
        db=db,
        user_id=user.id
    )
    
    # 返回成功响应
    return success_response(
        message="清空成功",
        data=None
    )