from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.utils.auth import get_current_user_unified as get_current_user
from app.models.user import User
from app.models.node_note import NodeNote
from app.schemas.tree import NodeNoteCreate, NodeNote as NodeNoteSchema

router = APIRouter(
    prefix="/node-notes",
    tags=["node-notes"],
    dependencies=[Depends(get_current_user)],
)

@router.post("/", response_model=NodeNoteSchema)
async def create_node_note(
    note: NodeNoteCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if note already exists
    existing_note = db.query(NodeNote).filter(
        NodeNote.user_id == current_user.id,
        NodeNote.node_id == note.node_id,
        NodeNote.action_index == note.action_index
    ).first()
    
    if existing_note:
        # Update existing note
        existing_note.note_text = note.note_text
        db.commit()
        db.refresh(existing_note)
        return existing_note
    
    # Create new note
    db_note = NodeNote(
        user_id=current_user.id,
        node_id=note.node_id,
        action_index=note.action_index,
        note_text=note.note_text
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@router.get("/", response_model=List[NodeNoteSchema])
async def get_user_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(NodeNote).filter(NodeNote.user_id == current_user.id).all()

@router.get("/node/{node_id}", response_model=List[NodeNoteSchema])
async def get_node_notes(
    node_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(NodeNote).filter(
        NodeNote.node_id == node_id,
        NodeNote.user_id == current_user.id
    ).all()

@router.get("/{note_id}", response_model=NodeNoteSchema)
async def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(NodeNote).filter(
        NodeNote.id == note_id, 
        NodeNote.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    return note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(NodeNote).filter(
        NodeNote.id == note_id, 
        NodeNote.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    db.delete(note)
    db.commit()
    return None 