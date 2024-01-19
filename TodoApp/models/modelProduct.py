from TodoApp.database import Base
from sqlalchemy import String, Column, Integer, Float


class Product(Base):
    __tablename__ = 'Product'

    id_product = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    description = Column(String(100))
    price = Column(Float)
