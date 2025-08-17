from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserWord(Base):
    __tablename__ = "user_words"

    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    score = Column(Float, default=0.0, nullable=False)
    last_reviewed = Column(DateTime(timezone=True), server_default=func.now())

    word = relationship("Word", back_populates="user_words")

    def __repr__(self):
        return f"<UserWord(id={self.id}, word_id={self.word_id}, score={self.score})>"
