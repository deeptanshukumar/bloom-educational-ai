from app import app
from models import db
from models.user import Role, User
import os

def init_roles():
    """Initialize basic roles in the database"""
    with app.app_context():
        # Create roles if they don't exist
        roles = [
            {'name': 'admin', 'description': 'Administrator with full access'},
            {'name': 'teacher', 'description': 'Can create and manage content'},
            {'name': 'student', 'description': 'Regular user with limited access'}
        ]
        
        for role_data in roles:
            role = Role.query.filter_by(name=role_data['name']).first()
            if not role:
                new_role = Role(name=role_data['name'], description=role_data['description'])
                db.session.add(new_role)
                print(f"Created role: {role_data['name']}")
        
        # Create admin user if specified in environment variables
        admin_username = os.environ.get('ADMIN_USERNAME')
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        
        if admin_username and admin_email and admin_password:
            admin = User.query.filter_by(username=admin_username).first()
            if not admin:
                from werkzeug.security import generate_password_hash
                admin_user = User(
                    username=admin_username,
                    email=admin_email,
                    password_hash=generate_password_hash(admin_password, method='pbkdf2:sha256')
                )
                
                # Add admin role to the admin user
                admin_role = Role.query.filter_by(name='admin').first()
                if admin_role:
                    admin_user.roles.append(admin_role)
                
                db.session.add(admin_user)
                print(f"Created admin user: {admin_username}")
        
        db.session.commit()
        print("Roles initialization complete")

if __name__ == "__main__":
    init_roles()