import os
import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()


SQLALCHEMY_DATABASE_URL = "sqlite:///crm_app.db"


engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(255), index=True)
    interaction_type = Column(String(50))
    date = Column(DateTime, default=datetime.datetime.utcnow)
    topics = Column(Text)
    sentiment = Column(String(50))

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(255), index=True)
    schedule_type = Column(String(50)) # meeting, call, email
    scheduled_date = Column(DateTime)

class Sample(Base):
    __tablename__ = "samples"
    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(255), index=True)
    sample_name = Column(String(255))
    quantity = Column(Integer)


Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()