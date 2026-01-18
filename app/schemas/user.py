from pydantic import BaseModel
from typing import List


class UserBase(BaseModel):
    name: str


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class ProfileUser(User):
    followers: List[User] = []
    following: List[User] = []

    class Config:
        from_attributes = True


class ProfileResponse(BaseModel):
    result: bool
    user: ProfileUser
