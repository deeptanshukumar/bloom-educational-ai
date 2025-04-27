from app import db  # Import the SQLAlchemy instance (db)
from sqlalchemy import Column, Integer, String, relationship

class Role(db.Model):
    """
    Represents a user role in the application.
    """
    __tablename__ = 'roles'  # Explicitly set the table name

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    description = Column(String(255))
    users = relationship('User', secondary='user_roles', back_populates='roles') # Corrected

    def __repr__(self):
        return f'<Role {self.name}>'
