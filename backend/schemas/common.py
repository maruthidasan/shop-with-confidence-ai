from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    success: bool = True
    message: str
    request_id: str | None = Field(default=None, alias="requestId")

    model_config = {"populate_by_name": True}


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: str = Field(alias="errorCode")
    request_id: str | None = Field(default=None, alias="requestId")

    model_config = {"populate_by_name": True}
