from pydantic import BaseModel, EmailStr, Field


class BotSchema(BaseModel):
    bot_token: str = Field(...)
    userID: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "bot_token": "token_from_botfather",
                "userID": 1
            }
        }
