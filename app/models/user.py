from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    api_key = Column(String(255), unique=True, index=True, nullable=False)

    tweets = relationship("Tweet", back_populates="author")
    likes = relationship("Like", back_populates="user")
    followers = relationship(
        "Follow",
        foreign_keys="Follow.followed_id",
        back_populates="following",
    )
    following = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
    )
