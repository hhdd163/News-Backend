"""
浏览历史数据验证模型

定义浏览历史相关的请求和响应数据模型。
使用 Pydantic 进行数据验证和序列化。
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

# 配置 Pydantic 使用本地时间处理 datetime


class AddHistoryRequest(BaseModel):
    """
    添加浏览历史请求模型
    
    用于接收前端传来的新闻ID
    """
    news_id: int = Field(..., alias="newsId", description="新闻ID")


class HistoryResponse(BaseModel):
    """
    浏览历史响应模型
    
    返回浏览记录的完整信息
    """
    id: int
    user_id: int = Field(alias="userId")
    news_id: int = Field(alias="newsId")
    view_time: datetime = Field(alias="viewTime")
    
    model_config = ConfigDict(
        from_attributes=True,  # 允许从 ORM 对象属性中取值
        populate_by_name=True  # 支持使用字段名或别名
    )


class HistoryNewsItemResponse(BaseModel):
    """
    浏览历史中的新闻项响应模型
    
    继承 NewsItemBase，添加浏览时间字段
    """
    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: int = Field(alias="categoryId")
    views: int
    publish_time: Optional[datetime] = Field(None, alias="publishTime")
    view_time: datetime = Field(alias="viewTime")  # 浏览时间
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class HistoryListResponse(BaseModel):
    """
    浏览历史列表响应模型
    
    包含新闻列表、总数和是否有更多数据
    """
    list: list[HistoryNewsItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore")
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )