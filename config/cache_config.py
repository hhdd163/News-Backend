"""
Redis 缓存配置模块

配置异步 Redis 连接，提供缓存读写的基础函数。
支持字符串、列表、字典等数据类型的缓存操作。
"""
from typing import Any

import redis.asyncio as redis
import json

# ==================== Redis 连接配置 ====================
REDIS_HOST = "localhost"  # Redis 服务器地址
REDIS_PORT = 6379  # Redis 端口号
REDIS_DB = 0  # Redis 数据库编号（0-15）

# 创建异步 Redis 连接对象
redis_client = redis.Redis(
    host=REDIS_HOST,    # Redis 服务器地址
    port=REDIS_PORT,    # Redis 端口号
    db=REDIS_DB,        # Redis 数据库编号，0-15
    decode_responses=True  # 自动将字节数据解码为字符串
)

# ==================== 缓存读取（字符串） ====================
async def get_cache(key: str):
    """
    从 Redis 获取缓存数据（字符串格式）
    
    Args:
        key: 缓存键名
    
    Returns:
        str: 缓存值，不存在或出错返回 None
    """
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败: {e}")
        return None

# ==================== 缓存读取（JSON 格式） ====================
async def get_json_cache(key: str):
    """
    从 Redis 获取 JSON 格式的缓存数据
    
    适用于列表、字典等复杂数据类型的缓存读取。
    
    Args:
        key: 缓存键名
    
    Returns:
        dict/list: 解析后的数据，不存在或出错返回 None
    """
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)  # 反序列化 JSON 字符串
        return None
    except Exception as e:
        print(f"获取 JSON 缓存失败: {e}")
        return None

# ==================== 设置缓存（支持过期时间） ====================
async def set_cache(key: str, value: Any, expire: int = 3600):
    """
    设置 Redis 缓存（带过期时间）
    
    使用 SETEX 命令，原子性地设置值和过期时间。
    自动处理字典、列表等复杂类型的 JSON 序列化。
    
    Args:
        key: 缓存键名
        value: 缓存值（可以是字符串、字典、列表等）
        expire: 过期时间（秒），默认 3600 秒（1小时）
    
    Returns:
        bool: 设置成功返回 True，失败返回 False
    """
    try:
        # 如果是字典或列表，先序列化为 JSON 字符串
        if isinstance(value, (dict, list)):
            # ensure_ascii=False 保证中文正常显示
            value = json.dumps(value, ensure_ascii=False)
        
        # SETEX 命令：设置值并指定过期时间
        await redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        print(f"设置缓存失败: {e}")
        return False