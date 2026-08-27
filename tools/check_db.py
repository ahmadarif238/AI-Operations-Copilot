import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from app.db.base import SessionLocal
from app.db.models import User, Ticket

def check():
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        ticket_count = db.query(Ticket).count()
        print(f"Users found: {user_count}")
        print(f"Tickets found: {ticket_count}")
        
        users = db.query(User).all()
        for u in users:
            print(f"- User: {u.email} ({u.role})")
            
    except Exception as e:
        print(f"Error checking DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check()
