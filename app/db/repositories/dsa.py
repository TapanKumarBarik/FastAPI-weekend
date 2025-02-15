from typing import List, Optional, Dict, Any
from ...schemas.dsa import DSAProblemCreate, TagCreate, DSAProblemUpdate
from ..database import database




class DSARepository:
    async def create_problem(self, user_id: int, problem: DSAProblemCreate) -> dict:
        async with database.transaction():
            # Insert problem
            query = """
            INSERT INTO dsa_problems (
                title, description, difficulty, source_url,
                confidence_score, priority, notes, solution,
                time_complexity, space_complexity, user_id,
                status
            )
            VALUES (
                :title, :description, :difficulty, :source_url,
                :confidence_score, :priority, :notes, :solution,
                :time_complexity, :space_complexity, :user_id,
                'not_started'
            )
            RETURNING id
            """
            values = {**problem.dict(exclude={'tag_ids'}), "user_id": user_id}
            problem_record = await database.fetch_one(query=query, values=values)
            
            # Add tags if provided
            if problem.tag_ids:
                for tag_id in problem.tag_ids:
                    await self._add_problem_tag(problem_record['id'], tag_id)
            
            # Get complete problem with tags
            return await self.get_problem(problem_record['id'])
    async def get_problem(self, problem_id: int) -> Optional[dict]:
        query = """
        WITH problem_data AS (
            SELECT 
                p.*,
                COALESCE(
                    json_agg(
                        json_build_object(
                            'id', t.id,
                            'name', t.name,
                            'description', t.description
                        )
                    ) FILTER (WHERE t.id IS NOT NULL),
                    '[]'::json
                ) as tags
            FROM dsa_problems p 
            LEFT JOIN problem_tags pt ON p.id = pt.problem_id
            LEFT JOIN tags t ON pt.tag_id = t.id
            WHERE p.id = :problem_id
            GROUP BY p.id
        )
        SELECT *, tags::json as tags
        FROM problem_data
        """
        result = await database.fetch_one(query=query, values={"problem_id": problem_id})
        if result:
            problem_dict = dict(result)
            # Ensure tags is always a list
            problem_dict['tags'] = problem_dict.get('tags', [])
            return problem_dict
        return None
    
    
    async def get_user_problems(
        self, 
        user_id: int, 
        difficulty: Optional[str] = None,
        status: Optional[str] = None,
        tag_id: Optional[int] = None
    ) -> List[dict]:
        query = """
        WITH problem_data AS (
            SELECT 
                p.*,
                COALESCE(
                    json_agg(
                        json_build_object(
                            'id', t.id,
                            'name', t.name,
                            'description', t.description
                        )
                    ) FILTER (WHERE t.id IS NOT NULL),
                    '[]'::json
                ) as tags
            FROM dsa_problems p
            LEFT JOIN problem_tags pt ON p.id = pt.problem_id
            LEFT JOIN tags t ON pt.tag_id = t.id
            WHERE p.user_id = :user_id
        """
        values = {"user_id": user_id}
        
        if difficulty:
            query += " AND p.difficulty = :difficulty"
            values["difficulty"] = difficulty
            
        if status:
            query += " AND p.status = :status"
            values["status"] = status
            
        if tag_id:
            query += " AND EXISTS (SELECT 1 FROM problem_tags WHERE problem_id = p.id AND tag_id = :tag_id)"
            values["tag_id"] = tag_id
            
        query += """
            GROUP BY p.id
        )
        SELECT *, tags::json as tags
        FROM problem_data
        ORDER BY updated_at DESC
        """
        
        result = await database.fetch_all(query=query, values=values)
        problems = []
        for row in result:
            problem_dict = dict(row)
            # Ensure tags is properly parsed from JSON
            if isinstance(problem_dict['tags'], str):
                import json
                problem_dict['tags'] = json.loads(problem_dict['tags'])
            problems.append(problem_dict)
        return problems
    
    async def _add_problem_tag(self, problem_id: int, tag_id: int) -> None:
        query = """
        INSERT INTO problem_tags (problem_id, tag_id)
        VALUES (:problem_id, :tag_id)
        ON CONFLICT DO NOTHING
        """
        await database.execute(
            query=query,
            values={"problem_id": problem_id, "tag_id": tag_id}
        )

    async def create_tag(self, tag: TagCreate) -> dict:
        query = """
        INSERT INTO tags (name, description)
        VALUES (:name, :description)
        RETURNING id, name, description
        """
        return await database.fetch_one(query=query, values=tag.dict())

    async def get_tags(self) -> List[dict]:
        query = "SELECT id, name, description FROM tags ORDER BY name"
        return await database.fetch_all(query=query)


    async def update_problem(
        self, 
        problem_id: int, 
        user_id: int, 
        updates: DSAProblemUpdate
    ) -> Optional[dict]:
        # First verify ownership
        problem = await self.get_problem(problem_id)
        if not problem or problem["user_id"] != user_id:
            return None

        # Build update query
        update_fields = []
        values = {"problem_id": problem_id}
        
        for field, value in updates.dict(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = :{field}")
                values[field] = value
                
        if not update_fields:
            return problem

        query = f"""
        UPDATE dsa_problems 
        SET {", ".join(update_fields)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = :problem_id
        RETURNING *
        """
        
        await database.execute(query=query, values=values)
        return await self.get_problem(problem_id)

    async def delete_problem(self, problem_id: int, user_id: int) -> bool:
        async with database.transaction():
            # First verify ownership
            check_query = """
            SELECT id FROM dsa_problems 
            WHERE id = :problem_id AND user_id = :user_id
            """
            problem = await database.fetch_one(
                query=check_query,
                values={"problem_id": problem_id, "user_id": user_id}
            )
            
            if not problem:
                return False
                
            # Delete problem tags
            await database.execute(
                "DELETE FROM problem_tags WHERE problem_id = :problem_id",
                values={"problem_id": problem_id}
            )
            
            # Delete problem
            await database.execute(
                "DELETE FROM dsa_problems WHERE id = :problem_id",
                values={"problem_id": problem_id}
            )
            
            return True



    async def add_tag_to_problem(self, problem_id: int, tag_id: int, user_id: int) -> bool:
        # Verify problem ownership
        check_query = """
        SELECT id FROM dsa_problems 
        WHERE id = :problem_id AND user_id = :user_id
        """
        problem = await database.fetch_one(
            query=check_query,
            values={"problem_id": problem_id, "user_id": user_id}
        )
        
        if not problem:
            return False
            
        # Add tag
        query = """
        INSERT INTO problem_tags (problem_id, tag_id)
        VALUES (:problem_id, :tag_id)
        ON CONFLICT DO NOTHING
        """
        await database.execute(
            query=query,
            values={"problem_id": problem_id, "tag_id": tag_id}
        )
        return True

    async def remove_tag_from_problem(self, problem_id: int, tag_id: int, user_id: int) -> bool:
        # Verify problem ownership
        check_query = """
        SELECT id FROM dsa_problems 
        WHERE id = :problem_id AND user_id = :user_id
        """
        problem = await database.fetch_one(
            query=check_query,
            values={"problem_id": problem_id, "user_id": user_id}
        )
        
        if not problem:
            return False
            
        # Remove tag
        query = """
        DELETE FROM problem_tags 
        WHERE problem_id = :problem_id AND tag_id = :tag_id
        """
        await database.execute(
            query=query,
            values={"problem_id": problem_id, "tag_id": tag_id}
        )
        return True