import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal
from app.models import Conversation, Message

def delete_empty_bugged_conversations():
    db = SessionLocal()
    try:
        # Find all conversations that start with "대화 " and have character_id = None
        convs = db.query(Conversation).filter(
            Conversation.character_id.is_(None),
            Conversation.title.like("대화 %")
        ).all()
        
        deleted_count = 0
        for conv in convs:
            # Check if it has any messages
            msg_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
            if msg_count == 0:
                print(f"Deleting empty buggy conversation {conv.id} ('{conv.title}')")
                db.delete(conv)
                deleted_count += 1
            else:
                print(f"Not deleting {conv.id} ('{conv.title}') because it has {msg_count} messages.")
        
        db.commit()
        print(f"Deleted {deleted_count} empty buggy conversations.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    delete_empty_bugged_conversations()
