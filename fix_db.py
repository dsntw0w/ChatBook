import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal
from app.models import Conversation, Message, ChatSession

def fix_corrupted_conversations():
    db = SessionLocal()
    try:
        # Find all messages that have a session_id but their conversation has character_id = None
        messages = db.query(Message).filter(Message.session_id.isnot(None)).all()
        
        fixed_count = 0
        for msg in messages:
            conv = db.query(Conversation).filter(Conversation.id == msg.conversation_id).first()
            if conv and conv.character_id is None:
                # Find the character_id from the session
                session = db.query(ChatSession).filter(ChatSession.id == msg.session_id).first()
                if session:
                    print(f"Fixing conversation {conv.id} ('{conv.title}') - Setting character_id to {session.character_id}")
                    conv.character_id = session.character_id
                    fixed_count += 1
        
        db.commit()
        print(f"Fixed {fixed_count} corrupted conversations in the database.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_corrupted_conversations()
