from flask import Flask
from models import db
from models.user import User, Role
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    app = Flask(__name__)
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
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
            
            # Create your user account
            user_email = 'deeptanshu.kumar13@gmail.com'
            admin_password = os.environ.get('ADMIN_PASSWORD')
            if not admin_password:
                print("Warning: ADMIN_PASSWORD not set in environment variables")
                return
                
            user = User.query.filter_by(email=user_email).first()
            
            if not user:
                user = User(
                    username='deeptanshu',
                    email=user_email,
                    password_hash=generate_password_hash(admin_password, method='pbkdf2:sha256'),
                    is_active=True
                )
                
                # Add admin role to the user
                admin_role = Role.query.filter_by(name='admin').first()
                if admin_role:
                    user.roles.append(admin_role)
                else:
                    print("Warning: Admin role not found!")
                
                db.session.add(user)
                print(f"Created user: {user_email}")
                
                db.session.commit()
                print("Database initialized successfully")
            else:
                # Update password for existing user
                user.password_hash = generate_password_hash(admin_password, method='pbkdf2:sha256')
                db.session.commit()
                print(f"Updated password for user: {user_email}")
            
            print("Database setup complete")
                
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    init_database()