from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, BLOB, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

DATABASE_URL = "sqlite:///./img.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Img(Base):
    __tablename__ = "img"
    id = Column(Integer, primary_key=True, autoincrement=True)
    img = Column(String(200))
    addr = Column(String(200))
    date = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)
