"""
浏览历史数据模型

定义用户浏览新闻的历史记录表，追踪用户的阅读行为。
用于实现“最近浏览”、“阅读历史”等功能。
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


# ==================== 浏览历史模型 ====================
class History(Base):
    """
    浏览历史表 ORM 模型
    
    映射到数据库表 history，记录用户浏览过的新闻
    通过 user_id 和 news_id 建立用户与新闻的关联关系
    使用唯一约束保证同一用户的同一条新闻只保留最新的浏览记录
    """
    __tablename__ = 'history'  # 数据库表名

    # ==================== 索引和约束配置 ====================
    # UniqueConstraint: 唯一约束，同一用户对同一条新闻只保留一条记录
    # Index: 普通索引，优化查询性能
    __table_args__ = (
        # 唯一约束：同一用户不能重复记录同一条新闻的浏览历史
        UniqueConstraint('user_id', 'news_id', name='user_news_unique'),
        # 用户ID索引：优化按用户查询浏览历史
        Index('fk_favorite_user_idx', 'user_id'),
        # 新闻ID索引：优化按新闻查询浏览者
        Index('fk_favorite_news_idx', 'news_id'),
    )

    # 历史记录ID：主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="浏览历史ID")
    # 用户ID：外键，关联到 user 表，不能为空
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), nullable=False, comment="用户ID")
    # 新闻ID：外键，关联到 news 表，不能为空
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey(News.id), nullable=False, comment="新闻ID")
    # 浏览时间：默认为当前本地时间，不能为空
    view_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, comment="浏览时间")

    def __repr__(self):
        """字符串表示，显示历史记录ID、用户ID、新闻ID和浏览时间"""
        return f"<History(id={self.id}, user_id={self.user_id}, news_id={self.news_id}, view_time={self.view_time})>"