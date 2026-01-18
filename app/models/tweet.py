from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=text("NOW()"))

    author = relationship("User", back_populates="tweets")
    tweet_medias = relationship("TweetMedia", back_populates="tweet")
    likes = relationship("Like", back_populates="tweet")
