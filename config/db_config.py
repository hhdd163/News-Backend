"""
数据库配置文件

配置异步 MySQL 数据库连接，使用 SQLAlchemy 异步引擎和 aiomysql 驱动。
提供数据库会话工厂和依赖注入函数，供路由层使用。
"""
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

# ==================== 数据库连接配置 ====================
# 异步数据库 URL 格式：mysql+aiomysql://用户名:密码@主机:端口/数据库名?字符集
# 添加 use_unicode=1&charset=utf8mb4 确保中文支持
ASYNC_DATABASE_URL = "mysql+aiomysql://root:Aa123456@localhost:3306/news_app?charset=utf8mb4&use_unicode=1"

# 创建异步数据库引擎
# create_async_engine 是 SQLAlchemy 提供的异步引擎创建函数
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,  # SQL 日志输出，开发环境设为 True 便于调试，生产环境应设为 False
    pool_size=10,  # 连接池大小：保持的持久连接数，根据并发量调整
    max_overflow=20  # 连接池溢出：允许创建的额外连接数，应对突发流量
)

# 创建异步会话工厂
# async_sessionmaker 用于生成数据库会话对象，每个请求使用独立会话
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,  # 绑定到上面创建的异步引擎
    class_=AsyncSession,  # 指定会话类为异步会话
    expire_on_commit=False  # 提交后不自动过期对象属性，避免访问已关闭会话时报错
)

# ==================== 数据库会话依赖注入 ====================
# FastAPI 依赖注入函数，用于在路由中获取数据库会话
# 使用 yield 实现会话的生命周期管理：请求开始时创建，结束时关闭
async def get_db():
    """
    数据库会话依赖注入函数
    
    工作流程：
    1. 创建新的数据库会话
    2. 通过 yield 将会话提供给路由函数
    3. 如果请求成功，提交事务
    4. 如果发生异常，回滚事务
    5. 最后关闭会话，释放连接
    
    Yields:
        AsyncSession: 异步数据库会话对象
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session  # 提供会话给路由函数使用
            await session.commit()  # 请求成功，提交事务
        except Exception:
            await session.rollback()  # 发生异常，回滚事务
            raise
        finally:
            await session.close()  # 无论成功与否，都关闭会话