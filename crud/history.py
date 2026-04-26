"""
浏览历史数据操作层（CRUD）

封装浏览历史相关的数据库操作，包括添加/更新浏览记录、获取历史列表等。
所有函数均为异步函数，使用 SQLAlchemy 异步会话进行操作。
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


# ==================== 添加或更新浏览记录 ====================
async def add_history(
    db: AsyncSession,
    user_id: int,
    news_id: int
):
    """
    添加或更新浏览历史记录
    
    处理流程：
    1. 查询是否已存在该用户对该新闻的浏览记录
    2. 如果存在，更新浏览时间为当前时间
    3. 如果不存在，创建新的浏览记录
    
    Args:
        db: 数据库会话对象
        user_id: 用户ID
        news_id: 新闻ID
    
    Returns:
        History: 浏览记录对象（新增或更新后的）
    """
    # 查询是否已存在浏览记录
    stmt = select(History).where(
        History.user_id == user_id,
        History.news_id == news_id
    )
    result = await db.execute(stmt)
    existing_history = result.scalar_one_or_none()
    
    if existing_history:
        # 如果已经浏览过，更新浏览时间（使用本地时间）
        existing_history.view_time = datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    else:
        # 如果没有浏览记录，创建新记录（使用本地时间）
        new_history = History(
            user_id=user_id,
            news_id=news_id,
            view_time=datetime.now()
        )
        db.add(new_history)
        await db.commit()
        await db.refresh(new_history)
        return new_history


# ==================== 获取浏览历史列表（分页） ====================
async def get_history_list(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 10
):
    """
    获取用户的浏览历史列表（带分页）
    
    使用联表查询（JOIN）获取浏览的新闻信息和浏览时间。
    
    Args:
        db: 数据库会话对象
        user_id: 用户ID
        page: 页码，从1开始
        page_size: 每页数量
    
    Returns:
        tuple: (rows, total)
            - rows: 历史记录列表，每项为 (新闻对象, 浏览时间)
            - total: 历史记录总数
    """
    # 获取历史记录总数
    count_query = select(func.count()).where(History.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 联表查询：获取浏览的新闻信息 + 浏览时间
    # 按浏览时间降序排序，最近浏览的在前
    query = (
        select(
            News,
            History.view_time.label("view_time")  # 浏览时间别名
        )
        .join(History, News.id == History.news_id)  # 联表条件
        .where(History.user_id == user_id)  # 过滤当前用户
        .order_by(History.view_time.desc())  # 按浏览时间降序排序
        .offset(offset)  # 分页偏移
        .limit(page_size)  # 每页数量
    )

    result = await db.execute(query)
    rows = result.all()  # 返回所有结果
    
    # 调试信息：打印用户的历史记录ID
    # if rows:
    #     history_ids = [row[0].id for row in rows]
    #     print(f"[DEBUG] 用户 {user_id} 的历史记录ID列表: {history_ids[:10]}...")
    
    return rows, total


# ==================== 删除单条浏览记录 ====================
async def delete_history(
    db: AsyncSession,
    user_id: int,
    history_id: int
):
    """
    删除指定的浏览历史记录
    
    处理流程：
    1. 查询浏览记录是否存在且属于当前用户
    2. 如果存在，执行删除操作
    3. 返回删除结果
    
    Args:
        db: 数据库会话对象
        user_id: 用户ID（用于验证记录归属）
        history_id: 历史记录ID
    
    Returns:
        bool: 删除成功返回 True，记录不存在或不属于该用户返回 False
    """
    from sqlalchemy import delete
    
    # 删除记录，同时验证用户ID防止越权删除
    stmt = delete(History).where(
        History.news_id == history_id,
        History.user_id == user_id  # 确保只能删除自己的记录
    )
    result = await db.execute(stmt)
    await db.commit()
    
    # 调试信息
    rowcount = result.rowcount

    return (rowcount or 0) > 0


# ==================== 清空浏览历史记录 ====================
async def clear_history(
    db: AsyncSession,
    user_id: int
):
    """
    清空用户的所有浏览历史记录
    
    处理流程：
    1. 删除该用户的所有浏览记录
    2. 返回删除的记录数量
    
    Args:
        db: 数据库会话对象
        user_id: 用户ID
    
    Returns:
        int: 删除的记录数量
    """
    from sqlalchemy import delete
    
    # 删除该用户的所有浏览记录
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    
    # 返回删除的记录数量（rowcount 为 0 时返回 0）
    return result.rowcount or 0