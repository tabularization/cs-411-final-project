from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, LargeBinary

from flight_price_tracker.utils.password_utils import generate_salt, hash_password

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    salt = Column(LargeBinary, nullable=False)
    hashed_password = Column(LargeBinary, nullable=False)

    @classmethod
    def create_user(cls, username, password):
        """
        Create a new user with hashed password.
        
        Args:
            username (str): User's username
            password (str): User's password
        
        Returns:
            User: Newly created user object
        """
        salt = generate_salt()
        hashed_password = hash_password(password, salt)
        
        new_user = cls(
            username=username, 
            salt=salt, 
            hashed_password=hashed_password
        )
        
        db.session.add(new_user)
        db.session.commit()
        return new_user