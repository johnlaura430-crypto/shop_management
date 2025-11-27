import os
from app import app, db

def reset_database():
    with app.app_context():
        # Delete the existing database file
        db_path = 'instance/shop.db'
        if os.path.exists(db_path):
            os.remove(db_path)
            print("Old database deleted.")
        
        # Create new tables
        db.create_all()
        
        # Create default user
        from werkzeug.security import generate_password_hash
        from models import User
        
        owner = User(
            username='owner',
            password_hash=generate_password_hash('owner123'),
            role='owner'
        )
        db.session.add(owner)
        db.session.commit()
        
        print("New database created successfully!")
        print("Default user: owner / owner123")

if __name__ == '__main__':
    reset_database()