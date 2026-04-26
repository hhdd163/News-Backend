"""
用户模块路由

提供用户注册、登录、信息查询、信息修改、密码修改等 API 接口。
使用 Token 进行身份验证，保护需要认证的路由。
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest
from crud import users
from config.db_config import get_db
from utils.response import success_response
from utils.auth import get_current_user

# ==================== 路由器配置 ====================
router = APIRouter(prefix="/api/user", tags=["users"])

# ==================== 用户注册 ====================
@router.post("/register")
async def register(
    user_data: UserRequest,  # 请求体参数，包含用户名和密码
    db: AsyncSession = Depends(get_db)  # 依赖注入数据库会话
):
    """
    用户注册接口
    
    处理流程：
    1. 验证用户名是否已存在
    2. 对密码进行加密处理
    3. 创建新用户记录
    4. 生成认证 Token
    5. 返回 Token 和用户信息
    
    Args:
        user_data: 用户注册数据（用户名、密码）
        db: 数据库会话对象
    
    Returns:
        JSONResponse: 包含 Token 和用户信息的成功响应
    """
    # 检查用户名是否已存在（当前代码中此检查被注释掉了）
    # existing_user = await users.get_user_by_username(db, user_data.username)
    # if existing_user:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    
    # 创建新用户（密码会在 CRUD 层自动加密）
    new_user = await users.create_user(db, user_data)
    # 生成认证 Token（有效期7天）
    token = await users.create_token(db, new_user.id)
    
    # 构建响应数据：使用 Pydantic 模型进行数据验证和序列化
    response_data = UserAuthResponse(
        token=token,
        userInfo=UserInfoResponse.model_validate(new_user)
    )
    # 返回标准化响应
    return success_response(message="注册成功", data=response_data)

# ==================== 用户登录 ====================
@router.post("/login")
async def login(
    user_data: UserRequest,  # 请求体参数，包含用户名和密码
    db: AsyncSession = Depends(get_db)  # 依赖注入数据库会话
):
    """
    用户登录接口
    
    处理流程：
    1. 验证用户名是否存在
    2. 验证密码是否正确（使用 bcrypt 比对）
    3. 生成认证 Token
    4. 返回 Token 和用户信息
    
    Args:
        user_data: 用户登录数据（用户名、密码）
        db: 数据库会话对象
    
    Returns:
        JSONResponse: 包含 Token 和用户信息的成功响应
    
    Raises:
        HTTPException: 当用户名或密码错误时抛出401错误
    """
    # 验证用户名和密码（在 CRUD 层进行密码比对）
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 生成认证 Token
    token = await users.create_token(db, user.id)
    
    # 构建响应数据
    response_data = UserAuthResponse(
        token=token,
        userInfo=UserInfoResponse.model_validate(user)
    )
    return success_response(message="登录成功", data=response_data)

# ==================== 获取用户信息 ====================
# 通过依赖注入 get_current_user 自动验证 Token 并获取当前用户
@router.get("/info")
async def get_user_info(
    user: User = Depends(get_current_user)  # 依赖注入：自动验证 Token 并返回用户对象
):
    """
    获取当前登录用户的信息
    
    需要认证：请求头中必须携带有效的 Authorization Token
    
    Args:
        user: 通过 Token 验证后的当前用户对象
    
    Returns:
        JSONResponse: 包含用户信息的成功响应
    """
    return success_response(
        message="获取用户信息成功",
        data=UserInfoResponse.model_validate(user)
    )

# ==================== 修改用户信息 ====================
# 需要认证：验证 Token -> 接收更新数据 -> 更新数据库 -> 返回结果
@router.put("/update")
async def update_user_info(
    user_data: UserUpdateRequest,  # 请求体参数，包含要更新的字段
    user: User = Depends(get_current_user),  # 依赖注入：当前登录用户
    db: AsyncSession = Depends(get_db)  # 依赖注入：数据库会话
):
    """
    修改用户信息接口
    
    支持更新昵称、头像、性别、个人简介、手机号等字段。
    只更新提供的字段，未提供的字段保持不变。
    
    Args:
        user_data: 用户更新数据（部分字段可选）
        user: 当前登录用户对象
        db: 数据库会话对象
    
    Returns:
        JSONResponse: 包含更新后用户信息的成功响应
    """
    # 调用 CRUD 层更新用户信息
    user = await users.update_user_info(db, user.username, user_data)
    return success_response(
        message="更新用户信息成功",
        data=UserInfoResponse.model_validate(user)
    )

# ==================== 修改密码 ====================
@router.put("/password")
async def update_password(
    password_data: UserChangePasswordRequest,  # 请求体参数，包含旧密码和新密码
    user: User = Depends(get_current_user),  # 依赖注入：当前登录用户
    db: AsyncSession = Depends(get_db)  # 依赖注入：数据库会话
):
    """
    修改用户密码接口
    
    处理流程：
    1. 验证旧密码是否正确
    2. 对新密码进行加密
    3. 更新数据库中的密码
    
    Args:
        password_data: 密码修改数据（旧密码、新密码）
        user: 当前登录用户对象
        db: 数据库会话对象
    
    Returns:
        JSONResponse: 成功响应
    
    Raises:
        HTTPException: 当密码修改失败时抛出500错误
    """
    # 调用 CRUD 层修改密码（会先验证旧密码）
    res_change_pwd = await users.update_password(
        db,
        user,
        password_data.old_password,
        password_data.new_password
    )
    if not res_change_pwd:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码失败,请稍后再试"
        )
    return success_response(message="修改密码成功")