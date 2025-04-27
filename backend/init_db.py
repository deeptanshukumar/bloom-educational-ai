from app import app, db
from models.user import User
from models.session import Session, Interaction

def init_database():
    with app.app_context():
        db.create_all()
        if User.query.filter_by(username='test_user').first() is None:
            test_user = User(
                username='test_user',
                email='test@example.com',
                password_hash='hashed_password_here'
            )
            db.session.add(test_user)
            db.session.commit()
            print("Test user created")
        print("Database initialized successfully")

if __name__ == "__main__":
    init_database()