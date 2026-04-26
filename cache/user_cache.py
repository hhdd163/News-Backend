"""
用户缓存策略模块

定义用户相关数据的缓存键命名规则和缓存操作方法。
包括用户信息的缓存读写逻辑。
"""
from typing import Any

from config.cache_config import get_json_cache, set_cache, redis_client

# ==================== 缓存键常量定义 ====================
USER_INFO_PREFIX = "user:info:"  # 用户信息缓存键前缀


# ==================== 用户信息缓存操作 ====================
async def get_cached_user_info(user_id: int):
    """
    从 Redis 获取用户信息缓存
    
    Args:
        user_id: 用户ID
    
    Returns:
        dict: 用户信息数据，缓存不存在返回 None
    """
    return await get_json_cache(f"{USER_INFO_PREFIX}{user_id}")


async def set_cached_user_info(user_id: int, user_data: dict[str, Any], expire: int = 3600):
    """
    将用户信息数据写入 Redis 缓存
    
    Args:
        user_id: 用户ID
        user_data: 用户信息数据
        expire: 过期时间（秒），默认 3600 秒（1小时）
    
    Returns:
        bool: 设置成功返回 True
    """
    return await set_cache(f"{USER_INFO_PREFIX}{user_id}", user_data, expire)


async def delete_cached_user_info(user_id: int):
    """
    删除用户信息缓存（更新用户信息或修改密码时调用）
    
    Args:
        user_id: 用户ID
    
    Returns:
        bool: 删除成功返回 True
    """
    try:
        await redis_client.delete(f"{USER_INFO_PREFIX}{user_id}")
        return True
    except Exception as e:
        print(f"删除用户信息缓存失败: {e}")
        return False
