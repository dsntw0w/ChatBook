import sys
sys.path.append('.')
from app.database import SessionLocal, engine, Base
from app.models import Conversation, Message
from app.schemas import ConversationCreate
import uuid
from datetime import datetime, timezone

def test():
    db = SessionLocal()
    # Create conversation with character_id = 999
    c_id = str(uuid.uuid4())
    conv = Conversation(
        id=c_id,
        title="Test Conv",
        provider="openai",
        model="gpt-5-nano",
        character_id=999,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(conv)
    db.commit()
    
    # query with is_(None)
    res1 = db.query(Conversation).filter(Conversation.character_id.is_(None)).all()
    # query with == None
    res2 = db.query(Conversation).filter(Conversation.character_id == None).all()
    
    print(f"Total None (is_): {len(res1)}, Total None (==): {len(res2)}")
    
    # check if our conv is in there
    found1 = any(c.id == c_id for c in res1)
    found2 = any(c.id == c_id for c in res2)
    print(f"Found in None (is_): {found1}, Found in None (==): {found2}")
    
    db.delete(conv)
    db.commit()

test()
