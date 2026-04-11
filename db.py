
from sqlalchemy.orm import declarative_base, sessionmaker
from pymongo import AsyncMongoClient
from config import DB_TYPE, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, MONGO_DB_NAME, MONGO_URI
from sqlalchemy import create_engine
import certifi

SQL_DB_URL = f"{DB_TYPE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQL_DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

mongo_client = AsyncMongoClient(MONGO_URI, tlsCAFile=certifi.where())

def get_mongo_db():
    return mongo_client[MONGO_DB_NAME]
