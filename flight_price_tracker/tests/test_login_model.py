import pytest
from flight_price_tracker.models.login_model import User, db
from flight_price_tracker.utils.password_utils import verify_password

@pytest.fixture
def sample_user():
    """Sample user data for tests."""
    return {
        "username": "testuser",
        "password": "securepassword123"
    }

@pytest.fixture
def session(app):
    """Provide a database session for tests."""
    with app.app_context():
        yield db.session
        db.session.rollback()


##########################################################
# User Creation
##########################################################

def test_create_user(session, sample_user):
    """Test creating a new user with a unique username."""
    User.create_user(**sample_user)
    user = session.query(User).filter_by(username=sample_user["username"]).first()
    assert user is not None, "User should be created in the database."
    assert user.username == sample_user["username"], "Username should match the input."
    assert len(user.salt) > 0, "Salt should be generated."
    assert len(user.hashed_password) > 0, "Password should be hashed."


def test_create_duplicate_user(session, sample_user):
    """Test attempting to create a user with a duplicate username."""
    User.create_user(**sample_user)
    with pytest.raises(ValueError, match="User with username 'testuser' already exists"):
        User.create_user(**sample_user)


def test_create_user_empty_password(session, sample_user):
    """Test creating a user with an empty password."""
    sample_user["password"] = ""
    with pytest.raises(Exception):
        User.create_user(**sample_user)


##########################################################
# Password Handling
##########################################################

def test_check_password_correct(session, sample_user):
    """Test checking the correct password."""
    User.create_user(**sample_user)
    user = session.query(User).filter_by(username=sample_user["username"]).first()
    assert verify_password(user.hashed_password, user.salt, sample_user["password"]) is True, "Password should match."


def test_check_password_incorrect(session, sample_user):
    """Test checking an incorrect password."""
    User.create_user(**sample_user)
    user = session.query(User).filter_by(username=sample_user["username"]).first()
    assert verify_password(user.hashed_password, user.salt, "wrongpassword") is False, "Password should not match."

def test_check_password_user_not_found(session):
    """Test checking password for a non-existent user."""
    with pytest.raises(ValueError, match="User nonexistentuser not found"):
        User.check_password("nonexistentuser", "password")