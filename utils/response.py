"""
统一响应工具模块

提供标准化的 API 响应格式，确保所有接口返回一致的数据结构。
使用 jsonable_encoder 将 Pydantic 模型、ORM 对象等转换为 JSON 兼容格式。
"""
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def success_response(message: str, data=None):
    """
    构建成功响应
    
    统一的响应格式：
    {
        "code": 200,
        "message": "操作成功",
        "data": { ... }
    }
    
    Args:
        message: 响应消息
        data: 响应数据（可以是 Pydantic 模型、字典、列表等）
    
    Returns:
        JSONResponse: 标准化后的 JSON 响应对象
    """
    content = {
        "code": 200,
        "message": message,
        "data": data
    }
    # 使用 jsonable_encoder 将 FastAPI、Pydantic、ORM 对象转换为 JSON 兼容格式
    # 这样可以正确处理 datetime、UUID 等特殊类型
    return JSONResponse(content=jsonable_encoder(content))
