"""
FastAPI 新闻应用主入口文件

本项目是一个头条新闻后端系统，提供用户管理、新闻浏览、收藏和历史记录等功能。
采用 FastAPI 框架构建，使用异步 SQLAlchemy 操作 MySQL 数据库，Redis 作为缓存层。

主要功能模块：
- 用户模块：注册、登录、信息管理
- 新闻模块：分类、列表、详情、相关推荐
- 收藏模块：添加/取消收藏、收藏列表
- 历史模块：浏览历史记录
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
# 导入各功能模块的路由
from routers import news, users, favorite, history
# 导入 CORS 中间件，用于跨域请求支持
from fastapi.middleware.cors import CORSMiddleware
# 导入全局异常处理器注册函数
from utils.exception_handlers import register_exception_handlers


# ==================== 应用生命周期管理 ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理器（替代已弃用的 @app.on_event）
    
    在应用启动和关闭时执行相应任务：
    - 启动时：初始化定时任务调度器（浏览量同步）
    - 关闭时：清理资源（可选）
    """
    # ==================== 启动时执行 ====================
    import asyncio
    from tasks import start_scheduler
    
    print("=" * 50)
    print("应用启动完成！")
    print("定时任务调度器已启动（浏览量同步）")
    print("=" * 50)
    
    # 在后台启动定时任务（不阻塞应用启动）
    scheduler_task = asyncio.create_task(start_scheduler())
    
    yield  # 应用运行期间
    
    # ==================== 关闭时执行 ====================
    print("=" * 50)
    print("应用关闭中...")
    scheduler_task.cancel()  # 取消定时任务
    print("定时任务调度器已停止")
    print("=" * 50)


# 创建 FastAPI 应用实例（使用 lifespan 参数）
app = FastAPI(
    title="头条新闻API",
    description="提供新闻浏览、用户管理、收藏等功能的后端API",
    version="1.0.0",
    lifespan=lifespan  # 使用新的生命周期管理器
)

# 注册全局异常处理器，统一处理各类异常并返回标准化响应
register_exception_handlers(app)

# 配置 CORS（跨域资源共享）中间件
# 允许前端跨域访问 API，开发环境下设置为 "*" 允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许访问的源域名列表，生产环境应指定具体域名
    allow_credentials=True, # 允许携带 Cookie 和认证信息
    allow_methods=["*"],  # 允许的 HTTP 方法（GET, POST, PUT, DELETE等）
    allow_headers=["*"],  # 允许的所有请求头
)


# 根路径测试接口
@app.get("/")
async def root():
    """API 根路径，用于测试服务是否正常运行"""
    return {"message": "Hello World"}


# 带参数的测试接口
@app.get("/hello/{name}")
async def say_hello(name: str):
    """测试接口，演示路径参数使用"""
    return {"message": f"Hello {name}"}

# ==================== 路由注册 ====================
# 将各功能模块的路由挂载到应用中
# 每个路由模块都有自己的 prefix 和 tags，在 Swagger UI 中会自动分组显示
app.include_router(news.router)      # 新闻相关接口 /api/news
app.include_router(users.router)     # 用户相关接口 /api/user
app.include_router(favorite.router)  # 收藏相关接口 /api/favorite
app.include_router(history.router)   # 历史相关接口 /api/history
