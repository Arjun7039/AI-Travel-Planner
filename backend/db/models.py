from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Date, JSON, Uuid
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), default="")
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    trips = relationship("Trip", back_populates="user")

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"))
    origin = Column(String(100))
    destination = Column(String(100))
    start_date = Column(Date)
    end_date = Column(Date)
    num_travellers = Column(Integer)
    budget_inr = Column(Numeric)
    preferences = Column(JSON)
    result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="trips")
