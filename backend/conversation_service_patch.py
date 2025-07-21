
def create_conversation_with_sequence(db: Session, **kwargs) -> Conversation:
    """Create conversation with explicit sequence handling"""
    try:
        # Use raw SQL to ensure sequence default is applied
        result = db.execute(text("""
            INSERT INTO conversations (user_id, title, auto_generated_title, 
                                    category_id, is_favorite, is_archived, 
                                    last_message_at, message_count, total_tokens_used)
            VALUES (:user_id, :title, :auto_generated_title, 
                   :category_id, :is_favorite, :is_archived,
                   :last_message_at, :message_count, :total_tokens_used)
            RETURNING id, created_at, updated_at;
        """), kwargs)
        
        row = result.fetchone()
        conversation_id, created_at, updated_at = row
        
        # Now fetch the full conversation object
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        return conversation
        
    except Exception as e:
        db.rollback()
        raise e
