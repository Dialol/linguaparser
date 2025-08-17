from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, nullable=False, index=True)
    translation = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    __table_args__ = (
            Index('idx_word_unique', 'word', unique=True),
            )

    user_words = relationship("UserWord", back_populates="word")

    def __repr__(self):
        return f"<Word(id={self.id}, word='{self.word}', translation='{self.translation}')>"
