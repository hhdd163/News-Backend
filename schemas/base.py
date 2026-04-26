from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

# 配置 Pydantic 使用本地时间处理 datetime
# 这样可以确保从数据库读取的 datetime 对象在序列化时保持为本地时间


class NewsItemBase(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: int = Field(alias="categoryId")
    views: int
    publish_time: Optional[datetime] = Field(None, alias="publishedTime")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )