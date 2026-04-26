"""
用户数据操作层（CRUD）

封装用户相关的数据库操作，包括注册、登录、Token管理、信息更新等。
所有函数均为异步函数，使用 SQLAlchemy 异步会话进行操作。
"""
import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from cache.user_cache import get_cached_user_info, set_cached_user_info
from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest
from utils import security

# ==================== 根据用户名查询用户 ====================
async def get_user_by_username(db: AsyncSession, username: str):
    """
    根据用户名查询用户
    
    Args:
        db: 数据库会话对象
        username: 用户名
    
    Returns:
        User: 用户对象，不存在则返回 None
    """
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()

# ==================== 创建用户 ====================
async def create_user(db: AsyncSession, user_data: UserRequest):
    """
    创建新用户
    
    处理流程：
    1. 对密码进行 bcrypt 加密
    2. 创建 User 对象
    3. 添加到数据库并提交
    4. 刷新对象以获取生成的 ID
    
    Args:
        db: 数据库会话对象
        user_data: 用户注册数据（包含用户名和密码）
    
    Returns:
        User: 创建后的用户对象（包含生成的 ID）
    """
    # 密码加密处理（使用 bcrypt）
    hashed_password = security.get_hash_password(user_data.password)
    # 创建用户对象
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.commit()  # 提交事务
    await db.refresh(user)  # 刷新对象，获取自动生成的 ID
    return user
# ==================== 生成/更新 Token ====================
async def create_token(db: AsyncSession, user_id: int):
    """
    为用户生成或更新认证 Token
    
    处理流程：
    1. 生成 UUID Token
    2. 设置过期时间（7天）
    3. 查询用户是否已有 Token
    4. 有则更新，无则创建
    
    Args:
        db: 数据库会话对象
        user_id: 用户ID
    
    Returns:
        str: 生成的 Token 值
    """
    # 生成唯一 Token（UUID v4）
    token = str(uuid.uuid4())
    # 设置过期时间：当前时间 + 7天
    # timedelta(days=7, hours=2, minutes=30, seconds=2) 全量写法
    expires_at = datetime.now() + timedelta(days=7)
    
    # 查询用户是否已有 Token
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()
    
    if user_token:
        # 已有 Token，更新 Token 值和过期时间
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        # 没有 Token，创建新记录
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)
        await db.commit()

    return token

# ==================== 验证用户（登录） ====================
async def authenticate_user(db: AsyncSession, username: str, password: str):
    """
    验证用户凭证（用于登录）
    
    处理流程：
    1. 根据用户名查询用户
    2. 验证密码是否正确（bcrypt 比对）
    
    Args:
        db: 数据库会话对象
        username: 用户名
        password: 明文密码
    
    Returns:
        User: 验证成功返回用户对象，失败返回 None
    """
    user = await get_user_by_username(db, username)
    if not user:
        return None  # 用户不存在
    if not security.verify_password(password, user.password):
        return None  # 密码错误
    return user  # 验证成功

# ==================== 根据 Token 查询用户 ====================
async def get_user_by_token(db: AsyncSession, token: str):
    """
    根据 Token 查询用户（用于身份验证）
    
    处理流程：
    1. 查询 Token 记录
    2. 检查 Token 是否存在且未过期
    3. 根据 user_id 查询用户信息
    
    Args:
        db: 数据库会话对象
        token: Token 值
    
    Returns:
        User: 查询成功返回用户对象，失败返回 None
    """
    # 查询 Token 记录
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()

    # 检查 Token 是否存在且未过期
    if not db_token or db_token.expires_at < datetime.now():
        return None

    # 根据 user_id 查询用户
    query = select(User).where(User.id == db_token.user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

# ==================== 更新用户信息 ====================
async def update_user_info(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    """
    更新用户信息
    
    处理流程：
    1. 构建 UPDATE 语句（只更新提供的字段）
    2. 执行更新并提交
    3. 检查是否成功更新
    4. 返回更新后的用户信息
    
    Args:
        db: 数据库会话对象
        username: 用户名（用于定位用户）
        user_data: 要更新的数据（Pydantic 模型）
    
    Returns:
        User: 更新后的用户对象
    
    Raises:
        HTTPException: 当用户不存在时抛出404错误
    """
    # 构建 UPDATE 语句
    # model_dump(exclude_unset=True, exclude_none=True) 只包含设置的字段，排除 None 值
    query = update(User).where(User.username == username).values(
        **user_data.model_dump(
            exclude_unset=True,  # 排除未设置的字段
            exclude_none=True    # 排除 None 值的字段
        )
    )
    result = await db.execute(query)
    await db.commit()

    # 检查更新是否成功（rowcount 为 0 表示没有匹配的记录）
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取更新后的用户信息
    updated_user = await get_user_by_username(db, username)
    
    # 清除用户信息缓存（下次查询时会重新缓存）
    from cache.user_cache import delete_cached_user_info
    await delete_cached_user_info(updated_user.id)
    
    return updated_user

# ==================== 修改密码 ====================
async def update_password(db: AsyncSession, user: User, old_password: str, new_password: str):
    """
    修改用户密码
    
    处理流程：
    1. 验证旧密码是否正确
    2. 对新密码进行加密
    3. 更新数据库中的密码
    4. 刷新对象以确保会话同步
    
    Args:
        db: 数据库会话对象
        user: 用户对象
        old_password: 旧密码（明文）
        new_password: 新密码（明文）
    
    Returns:
        bool: 修改成功返回 True，失败返回 False
    """
    # 验证旧密码
    if not security.verify_password(old_password, user.password):
        return False
    
    # 加密新密码
    hashed_new_pwd = security.get_hash_password(new_password)
    user.password = hashed_new_pwd
    
    # 将用户对象添加到会话，确保 SQLAlchemy 接管该对象
    # 规避 session 过期或关闭导致的不能提交问题
    db.add(user)
    await db.commit()
    await db.refresh(user)  # 刷新对象，确保数据同步
    
    # 清除用户信息缓存（修改密码后）
    from cache.user_cache import delete_cached_user_info
    await delete_cached_user_info(user.id)
    
    return True
