from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class APIClientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    user_id: int


class APIClientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    is_active: bool | None = None


class APIClientResponse(BaseModel):
    id: int
    name: str
    client_key: str
    user_id: int
    is_active: bool
    last_used_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class APIClientCreateResponse(BaseModel):
    id: int
    name: str
    client_key: str
    client_secret: str
    user_id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class APIClientAuthRequest(BaseModel):
    client_key: str = Field(min_length=2, max_length=100)
    client_secret: str = Field(min_length=2)


class APIClientTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"