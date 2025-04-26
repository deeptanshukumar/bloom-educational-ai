from backend.app import db  # Import the db instance
from backend.models.user import User
from backend.models.role import Role
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    with db.app.app_context():
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

            else:
                # Update password for existing user
                user.password_hash = generate_password_hash(admin_password, method='pbkdf2:sha256')
                db.session.commit()
                print(f"Updated password for user: {user_email}")

            db.session.commit()
            print("Database setup complete")

        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            db.session.rollback()
            raise