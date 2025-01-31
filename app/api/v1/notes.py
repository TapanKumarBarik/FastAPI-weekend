from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ...schemas.note import Notebook, NotebookCreate, Section, SectionCreate, Page, PageCreate
from ...db.repositories.notes import NoteRepository
from ...dependencies import get_current_active_user
from ...schemas.user import User
from pydantic import BaseModel

router = APIRouter()

class DeleteResponse(BaseModel):
    message: str

# Notebook endpoints
@router.post("/notebooks/", response_model=Notebook)
async def create_notebook(
    notebook: NotebookCreate,
    current_user: User = Depends(get_current_active_user),
    note_repo: NoteRepository = Depends()
):
    """Create a new notebook"""
    return await note_repo.create_notebook(current_user.id, notebook)

@router.get("/notebooks/", response_model=List[Notebook])
async def get_notebooks(
    current_user: User = Depends(get_current_active_user),
    note_repo: NoteRepository = Depends()
):
    """Get all notebooks for the current user"""
    return await note_repo.get_notebooks(current_user.id)

@router.delete("/notebooks/{notebook_id}", response_model=DeleteResponse)
async def delete_notebook(
    notebook_id: int,
    current_user: User = Depends(get_current_active_user),
    note_repo: NoteRepository = Depends()
):
    """Delete a notebook and all its contents"""
    deleted = await note_repo.delete_notebook(notebook_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return DeleteResponse(message="Notebook deleted successfully")

# Section endpoints
@router.post("/notebooks/{notebook_id}/sections/", response_model=Section)
async def create_section(
    notebook_id: int,
    section: SectionCreate,
    note_repo: NoteRepository = Depends()
):
    """Create a new section in a notebook"""
    return await note_repo.create_section(notebook_id, section)

@router.get("/notebooks/{notebook_id}/sections/", response_model=List[Section])
async def get_sections(
    notebook_id: int,
    note_repo: NoteRepository = Depends()
):
    """Get all sections in a notebook"""
    return await note_repo.get_sections(notebook_id)

@router.delete("/sections/{section_id}", response_model=DeleteResponse)
async def delete_section(
    section_id: int,
    note_repo: NoteRepository = Depends()
):
    """Delete a section and all its pages"""
    deleted = await note_repo.delete_section(section_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Section not found")
    return DeleteResponse(message="Section deleted successfully")

# Page endpoints
@router.post("/sections/{section_id}/pages/", response_model=Page)
async def create_page(
    section_id: int,
    page: PageCreate,
    note_repo: NoteRepository = Depends()
):
    """Create a new page in a section"""
    return await note_repo.create_page(section_id, page)

@router.get("/sections/{section_id}/pages/", response_model=List[Page])
async def get_pages(
    section_id: int,
    note_repo: NoteRepository = Depends()
):
    """Get all pages in a section"""
    return await note_repo.get_pages(section_id)

@router.put("/pages/{page_id}", response_model=Page)
async def update_page(
    page_id: int,
    page: PageCreate,
    note_repo: NoteRepository = Depends()
):
    """Update a page's content"""
    updated_page = await note_repo.update_page(page_id, page)
    if not updated_page:
        raise HTTPException(status_code=404, detail="Page not found")
    return updated_page

@router.delete("/pages/{page_id}", response_model=DeleteResponse)
async def delete_page(
    page_id: int,
    note_repo: NoteRepository = Depends()
):
    """Delete a page"""
    deleted = await note_repo.delete_page(page_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Page not found")
    return DeleteResponse(message="Page deleted successfully")