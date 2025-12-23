from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Media(Base):
    __tablename__ = "medias"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"))

    tweet_medias = relationship("TweetMedia", back_populates="media")
