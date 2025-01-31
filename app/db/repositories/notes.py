from typing import List, Optional
from fastapi import HTTPException
from ...schemas.note import NotebookCreate, SectionCreate, PageCreate
from ..database import database

class NoteRepository:
    async def create_notebook(self, user_id: int, notebook: NotebookCreate) -> dict:
        query = """
        INSERT INTO notebooks (title, description, user_id)
        VALUES (:title, :description, :user_id)
        RETURNING id, title, description, user_id, created_at, updated_at
        """
        values = {**notebook.dict(), "user_id": user_id}
        return await database.fetch_one(query=query, values=values)

    async def get_notebooks(self, user_id: int) -> List[dict]:
        query = """
        SELECT id, title, description, user_id, created_at, updated_at
        FROM notebooks
        WHERE user_id = :user_id
        ORDER BY updated_at DESC
        """
        return await database.fetch_all(query=query, values={"user_id": user_id})

    async def create_section(self, notebook_id: int, section: SectionCreate) -> dict:
        query = """
        INSERT INTO sections (title, notebook_id)
        VALUES (:title, :notebook_id)
        RETURNING id, title, notebook_id, created_at, updated_at
        """
        values = {**section.dict(), "notebook_id": notebook_id}
        return await database.fetch_one(query=query, values=values)
    
    async def get_sections(self, notebook_id: int) -> List[dict]:
        """Get all sections with their pages"""
        query = """
        SELECT 
            s.id,
            s.title,
            s.notebook_id,
            s.created_at,
            s.updated_at,
            COALESCE(
                jsonb_agg(
                    CASE WHEN p.id IS NOT NULL THEN
                        jsonb_build_object(
                            'id', p.id,
                            'title', p.title,
                            'content', p.content,
                            'section_id', p.section_id,
                            'created_at', p.created_at,
                            'updated_at', p.updated_at
                        )
                    ELSE NULL END
                ) FILTER (WHERE p.id IS NOT NULL),
                '[]'::jsonb
            ) as pages
        FROM sections s
        LEFT JOIN pages p ON s.id = p.section_id
        WHERE s.notebook_id = :notebook_id
        GROUP BY s.id, s.title, s.notebook_id, s.created_at, s.updated_at
        ORDER BY s.created_at DESC
        """
        sections = await database.fetch_all(query=query, values={"notebook_id": notebook_id})
        
        # Convert sections to list of dicts
        result = []
        for section in sections:
            section_dict = dict(section)
            # Parse the JSON string into a Python list if it's a string
            if isinstance(section_dict['pages'], str):
                import json
                section_dict['pages'] = json.loads(section_dict['pages'])
            result.append(section_dict)
        
        return result
    async def delete_notebook(self, notebook_id: int, user_id: int) -> bool:
        query = """
        DELETE FROM notebooks
        WHERE id = :notebook_id AND user_id = :user_id
        RETURNING id
        """
        result = await database.fetch_one(
            query=query, 
            values={"notebook_id": notebook_id, "user_id": user_id}
        )
        return result is not None

    async def delete_section(self, section_id: int) -> bool:
        query = """
        DELETE FROM sections
        WHERE id = :section_id
        RETURNING id
        """
        result = await database.fetch_one(
            query=query,
            values={"section_id": section_id}
        )
        return result is not None

    async def delete_page(self, page_id: int) -> bool:
        query = """
        DELETE FROM pages
        WHERE id = :page_id
        RETURNING id
        """
        result = await database.fetch_one(
            query=query,
            values={"page_id": page_id}
        )
        return result is not None
        # Add to NoteRepository class
    
    async def create_page(self, section_id: int, page: PageCreate) -> dict:
        query = """
        INSERT INTO pages (title, content, section_id)
        VALUES (:title, :content, :section_id)
        RETURNING id, title, content, section_id, created_at, updated_at
        """
        values = {**page.dict(), "section_id": section_id}
        return await database.fetch_one(query=query, values=values)
    
    async def get_pages(self, section_id: int) -> List[dict]:
        query = """
        SELECT id, title, content, section_id, created_at, updated_at
        FROM pages
        WHERE section_id = :section_id
        ORDER BY updated_at DESC
        """
        return await database.fetch_all(query=query, values={"section_id": section_id})
    
    async def update_page(self, page_id: int, updates: PageCreate) -> Optional[dict]:
        query = """
        UPDATE pages
        SET title = :title,
            content = :content,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :page_id
        RETURNING id, title, content, section_id, created_at, updated_at
        """
        values = {**updates.dict(), "page_id": page_id}
        return await database.fetch_one(query=query, values=values)