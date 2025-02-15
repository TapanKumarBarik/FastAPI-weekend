from sqlalchemy import Column, Integer, String, DateTime, Enum, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from .user import Base

class DifficultyLevel(str, PyEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class ProblemStatus(str, PyEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NEED_REVIEW = "need_review"

# Association table for problems and tags
problem_tags = Table(
    'problem_tags',
    Base.metadata,
    Column('problem_id', Integer, ForeignKey('dsa_problems.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)
    description = Column(String(200), nullable=True)

class DSAProblem(Base):
    __tablename__ = "dsa_problems"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String, nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    status = Column(Enum(ProblemStatus), default=ProblemStatus.NOT_STARTED)
    source_url = Column(String(500), nullable=True)
    confidence_score = Column(Float, default=0.0)
    priority = Column(Integer, default=0)
    notes = Column(String, nullable=True)
    solution = Column(String, nullable=True)
    time_complexity = Column(String(50), nullable=True)
    space_complexity = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_reviewed = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    tags = relationship("Tag", secondary=problem_tags)
    user = relationship("User", back_populates="dsa_problems")