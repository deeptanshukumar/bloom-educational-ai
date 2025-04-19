from app import app, db
from models.user import User
from models.session import Session, Interaction

def test_database():
    with app.app_context():
        # Create all tables if they don't exist
        db.create_all()

        # Query all users
        users = User.query.all()
        print(f"Number of users: {len(users)}")
        for user in users:
            print(f"User: {user.username}, Email: {user.email}")
        
        # Test creating a session
        if users:
            test_user = users[0]
            new_session = Session(user_id=test_user.id, subject="mathematics")
            db.session.add(new_session)
            db.session.commit()
            print(f"Created session for user {test_user.username}")

if __name__ == "__main__":
    test_database()