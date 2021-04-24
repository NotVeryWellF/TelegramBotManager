from pydantic import BaseModel, Field


class SimpleResponse(BaseModel):
    data: str = Field(...)
    code: int = 200
    message: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "data": "Text data",
                "code": 200,
                "message": "Some message for you"
            }
        }


class TokenResponse(BaseModel):
    data: dict = Field(...)
    code: int = 200
    message: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "data": {
                            "access_token": "your authorization token"
                        },
                "code": 200,
                "message": "Some message for you"
            }
        }


class BotListResponse(BaseModel):
    data: list = Field(...)
    code: int = 200
    message: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "data": [
                            {
                                "id": "bot id",
                                "bot_token": "bot token",
                                "userID": "Your user id"
                            },
                            {
                                "id": "another bot id",
                                "bot_token": "bot token",
                                "userID": "Your user id"
                            }
                        ],
                "code": 200,
                "message": "Some message for you"
            }
        }

