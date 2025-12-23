from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Like(Base):
    __tablename__ = "likes"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), primary_key=True)

    user = relationship("User", back_populates="likes")
    tweet = relationship("Tweet", back_populates="likes")
