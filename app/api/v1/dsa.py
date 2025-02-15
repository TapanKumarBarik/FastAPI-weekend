from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ...db.repositories.dsa import DSARepository
from ...schemas.dsa import DSAProblem, DSAProblemCreate, DSAProblemUpdate, Tag, TagCreate
from ...dependencies import get_current_active_user
from ...schemas.user import User

router = APIRouter()

@router.post("/problems/", response_model=DSAProblem)
async def create_problem(
    problem: DSAProblemCreate,
    current_user: User = Depends(get_current_active_user),
    dsa_repo: DSARepository = Depends()
):
    """Create a new DSA problem"""
    return await dsa_repo.create_problem(current_user.id, problem)

@router.get("/problems/", response_model=List[DSAProblem])
async def get_problems(
    current_user: User = Depends(get_current_active_user),
    dsa_repo: DSARepository = Depends(),
    difficulty: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    tag_id: Optional[int] = Query(None)
):
    """Get all DSA problems with optional filters"""
    return await dsa_repo.get_user_problems(
        user_id=current_user.id,
        difficulty=difficulty,
        status=status,
        tag_id=tag_id
    )

@router.get("/problems/{problem_id}", response_model=DSAProblem)
async def get_problem(
    problem_id: int,
    current_user: User = Depends(get_current_active_user),
    dsa_repo: DSARepository = Depends()
):
    """Get a specific DSA problem by ID"""
    problem = await dsa_repo.get_problem(problem_id)
    if not problem or problem.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem

@router.put("/problems/{problem_id}", response_model=DSAProblem)
async def update_problem(
    problem_id: int,
    updates: DSAProblemUpdate,
    current_user: User = Depends(get_current_active_user),
    dsa_repo: DSARepository = Depends()
):
    """Update a DSA problem"""
    problem = await dsa_repo.update_problem(problem_id, current_user.id, updates)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem

@router.delete("/problems/{problem_id}", status_code=204)
async def delete_problem(
    problem_id: int,
    current_user: User = Depends(get_current_active_user),
    dsa_repo: DSARepository = Depends()
):
    """Delete a DSA problem"""
    deleted = await dsa_repo.delete_problem(problem_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Problem not found")

@router.post("/tags/", response_model=Tag)
async def create_tag(
    tag: TagCreate,
    dsa_repo: DSARepository = Depends()
):
    """Create a new tag"""
    return await dsa_repo.create_tag(tag)

@router.get("/tags/", response_model=List[Tag])
async def get_tags(
    dsa_repo: DSARepository = Depends()
):
    """Get all available tags"""
    return await dsa_repo.get_tags()

@router.post("/problems/{problem_id}/tags/{tag_id}")
async def add_tag_to_problem(
    problem_id: int,
    tag_id: int,
    current_user: User = Depends(get_current_active_user),
    dsa_repo: DSARepository = Depends()
):
    """Add a tag to a problem"""
    added = await dsa_repo.add_tag_to_problem(problem_id, tag_id, current_user.id)
    if not added:
        raise HTTPException(status_code=404, detail="Problem or tag not found")
    return {"message": "Tag added successfully"}

@router.delete("/problems/{problem_id}/tags/{tag_id}")
async def remove_tag_from_problem(
    problem_id: int,
    tag_id: int,
    current_user: User = Depends(get_current_active_user),
    dsa_repo: DSARepository = Depends()
):
    """Remove a tag from a problem"""
    removed = await dsa_repo.remove_tag_from_problem(problem_id, tag_id, current_user.id)
    if not removed:
        raise HTTPException(status_code=404, detail="Problem or tag not found")
    return {"message": "Tag removed successfully"}