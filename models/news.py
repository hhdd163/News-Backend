"""
新闻相关数据模型

定义新闻分类和新闻内容的 ORM 模型，映射到数据库表。
使用 SQLAlchemy 2.0 风格的声明式基类和类型注解。
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Index, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped,mapped_column


# ==================== 基础模型类 ====================
class Base(DeclarativeBase):
    """
    ORM 基础模型类
    
    所有模型类继承此类，自动包含 created_at 和 updated_at 字段
    用于记录数据的创建时间和更新时间
    """
    # 创建时间字段：插入数据时自动设置为当前本地时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )
    # 更新时间字段：插入时设置，更新时自动刷新为当前本地时间
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,  # 更新记录时自动修改为当前时间
        comment="更新时间"
    )

# ==================== 新闻分类模型 ====================
class Category(Base):
    """
    新闻分类表 ORM 模型
    
    映射到数据库表 news_category，存储新闻的分类信息
    例如：科技、体育、娱乐、财经等
    """
    __tablename__ = "news_category"  # 数据库表名

    # 分类ID：主键，自增
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True,comment="分类id")
    # 分类名称：唯一约束，不能为空
    name: Mapped[str] = mapped_column(String(50),unique= True,nullable=False,comment="分类名称")
    # 排序字段：用于控制分类显示顺序，默认值为0
    sort_order: Mapped[int] = mapped_column(Integer,default=0,nullable=False,comment="排序")

    def __repr__(self):
        """字符串表示，便于调试和日志输出"""
        return f"<Category(id={self.id},name={self.name},sort_order={self.sort_order})>"

# ==================== 新闻内容模型 ====================
class News(Base):
    """
    新闻内容表 ORM 模型
    
    映射到数据库表 news，存储新闻的详细信息
    包括标题、内容、作者、分类、浏览量等字段
    """
    __tablename__ = "news"  # 数据库表名

    # ==================== 索引配置 ====================
    # 通过 __table_args__ 定义表级约束和索引
    __table_args__ = (
        # 分类ID索引：优化按分类查询新闻的性能
        Index('fk_news_category_idx', 'category_id'),
        # 发布时间索引：优化按时间排序和分页查询
        Index('idx_publish_time', 'publish_time')
    )

    # 新闻ID：主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="新闻ID")
    # 新闻标题：不能为空，最大长度255字符
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="新闻标题")
    # 新闻简介：可选字段，用于列表页展示
    description: Mapped[Optional[str]] = mapped_column(String(500), comment="新闻简介")
    # 新闻内容：文本类型，支持长文本，不能为空
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="新闻内容")
    # 封面图片URL：可选字段，存储图片链接
    image: Mapped[Optional[str]] = mapped_column(String(255), comment="封面图片URL")
    # 作者：可选字段
    author: Mapped[Optional[str]] = mapped_column(String(50), comment="作者")
    # 分类ID：外键，关联到 news_category 表的 id 字段
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('news_category.id'), comment="分类ID")
    # 阅读量：默认值为0，每次查看详情时+1
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="阅读量")
    # 发布时间：默认为当前本地时间
    publish_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="发布时间")

    def __repr__(self):
        """字符串表示，显示新闻ID、标题和浏览量"""
        return f"<News(id={self.id}, title='{self.title}', views={self.views})>"
