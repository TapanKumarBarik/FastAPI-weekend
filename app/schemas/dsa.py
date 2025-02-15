from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class ProblemStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NEED_REVIEW = "need_review"

class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True

class DSAProblemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    difficulty: DifficultyLevel
    source_url: Optional[HttpUrl] = None
    confidence_score: float = Field(0.0, ge=0.0, le=5.0)
    priority: int = Field(0, ge=0, le=5)
    notes: Optional[str] = None
    solution: Optional[str] = None
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None

class DSAProblemCreate(DSAProblemBase):
    tag_ids: List[int] = []

class DSAProblem(BaseModel):
    id: int
    title: str
    description: str
    difficulty: DifficultyLevel
    status: ProblemStatus
    source_url: Optional[HttpUrl] = None
    confidence_score: float = Field(0.0, ge=0.0, le=5.0)
    priority: int = Field(0, ge=0, le=5)
    notes: Optional[str] = None
    solution: Optional[str] = None
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_reviewed: Optional[datetime]
    tags: List[Tag] = []  # Ensure this is defined as a list of Tag objects

    class Config:
        from_attributes = True
        
class DSAProblemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    source_url: Optional[HttpUrl] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=5.0)
    priority: Optional[int] = Field(None, ge=0, le=5)
    notes: Optional[str] = None
    solution: Optional[str] = None
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    status: Optional[ProblemStatus] = None