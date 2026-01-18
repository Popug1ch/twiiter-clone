from pydantic import BaseModel
from typing import List


class TweetCreate(BaseModel):
    tweet_data: str
    tweet_media_ids: List[int] | None = None


class LikeUser(BaseModel):
    user_id: int
    name: str


class Author(BaseModel):
    id: int
    name: str


class TweetInFeed(BaseModel):
    id: int
    content: str
    attachments: List[str]
    author: Author
    likes: List[LikeUser]


class TweetsFeedResponse(BaseModel):
    result: bool
    tweets: List[TweetInFeed]
