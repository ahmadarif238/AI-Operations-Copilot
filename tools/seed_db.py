import sys
import os
import requests
# Add backend to path to import models if needed, but using API is better/safer to test E2E.
# However, for direct DB seeding without API running, we can use SQLAlchemy.
# user spec: "script to seed DB".

sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from app.db.base import SessionLocal, engine
from app.db.models import Base, User, Ticket, Log
from app.core.config import settings
from sqlalchemy.orm import Session

def seed():
    print("Seeding Database...")
    
    # Create Tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if exists
    if db.query(User).filter(User.email == "admin@copilot.com").first():
        print("Data already exists.")
        return

    # Create Users
    admin = User(name="Admin User", email="admin@copilot.com", role="admin")
    op_user = User(name="Operator", email="ops@copilot.com", role="user")
    
    db.add(admin)
    db.add(op_user)
    db.commit()
    
    # Create Tickets
    t1 = Ticket(title="Test Ticket 1", description="Initial seeded ticket", severity="low", created_by=admin.id)
    db.add(t1)
    
    # Create Logs
    l1 = Log(type="INFO", message="System initialized")
    db.add(l1)
    
    db.commit()
    db.close()
    print("Seeding Complete. Admin: admin@copilot.com")

if __name__ == "__main__":
    seed()
