from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.utils.auth import get_current_user_unified as get_current_user
from app.models.user import User
from app.models.tree_path import TreePath
from app.schemas.tree import TreePathCreate, TreePath as TreePathSchema
from uuid import UUID

router = APIRouter(
    prefix="/tree-paths",
    tags=["tree-paths"],
    dependencies=[Depends(get_current_user)],
)

@router.post("/", response_model=TreePathSchema)
async def create_tree_path(
    tree_path: TreePathCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_tree_path = TreePath(
        user_id=current_user.id,
        tree_type=tree_path.tree_type,
        tree_json=tree_path.tree_json
    )
    db.add(db_tree_path)
    db.commit()
    db.refresh(db_tree_path)
    return db_tree_path

@router.get("/", response_model=List[TreePathSchema])
async def get_user_tree_paths(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(TreePath).filter(TreePath.user_id == current_user.id).all()

@router.get("/{tree_path_id}", response_model=TreePathSchema)
async def get_tree_path(
    tree_path_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tree_path = db.query(TreePath).filter(
        TreePath.id == tree_path_id, 
        TreePath.user_id == current_user.id
    ).first()
    
    if not tree_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tree path not found"
        )
    
    return tree_path

@router.delete("/{tree_path_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tree_path(
    tree_path_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tree_path = db.query(TreePath).filter(
        TreePath.id == tree_path_id, 
        TreePath.user_id == current_user.id
    ).first()
    
    if not tree_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tree path not found"
        )
    
    db.delete(tree_path)
    db.commit()
    return None 