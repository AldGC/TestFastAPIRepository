from TodoApp.database import Base
from sqlalchemy import String, Column, Integer, Boolean
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    hashed_password = Column(String(1000))
    is_active = Column(Boolean, default=True)
    role = Column(String(100))
    phone_number = Column(String(100))

    todo = relationship("Todo", back_populates="owner")
