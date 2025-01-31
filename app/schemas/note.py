from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class PageBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: Optional[str] = None

class PageCreate(PageBase):
    pass

class Page(PageBase):
    id: int
    section_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}

class SectionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)

class SectionCreate(SectionBase):
    pass

class Section(SectionBase):
    id: int
    notebook_id: int
    created_at: datetime
    updated_at: datetime
    pages: List[Page] = []

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}

class NotebookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)

class NotebookCreate(NotebookBase):
    pass

class Notebook(NotebookBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    sections: List[Section] = []

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}