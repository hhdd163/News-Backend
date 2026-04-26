"""
收藏功能数据模型

定义用户收藏新闻的关系表，实现用户与新闻的多对多关系。
每个用户可以收藏多条新闻，每条新闻可以被多个用户收藏。
"""
from datetime import datetime
from sqlalchemy import UniqueConstraint, Index, Integer, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from models.news import News
from models.users import User


# ==================== 基础模型类 ====================
class Base(DeclarativeBase):
    """ORM 基础模型类"""
    pass


# ==================== 收藏关系模型 ====================
class Favorite(Base):
    """
    收藏表 ORM 模型
    
    映射到数据库表 favorite，记录用户收藏的新闻
    通过 user_id 和 news_id 建立用户与新闻的关联关系
    使用唯一约束保证同一用户不能重复收藏同一条新闻
    """
    __tablename__ = 'favorite'  # 数据库表名

    # ==================== 索引和约束配置 ====================
    # UniqueConstraint: 唯一约束，防止重复收藏
    # Index: 普通索引，优化查询性能
    __table_args__ = (
        # 唯一约束：同一用户不能重复收藏同一条新闻
        UniqueConstraint('user_id', 'news_id', name='user_news_unique'),
        # 用户ID索引：优化按用户查询收藏列表
        Index('fk_favorite_user_idx', 'user_id'),
        # 新闻ID索引：优化按新闻查询收藏者
        Index('fk_favorite_news_idx', 'news_id'),
    )

    # 收藏ID：主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="收藏ID")
    # 用户ID：外键，关联到 user 表，不能为空
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), nullable=False, comment="用户ID")
    # 新闻ID：外键，关联到 news 表，不能为空
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey(News.id), nullable=False, comment="新闻ID")
    # 收藏时间：默认为当前本地时间，不能为空
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, comment="创建时间")

    def __repr__(self):
        """字符串表示，显示收藏ID、用户ID、新闻ID和收藏时间"""
        return f"<Favorite(id={self.id}, user_id={self.user_id}, news_id={self.news_id}, created_at={self.created_at})>"