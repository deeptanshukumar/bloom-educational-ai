from flask import Flask
from models import db
from models.user import User, Role
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    app = Flask(__name__)
    
    # Configure SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bloom_dev.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            
            # Create roles
            roles = [
                {'name': 'admin', 'description': 'Administrator with full access'},
                {'name': 'teacher', 'description': 'Can create and manage content'},
                {'name': 'student', 'description': 'Regular user with limited access'}
            ]
            
            for role_data in roles:
                if not Role.query.filter_by(name=role_data['name']).first():
                    role = Role(**role_data)
                    db.session.add(role)
                    print(f"Created role: {role_data['name']}")
            
            # Commit roles first
            db.session.commit()
            
            # Create test user if it doesn't exist
            test_email = 'deeptanshu.kumar13@gmail.com'
            test_user = User.query.filter_by(email=test_email).first()
            
            if not test_user:
                test_user = User(
                    username='deeptanshu',
                    email=test_email,
                    password_hash=generate_password_hash('password123', method='pbkdf2:sha256'),
                    is_active=True  # Make sure user is active
                )
                
                # Add admin role to the test user
                admin_role = Role.query.filter_by(name='admin').first()
                if admin_role:
                    test_user.roles.append(admin_role)
                else:
                    print("Warning: Admin role not found!")
                
                db.session.add(test_user)
                print(f"Created test user: {test_email}")
                
                db.session.commit()
                print("Database initialized successfully")
                
                # Verify user was created
                created_user = User.query.filter_by(email=test_email).first()
                if created_user:
                    print(f"Verified user exists with email: {created_user.email}")
                    print(f"User roles: {[role.name for role in created_user.roles]}")
                else:
                    print("Warning: Failed to verify user creation!")
            
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    init_database()