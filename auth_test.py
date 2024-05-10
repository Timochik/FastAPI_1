from unittest import TestCase
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .main import ContactInDB, create_user, get_db, CreateUserRequest

# Assuming your models.py defines ContactInDB

class TestCreateUser(TestCase):
  def setUp(self):
    # Create a temporary engine for testing
    self.engine = create_engine('sqlite:///:memory:')
    # Create all tables based on models
    # (You might need to modify this line based on your model declaration)
    ContactInDB.Base.metadata.create_all(self.engine)
    self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

  def tearDown(self):
    # Drop all tables after each test
    ContactInDB.Base.metadata.drop_all(self.engine)

  def test_create_user_success(self):
    # Create a session
    db = self.SessionLocal()
    # Define user data
    user_data = CreateUserRequest(username="test_user", password="test_password")

    # Call the create_user function
    created_user = create_user(db, user_data)

    # Check if user is created successfully
    self.assertIsNotNone(created_user)
    # Check if username matches
    self.assertEqual(created_user.username, user_data.username)

    # Close the session
    db.close()

  def test_create_user_duplicate_username(self):
    # Create a session
    db = self.SessionLocal()
    # Define user data
    user_data = CreateUserRequest(username="test_user", password="test_password")

    # Create a user first
    create_user(db, user_data)

    # Try creating another user with the same username
    with self.assertRaises(Exception):  # Replace Exception with specific error type
      create_user(db, user_data)

    # Close the session
    db.close()


from unittest.mock import patch, MagicMock

# Use MagicMock for your tests here


from .main import authenticate_user, get_db

# Assuming your models.py defines ContactInDB

class TestAuthenticateUser(TestCase):
  def setUp(self):
    # Patch get_db function to avoid actual database interaction during tests
    self.get_db_patcher = patch('your_file.get_db')
    self.get_db_patcher.start()

  def tearDown(self):
    self.get_db_patcher.stop()

  def test_authenticate_user_success(self):
    # Mock the database session to return a valid user
    db_mock = MagicMock()
    user = ContactInDB(username="test_user", hashed_password="hashed_password")
    db_mock.query.return_value.first.return_value = user
    self.get_db_patcher.return_value = db_mock

    # Define user credentials
    username = "test_user"
    password = "valid_password"  # Assuming password is validated before hashing

    # Call the authenticate_user function
    authenticated_user = authenticate_user(username, password, db_mock)

    # Check if user is authenticated successfully
    self.assertIsNotNone(authenticated_user)
    self.assertEqual(authenticated_user.username, username)

  def test_authenticate_user_invalid_username(self):
    # Mock the database session to return None
    db_mock = MagicMock()
    db_mock.query.return_value.first.return_value = None
    self.get_db_patcher.return_value = db_mock

    # Define user credentials
    username = "invalid_user"
    password = "valid_password"

    # Call the authenticate_user function
    authenticated_user = authenticate_user(username, password, db_mock)

    # Check if user is not authenticated
    self.assertIsNone(authenticated_user)

  def test_authenticate_user_invalid_password(self):
    # Mock the database session to return a valid user
    db_mock = MagicMock()
    user = ContactInDB(username="test_user", hashed_password="hashed_password")
    db_mock.query.return_value.first.return_value = user
    self.get
