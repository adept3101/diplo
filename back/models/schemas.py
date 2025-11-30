from pydantic import BaseModel, Field
# from datetime import datetime


class UserSchema(BaseModel):
    login: str = Field(max_length=32, pattern=r"^[a-zA-Z]+$")
    password: str = Field(max_length=32)
