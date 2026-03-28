from typing import Any

from pydantic import BaseModel


class BaseResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any = None


def success_response(data: Any = None, message: str = "success") -> BaseResponse:
    return BaseResponse(code=200, message=message, data=data)

