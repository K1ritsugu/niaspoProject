import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class OrderStatusEnum(enum.Enum):
    preparing = "preparing"
    ready_waiting_for_courier = "ready_waiting_for_courier"
    on_the_way = "on_the_way"
    closed = "closed"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    address = Column(String)
    role = Column(String, default='user')


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.now)
    closed_at = Column(DateTime, nullable=True, default=datetime.now)
    order = relationship("Order", back_populates="transaction", uselist=False)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    items = Column(JSON, nullable=False) 
    status = Column(String, default="processing")
    payment_method = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    closed_at = Column(DateTime, nullable=True) 
    transaction = relationship("Transaction", back_populates="order")
    user = relationship("User")


class OrderStatus(Base):
    __tablename__ = "order_statuses"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True, nullable=False)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

    order = relationship("Order")