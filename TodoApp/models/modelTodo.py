from database import Base
from sqlalchemy import String, Column, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship


class Todo(Base):
    __tablename__ = 'Todo'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    description = Column(String(100))
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('User.id'))

    owner = relationship("User", back_populates="todo")
