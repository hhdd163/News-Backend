# 📰 头条新闻后端系统

基于 FastAPI 构建的高性能新闻后端 API，提供用户管理、新闻浏览、收藏和浏览历史等功能。采用异步架构，使用 MySQL 数据库和 Redis 缓存层，实现高并发场景下的快速响应。

## ✨ 主要功能

### 🔐 用户模块
- 用户注册与登录（bcrypt 密码加密）
- Token 认证机制（UUID Token，7天有效期）
- 用户信息查看与修改
- 密码修改

### 📰 新闻模块
- 新闻分类管理
- 新闻列表（分页查询）
- 新闻详情查看
- 相关推荐（按浏览量和时间排序）
- 浏览量统计

### ⭐ 收藏模块
- 添加/取消收藏
- 收藏列表（分页查询）
- 清空所有收藏
- 收藏状态检查

### 📜 浏览历史模块
- 自动记录浏览历史
- 历史列表（分页查询）
- 删除单条记录
- 清空所有历史

## 🚀 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.10+ | 编程语言 |
| **FastAPI** | 0.100+ | Web 框架 |
| **SQLAlchemy** | 2.0+ | 异步 ORM |
| **MySQL** | 8.0+ | 主数据库 |
| **Redis** | 7.0+ | 缓存层 |
| **Pydantic** | 2.0+ | 数据验证 |
| **aiomysql** | 0.2+ | MySQL 异步驱动 |
| **passlib** | 1.7+ | 密码加密 |
| **bcrypt** | 4.0+ | 哈希算法 |

## 📋 项目结构

```
FastAPIProject/
├── cache/              # 缓存策略模块
│   ├── news_cache.py       # 新闻缓存
│   ├── user_cache.py       # 用户缓存
│   └── favorite_cache.py   # 收藏缓存
├── config/             # 配置文件
│   ├── db_config.py        # 数据库配置
│   └── cache_config.py     # Redis 配置
├── crud/               # 数据操作层
│   ├── news.py             # 新闻基础操作
│   ├── news_cache.py       # 新闻缓存操作
│   ├── users.py            # 用户操作
│   ├── favorite.py         # 收藏操作
│   └── history.py          # 历史操作
├── models/             # ORM 模型
│   ├── news.py             # 新闻模型
│   ├── users.py            # 用户模型
│   ├── favorite.py         # 收藏模型
│   └── history.py          # 历史模型
├── routers/            # 路由层
│   ├── news.py             # 新闻路由
│   ├── users.py            # 用户路由
│   ├── favorite.py         # 收藏路由
│   └── history.py          # 历史路由
├── schemas/            # 数据验证模型
│   ├── base.py             # 基础模型
│   ├── users.py            # 用户模型
│   ├── favorite.py         # 收藏模型
│   └── history.py          # 历史模型
├── utils/              # 工具函数
│   ├── auth.py             # 身份认证
│   ├── security.py         # 安全工具
│   ├── response.py         # 响应封装
│   ├── exception.py        # 异常定义
│   └── exception_handlers.py # 异常处理
├── main.py             # 应用入口
├── tasks.py            # 定时任务（浏览量同步）
├── requirements.txt    # 依赖列表
└── .gitignore         # Git 忽略文件
```

## 🔧 环境要求

- Python 3.10 或更高版本
- MySQL 8.0 或更高版本
- Redis 7.0 或更高版本

## 📦 安装与配置

### 1. 克隆项目

```bash
git clone https://github.com/your-username/FastAPI-News-Backend.git
cd FastAPI-News-Backend
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置数据库

修改 `config/db_config.py` 中的数据库连接信息：

```python
ASYNC_DATABASE_URL = "mysql+aiomysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4"
```

### 5. 配置 Redis

修改 `config/cache_config.py` 中的 Redis 连接信息：

```python
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
```

### 6. 初始化数据库

```sql
CREATE DATABASE news_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

启动应用后，SQLAlchemy 会自动创建表结构。

## 🚀 运行项目

### 开发模式

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产模式

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

访问 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📚 API 接口文档

### 用户接口 `/api/user`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/register` | 用户注册 | ❌ |
| POST | `/login` | 用户登录 | ❌ |
| GET | `/info` | 获取用户信息 | ✅ |
| PUT | `/update` | 修改用户信息 | ✅ |
| PUT | `/password` | 修改密码 | ✅ |

### 新闻接口 `/api/news`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/categories` | 获取新闻分类 | ❌ |
| GET | `/list` | 获取新闻列表 | ❌ |
| GET | `/detail` | 获取新闻详情 | ❌ |

### 收藏接口 `/api/favorite`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/check` | 检查收藏状态 | ✅ |
| POST | `/add` | 添加收藏 | ✅ |
| DELETE | `/remove` | 取消收藏 | ✅ |
| GET | `/list` | 获取收藏列表 | ✅ |
| DELETE | `/clear` | 清空收藏 | ✅ |

### 历史接口 `/api/history`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/add` | 添加浏览记录 | ✅ |
| GET | `/list` | 获取历史列表 | ✅ |
| DELETE | `/delete/{id}` | 删除单条记录 | ✅ |
| DELETE | `/clear` | 清空历史 | ✅ |

## 🔑 缓存策略

### 缓存模块

| 模块 | 缓存项 | 过期时间 | 说明 |
|------|--------|---------|------|
| **新闻** | 分类 | 7200秒 | 数据稳定 |
| 新闻 | 列表 | 1800秒 | 分页查询 |
| 新闻 | 详情 | 1800秒 | 排除实时浏览量 |
| 新闻 | 相关推荐 | 900秒 | 推荐结果 |
| **用户** | 用户信息 | 3600秒 | Token验证后缓存 |
| **收藏** | 收藏状态 | 300秒 | 频繁检查 |

### 浏览量同步

- **机制**：Redis 计数器 + 定时任务同步到 MySQL
- **频率**：每 5 分钟同步一次
- **优势**：减少数据库写入压力，提升并发性能

## 📖 使用示例

### 用户注册

```bash
curl -X POST http://localhost:8000/api/user/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "123456"}'
```

### 获取新闻列表

```bash
curl http://localhost:8000/api/news/list?categoryId=1&page=1&pageSize=10
```

### 添加收藏

```bash
curl -X POST http://localhost:8000/api/favorite/add \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"newsId": 1}'
```

## 🛠️ 开发指南

### 添加新模块

1. 在 `models/` 创建 ORM 模型
2. 在 `schemas/` 创建 Pydantic 模型
3. 在 `crud/` 封装数据库操作
4. 在 `routers/` 定义路由
5. 在 `main.py` 注册路由

### 添加缓存

参考 `cache/` 目录下的缓存模块实现：

```python
from cache.news_cache import get_cached_news_detail, set_cached_news_detail

# 获取缓存
cached = await get_cached_news_detail(news_id)
if cached:
    return cached

# 写入缓存
await set_cached_news_detail(news_id, data, expire=1800)
```

## 🧪 测试

### 运行测试（待添加）

```bash
pytest
```

### 性能测试

使用 Locust 或 JMeter 进行压力测试，验证缓存效果。

## 📝 数据库设计

### 主要表结构

- **user**: 用户信息表
- **user_token**: 用户令牌表
- **news**: 新闻表
- **category**: 新闻分类表
- **favorite**: 收藏记录表
- **history**: 浏览历史表

详细设计请参考项目中的 ORM 模型文件。

## 🔒 安全特性

- ✅ bcrypt 密码加密
- ✅ Token 认证机制
- ✅ CORS 跨域配置
- ✅ 全局异常处理
- ✅ 输入数据验证（Pydantic）
- ✅ SQL 注入防护（SQLAlchemy ORM）

## 📊 性能优化

- ✅ 异步架构（async/await）
- ✅ 数据库连接池
- ✅ Redis 多级缓存
- ✅ 浏览量批量更新
- ✅ 索引优化（外键、查询字段）

## 🐛 常见问题

### 1. Redis 连接失败

检查 Redis 服务是否启动：
```bash
redis-cli ping
```

### 2. 数据库连接失败

检查 MySQL 服务和配置：
```bash
mysql -u root -p
```

### 3. 缓存不生效

清除 Redis 缓存：
```bash
redis-cli FLUSHDB
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👨‍ 作者

[Your Name](https://github.com/your-username)

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Redis](https://redis.io/)

---

**⚠️ 注意**: 本项目为学习演示项目，生产环境使用时请：
1. 修改默认密码和密钥
2. 配置 HTTPS
3. 限制 CORS 允许的域名
4. 添加限流和防护机制
5. 定期备份数据库
