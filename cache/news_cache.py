"""
新闻缓存策略模块

定义新闻相关数据的缓存键命名规则和缓存操作方法。
包括新闻分类、新闻列表、新闻详情、相关推荐的缓存读写逻辑。
"""
from typing import Any, Optional

from config.cache_config import get_json_cache, set_cache, redis_client

# ==================== 缓存键常量定义 ====================
CATEGORIES_KEY = "news:categories"  # 新闻分类缓存键
NEWS_LIST_PREFIX = "news:list:"  # 新闻列表缓存键前缀
NEWS_DETAIL_PREFIX = "news:detail:"  # 新闻详情缓存键前缀
RELATED_NEWS_PREFIX = "news:related:"  # 相关新闻缓存键前缀
NEWS_VIEWS_PREFIX = "news:views:"  # 新闻浏览量计数器前缀

# ==================== 新闻分类缓存操作 ====================
# 获取新闻分类缓存
async def get_cached_categories():
    """
    从 Redis 获取新闻分类缓存
    
    Returns:
        list: 分类列表，缓存不存在返回 None
    """
    return await get_json_cache(CATEGORIES_KEY)

# 写入新闻分类缓存
# 分类配置 7200秒（2小时）；列表: 600秒；详情: 1800秒；验证码:120秒
# 数据越稳定，缓存越持久。避免所有key同时过期引起缓存雪崩
async def set_cached_categories(data: list[dict[str, Any]], expire: int = 7200):
    """
    将新闻分类数据写入 Redis 缓存
    
    Args:
        data: 分类数据列表
        expire: 过期时间（秒），默认 7200 秒（2小时）
    
    Returns:
        bool: 设置成功返回 True
    """
    return await set_cache(CATEGORIES_KEY, data, expire)

# ==================== 新闻列表缓存操作 ====================
# 写入缓存-新闻列表
# Key 格式: news:list:{category_id}:{page}:{size}
async def set_cached_news_list(
    category_id: Optional[int],
    page: int,
    size: int,
    news_list: list[dict[str, Any]],
    expire: int = 1800
):
    """
    将新闻列表数据写入 Redis 缓存
    
    Args:
        category_id: 分类ID（可为 None，表示全部）
        page: 页码
        size: 每页数量
        news_list: 新闻列表数据
        expire: 过期时间（秒），默认 1800 秒（30分钟）
    
    Returns:
        bool: 设置成功返回 True
    """
    # 构建缓存键：news:list:{category_id}:{page}:{size}
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await set_cache(key, news_list, expire)

# 读取缓存-新闻列表
async def get_cached_news_list(category_id: Optional[int], page: int, size: int):
    """
    从 Redis 获取新闻列表缓存
    
    Args:
        category_id: 分类ID（可为 None，表示全部）
        page: 页码
        size: 每页数量
    
    Returns:
        list: 新闻列表数据，缓存不存在返回 None
    """
    # 构建缓存键：news:list:{category_id}:{page}:{size}
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await get_json_cache(key)


# ==================== 新闻详情缓存操作 ====================
async def get_cached_news_detail(news_id: int):
    """
    从 Redis 获取新闻详情缓存
    
    Args:
        news_id: 新闻ID
    
    Returns:
        dict: 新闻详情数据（不包含 views 字段），缓存不存在返回 None
    """
    return await get_json_cache(f"{NEWS_DETAIL_PREFIX}{news_id}")


async def set_cached_news_detail(news_id: int, news_data: dict[str, Any], expire: int = 1800):
    """
    将新闻详情数据写入 Redis 缓存
    
    Args:
        news_id: 新闻ID
        news_data: 新闻数据（不应包含 views 字段，因为需要实时更新）
        expire: 过期时间（秒），默认 1800 秒（30分钟）
    
    Returns:
        bool: 设置成功返回 True
    """
    return await set_cache(f"{NEWS_DETAIL_PREFIX}{news_id}", news_data, expire)


async def delete_cached_news_detail(news_id: int):
    """
    删除新闻详情缓存（更新新闻内容时调用）
    
    Args:
        news_id: 新闻ID
    
    Returns:
        bool: 删除成功返回 True
    """
    try:
        await redis_client.delete(f"{NEWS_DETAIL_PREFIX}{news_id}")
        return True
    except Exception as e:
        print(f"删除新闻详情缓存失败: {e}")
        return False


# ==================== 相关新闻缓存操作 ====================
async def get_cached_related_news(news_id: int):
    """
    从 Redis 获取相关新闻缓存
    
    Args:
        news_id: 新闻ID
    
    Returns:
        list: 相关新闻列表，缓存不存在返回 None
    """
    return await get_json_cache(f"{RELATED_NEWS_PREFIX}{news_id}")


async def set_cached_related_news(news_id: int, related_list: list[dict[str, Any]], expire: int = 900):
    """
    将相关新闻数据写入 Redis 缓存
    
    Args:
        news_id: 新闻ID
        related_list: 相关新闻列表
        expire: 过期时间（秒），默认 900 秒（15分钟）
    
    Returns:
        bool: 设置成功返回 True
    """
    return await set_cache(f"{RELATED_NEWS_PREFIX}{news_id}", related_list, expire)


async def delete_cached_related_news(news_id: int):
    """
    删除相关新闻缓存（更新新闻时调用）
    
    Args:
        news_id: 新闻ID
    
    Returns:
        bool: 删除成功返回 True
    """
    try:
        await redis_client.delete(f"{RELATED_NEWS_PREFIX}{news_id}")
        return True
    except Exception as e:
        print(f"删除相关新闻缓存失败: {e}")
        return False


# ==================== 新闻浏览量计数器（第三阶段） ====================
async def increment_news_views_cache(news_id: int):
    """
    使用 Redis 计数器增加新闻浏览量（高并发优化）
    
    Args:
        news_id: 新闻ID
    
    Returns:
        int: 增加后的浏览量
    """
    try:
        key = f"{NEWS_VIEWS_PREFIX}{news_id}"
        # Redis 原子递增操作
        new_count = await redis_client.incr(key)
        # 设置过期时间为 24 小时（防止内存泄漏）
        await redis_client.expire(key, 86400)
        return new_count
    except Exception as e:
        print(f"Redis 浏览量计数失败: {e}")
        return 0


async def get_news_views_from_cache(news_id: int) -> int:
    """
    从 Redis 获取新闻浏览量增量
    
    Args:
        news_id: 新闻ID
    
    Returns:
        int: 浏览量增量，不存在返回 0
    """
    try:
        key = f"{NEWS_VIEWS_PREFIX}{news_id}"
        value = await redis_client.get(key)
        return int(value) if value else 0
    except Exception as e:
        print(f"获取 Redis 浏览量失败: {e}")
        return 0


async def delete_news_views_cache(news_id: int):
    """
    删除新闻浏览量缓存（同步到数据库后清除）
    
    Args:
        news_id: 新闻ID
    """
    try:
        await redis_client.delete(f"{NEWS_VIEWS_PREFIX}{news_id}")
    except Exception as e:
        print(f"删除浏览量缓存失败: {e}")


async def get_all_news_views_keys() -> list[str]:
    """
    获取所有有浏览量增量的新闻ID
    
    Returns:
        list: 新闻ID列表
    """
    try:
        # 使用 SCAN 命令遍历所有匹配的键（避免使用 KEYS 阻塞 Redis）
        keys = []
        async for key in redis_client.scan_iter(f"{NEWS_VIEWS_PREFIX}*"):
            keys.append(key.decode() if isinstance(key, bytes) else key)
        return keys
    except Exception as e:
        print(f"获取浏览量键列表失败: {e}")
        return []