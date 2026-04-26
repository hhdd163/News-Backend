from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

# 配置 Pydantic 使用本地时间处理 datetime

from schemas.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(...,alias="isFavorite")


class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")

# 规划两个类: 一个是新闻模型类 + 收藏模型类
class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: int = Field(alias="favoriteId")
    favorite_time: datetime = Field(alias="favoriteTime")
    model_config = ConfigDict(
        populate_by_name=True,  # alias / 字段名兼容
        from_attributes=True    # 允许从 ORM 对象属性中取值
    )



# 收藏列表接口响应模型类
class FavoriteListResponse(BaseModel):
    list: list[FavoriteNewsItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore")
    model_config = ConfigDict(
        populate_by_name=True,  # alias / 字段名兼容
        from_attributes=True    # 允许从 ORM 对象属性中取值
    )