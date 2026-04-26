"""
密码安全工具模块

使用 bcrypt 算法进行密码加密和验证。
bcrpyt 是一种安全的哈希算法，自动加盐，防止彩虹表攻击。
"""
from passlib.context import CryptContext

# 创建密码上下文，配置使用 bcrypt 算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==================== 密码加密 ====================
def get_hash_password(password: str):
    """
    对明文密码进行加密
    
    Args:
        password: 明文密码
    
    Returns:
        str: 加密后的密码哈希值（包含盐值）
    """
    return pwd_context.hash(password)

# ==================== 密码验证 ====================
def verify_password(plain_password, hashed_password):
    """
    验证明文密码是否与哈希值匹配
    
    Args:
        plain_password: 明文密码
        hashed_password: 加密后的密码哈希值
    
    Returns:
        bool: 密码匹配返回 True，不匹配返回 False
    """
    return pwd_context.verify(plain_password, hashed_password)