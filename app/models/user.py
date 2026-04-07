from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.sql import func
from app.core.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    kc_sub = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_words = relationship("UserWord", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_users_kc_sub", "kc_sub", unique=True),)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', kc_sub='{self.kc_sub}')>"

