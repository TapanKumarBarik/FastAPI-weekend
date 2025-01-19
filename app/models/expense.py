from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .user import Base

# Group members association table
group_members = Table(
    'group_members',
    Base.metadata,
    Column('group_id', Integer, ForeignKey('groups.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    members = relationship("User", secondary=group_members)
    expenses = relationship("Expense", back_populates="group")

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    description = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=True)
    
    user = relationship("User", back_populates="expenses")
    group = relationship("Group", back_populates="expenses")