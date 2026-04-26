# 🚀 快速开始指南

## 前置条件

确保以下软件已安装：
- [Python 3.10+](https://www.python.org/downloads/)
- [MySQL 8.0+](https://dev.mysql.com/downloads/mysql/)
- [Redis 7.0+](https://redis.io/download/)

## 5 分钟快速启动

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

创建数据库：
```sql
CREATE DATABASE news_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

修改 `config/db_config.py`：
```python
ASYNC_DATABASE_URL = "mysql+aiomysql://root:你的密码@localhost:3306/news_app?charset=utf8mb4"
```

### 5. 启动 Redis

```bash
# Windows
redis-server

# Linux/Mac
redis-server --daemonize yes
```

### 6. 启动服务

```bash
uvicorn main:app --reload
```

访问 http://localhost:8000/docs 查看 API 文档。

## 🧪 快速测试

### 1. 注册用户

```bash
curl -X POST http://localhost:8000/api/user/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "123456"}'
```

### 2. 登录获取 Token

```bash
curl -X POST http://localhost:8000/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "123456"}'
```

保存返回的 token，用于后续请求。

### 3. 获取新闻分类

```bash
curl http://localhost:8000/api/news/categories
```

## 📚 下一步

- 查看完整的 [README.md](README.md)
- 了解 [缓存策略](README.md#-缓存策略)
- 阅读 [API 文档](http://localhost:8000/docs)

## ❓ 遇到问题？

查看 [常见问题](README.md#-常见问题) 或提交 [Issue](https://github.com/your-username/FastAPI-News-Backend/issues)
