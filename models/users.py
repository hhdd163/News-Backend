"""
用户相关数据模型

定义用户信息和用户令牌的 ORM 模型，映射到数据库表。
包括用户基本信息、密码（加密存储）、头像、性别等字段。
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Index, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# ==================== 基础模型类 ====================
class Base(DeclarativeBase):
    """ORM 基础模型类，所有用户相关模型继承此类"""
    pass


# ==================== 用户信息模型 ====================
class User(Base):
    """
    用户信息表 ORM 模型
    
    映射到数据库表 user，存储用户的注册信息和个人资料
    包括用户名、密码（加密）、昵称、头像、性别、手机号等
    """
    __tablename__ = 'user'  # 数据库表名

    # ==================== 索引配置 ====================
    # 为 username 和 phone 字段创建唯一索引，加速查询并保证唯一性
    __table_args__ = (
        Index('username_UNIQUE', 'username'),  # 用户名唯一索引
        Index('phone_UNIQUE', 'phone'),  # 手机号唯一索引
    )

    # 用户ID：主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    # 用户名：唯一约束，不能为空，用于登录
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    # 密码：加密存储（使用 bcrypt），不能为空
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码（加密存储）")
    # 昵称：可选字段，用于显示
    nickname: Mapped[Optional[str]] = mapped_column(String(50), comment="昵称")
    # 头像URL：可选字段，默认使用猫图片作为默认头像
    avatar: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="头像URL",
        default='https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'
    )
    # 性别：枚举类型，可选值为 male/female/unknown，默认为 unknown
    gender: Mapped[Optional[str]] = mapped_column(
        Enum('male', 'female', 'unknown'),
        comment="性别",
        default='unknown'
    )
    # 个人简介：可选字段，最大长度500字符
    bio: Mapped[Optional[str]] = mapped_column(
        String(500),
        comment="个人简介",
        default='这个人很懒，什么都没留下'
    )
    # 手机号：唯一约束，可选字段
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, comment="手机号")
    # 创建时间：默认为当前本地时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    # 更新时间：插入时设置，更新时自动刷新（使用本地时间）
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间"
    )

    def __repr__(self):
        """字符串表示，显示用户ID、用户名和昵称"""
        return f"<User(id={self.id}, username='{self.username}', nickname='{self.nickname}')>"


# ==================== 用户令牌模型 ====================
class UserToken(Base):
    """
    用户令牌表 ORM 模型
    
    映射到数据库表 user_token，存储用户的认证令牌（Token）
    用于实现基于 Token 的身份验证机制，替代传统的 Session
    Token 有过期时间，定期更新以保证安全性
    """
    __tablename__ = 'user_token'  # 数据库表名

    # ==================== 索引配置 ====================
    # 为 token 字段创建唯一索引，加速 Token 查询
    # 为 user_id 创建索引，优化按用户查询 Token 的性能
    __table_args__ = (
        Index('token_UNIQUE', 'token'),  # Token 唯一索引
        Index('fk_user_token_user_idx', 'user_id'),  # 用户ID索引
    )

    # 令牌ID：主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="令牌ID")
    # 用户ID：外键，关联到 user 表的 id 字段，不能为空
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), nullable=False, comment="用户ID")
    # Token值：唯一约束，使用 UUID 生成，不能为空
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, comment="令牌值")
    # 过期时间：Token 的有效期，超过此时间 Token 失效
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="过期时间")
    # 创建时间：默认为当前本地时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")

    def __repr__(self):
        """字符串表示，显示令牌ID、用户ID和Token值"""
        return f"<UserToken(id={self.id}, user_id={self.user_id}, token='{self.token}')>"