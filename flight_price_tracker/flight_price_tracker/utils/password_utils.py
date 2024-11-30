import hashlib
import os

def generate_salt():
    """Generate a random salt for password hashing."""
    return os.urandom(32)  # 32 bytes = 256 bits

def hash_password(password, salt):
    """
    Hash a password using SHA-256 with a salt.
    
    Args:
        password (str): The user's password
        salt (bytes): Random salt for additional security
    
    Returns:
        bytes: Hashed password
    """
    # Combine password and salt, then hash
    return hashlib.pbkdf2_hmac('sha256', 
                                password.encode('utf-8'), 
                                salt, 
                                100000)  # 100,000 iterations for security

def verify_password(stored_password, stored_salt, provided_password):
    """
    Verify if the provided password matches the stored password.
    
    Args:
        stored_password (bytes): The hashed password from database
        stored_salt (bytes): The salt used for original hashing
        provided_password (str): The password to verify
    
    Returns:
        bool: True if password is correct, False otherwise
    """
    # Hash the provided password with the stored salt
    hashed_provided_password = hash_password(provided_password, stored_salt)
    
    # Compare the newly hashed password with the stored password
    return hashed_provided_password == stored_password