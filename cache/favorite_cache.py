"""
收藏缓存策略模块

定义收藏相关数据的缓存键命名规则和缓存操作方法。
包括收藏状态检查的缓存读写逻辑。
"""
from config.cache_config import get_cache, set_cache, redis_client

# ==================== 缓存键常量定义 ====================
FAVORITE_CHECK_PREFIX = "favorite:check:"  # 收藏状态缓存键前缀


# ==================== 收藏状态缓存操作 ====================
async def get_cached_favorite_status(user_id: int, news_id: int):
    """
    从 Redis 获取收藏状态缓存
    
    Args:
        user_id: 用户ID
        news_id: 新闻ID
    
    Returns:
        str: "1" 表示已收藏，"0" 表示未收藏，缓存不存在返回 None
    """
    return await get_cache(f"{FAVORITE_CHECK_PREFIX}{user_id}:{news_id}")


async def set_cached_favorite_status(user_id: int, news_id: int, is_favorite: bool, expire: int = 300):
    """
    将收藏状态写入 Redis 缓存
    
    Args:
        user_id: 用户ID
        news_id: 新闻ID
        is_favorite: 是否已收藏
        expire: 过期时间（秒），默认 300 秒（5分钟）
    
    Returns:
        bool: 设置成功返回 True
    """
    # 缓存值："1" 表示已收藏，"0" 表示未收藏
    value = "1" if is_favorite else "0"
    return await set_cache(f"{FAVORITE_CHECK_PREFIX}{user_id}:{news_id}", value, expire)


async def delete_cached_favorite_status(user_id: int, news_id: int):
    """
    删除收藏状态缓存（添加/取消收藏时调用）
    
    Args:
        user_id: 用户ID
        news_id: 新闻ID
    
    Returns:
        bool: 删除成功返回 True
    """
    try:
        await redis_client.delete(f"{FAVORITE_CHECK_PREFIX}{user_id}:{news_id}")
        return True
    except Exception as e:
        print(f"删除收藏状态缓存失败: {e}")
        return False
