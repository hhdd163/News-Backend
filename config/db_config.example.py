# ==================== 数据库配置示例 ====================
# 复制此文件为 db_config.py 并修改为实际配置

# 异步数据库连接 URL 格式
# mysql+aiomysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4
ASYNC_DATABASE_URL = "mysql+aiomysql://root:your_password@localhost:3306/news_app?charset=utf8mb4"

# 注意：
# 1. 请将 root:your_password 替换为实际的数据库用户名和密码
# 2. 请确保 news_app 数据库已创建
# 3. 生产环境请勿将真实的数据库密码提交到 Git
