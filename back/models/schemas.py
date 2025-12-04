from pydantic import BaseModel, Field
# from datetime import datetime


class UserSchema(BaseModel):
    login: str = Field(max_length=32, pattern=r"^[a-zA-Z](.[a-zA-Z0-9_-]*)$")
    password: str = Field(max_length=32)
