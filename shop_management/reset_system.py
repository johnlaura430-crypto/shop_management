import os
import sqlite3
from app import app, db, User
from werkzeug.security import generate_password_hash

def reset_system():
    print("🔄 Resetting MrCheap Shop System...")
    print("⚠️  WARNING: This will delete ALL data!")
    print("=" * 50)
    
    confirmation = input("Type 'RESET' to confirm: ")
    if confirmation != 'RESET':
        print("❌ Reset cancelled.")
        return
    
    with app.app_context():
        # Delete all data from tables
        try:
            # Drop all tables and recreate
            db.drop_all()
            db.create_all()
            
            # Create default owner user
            owner = User(
                username='owner',
                password_hash=generate_password_hash('owner123'),
                role='owner'
            )
            db.session.add(owner)
            db.session.commit()
            
            print("✅ System reset successfully!")
            print("📝 Default login created:")
            print("   Username: owner")
            print("   Password: owner123")
            print("🎯 System is now ready for fresh start!")
            
        except Exception as e:
            print(f"❌ Error resetting system: {e}")
    
    input("Press Enter to continue...")

if __name__ == '__main__':
    reset_system()