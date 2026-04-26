"""
身份认证工具模块

提供基于 Token 的身份验证功能。
通过解析请求头中的 Authorization Token，验证用户身份并返回用户对象。
用于需要认证的路由的依赖注入。
"""
from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_config import get_db
from crud import users


# ==================== 获取当前用户（身份验证） ====================
async def get_current_user(
    authorization: str = Header(..., alias="Authorization"),  # 从请求头获取 Token
    db: AsyncSession = Depends(get_db)  # 依赖注入数据库会话
):
    """
    获取当前登录用户的依赖注入函数
    
    工作流程：
    1. 从请求头中提取 Token（格式：Bearer <token>）
    2. 查询数据库验证 Token 是否有效且未过期
    3. 返回对应的用户对象
    
    使用方式：
        @router.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            # 只有携带有效 Token 的请求才能访问
            pass
    
    Args:
        authorization: 请求头中的 Authorization 字段，格式为 "Bearer <token>"
        db: 数据库会话对象
    
    Returns:
        User: 当前登录的用户对象
    
    Raises:
        HTTPException: 当 Token 无效或已过期时抛出401错误
    """
    # 从 "Bearer <token>" 格式中提取纯 Token 值
    # 方式一：token = authorization.split(" ")[1]
    token = authorization.replace("Bearer ", "")
    
    # 根据 Token 查询用户（同时验证 Token 是否过期）
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌或已经过期的令牌"
        )
    
    # 用户信息缓存优化：
    # 1. 数据库查询是必须的（用于验证 Token）
    # 2. 查询后将用户信息写入缓存，供后续请求使用
    # 3. 注意：这里不读取缓存，因为每次都需要从数据库验证 Token
    from cache.user_cache import set_cached_user_info
    await set_cached_user_info(user.id, {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "gender": user.gender,
        "bio": user.bio,
        "phone": user.phone,
    })
    
    return user