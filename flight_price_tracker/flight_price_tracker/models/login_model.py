from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.exc import IntegrityError

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
        
        Raises:
            ValueError: If the username already exists or the password is empty.

        Returns:
            User: Newly created user object
        """
        if not password:
            raise ValueError("Password cannot be empty")

        salt = generate_salt()
        hashed_password = hash_password(password, salt)

        new_user = cls(
            username=username,
            salt=salt,
            hashed_password=hashed_password
        )

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"User with username '{username}' already exists")
        return new_user

    @classmethod
    def check_password(cls, username, password):
        """
        Check a user's password.

        Raises:
            ValueError: If the user is not found or the password is incorrect.

        Returns:
            bool: True if the password is correct.
        """
        user = cls.query.filter_by(username=username).first()
        if not user:
            raise ValueError(f"User {username} not found")
        salt = user.salt
        hashed_password = hash_password(password, salt)
        if hashed_password != user.hashed_password:
            raise ValueError("Incorrect password")
        return True