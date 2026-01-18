from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class TweetMedia(Base):
    __tablename__ = "tweet_medias"

    tweet_id = Column(Integer, ForeignKey("tweets.id"), primary_key=True)
    media_id = Column(Integer, ForeignKey("medias.id"), primary_key=True)

    tweet = relationship("Tweet", back_populates="tweet_medias")
    media = relationship("Media", back_populates="tweet_medias")
