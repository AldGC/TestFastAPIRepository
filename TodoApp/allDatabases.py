from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

"""
sqlite
SQLALCHEMY_DATABASE_URL = 'sqlite:///./todos_app.db'
"""


#mysql
#SQLALCHEMY_DATABASE_URL = 'mysql+mysqlconnector://root:%Bin0s-105%@127.0.0.1:3307/todoapp'


#postgresql
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:admin*1234!@127.0.0.1:5432/TodoAppDatabase'

"""
sqlite
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
"""

"""
mysql
engine = create_engine(SQLALCHEMY_DATABASE_URL)
"""

#postgresql
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
