from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:emR$d4pB@localhost:5432/TestDatabase'

SQLALCHEMY_DATABASE_URL = 'sqlite:///./todos_app.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()