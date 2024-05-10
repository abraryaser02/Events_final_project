import os
import sys
import pytest
from sqlalchemy import text
from project import app, db

# Add the project directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Ensure environment variables are set correctly
os.environ['APP_SETTINGS'] = 'project.config.TestingConfig'
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5435/backend_dev'
os.environ['DATABASE_TEST_URL'] = 'postgresql://postgres:postgres@localhost:5435/backend_test'

print("APP_SETTINGS:", os.getenv('APP_SETTINGS'))
print("DATABASE_URL:", os.getenv('DATABASE_URL'))
print("DATABASE_TEST_URL:", os.getenv('DATABASE_TEST_URL'))

def apply_schema(engine):
    schema_path = os.path.join(os.path.dirname(__file__), '../../postgres/schema.sql')
    with engine.connect() as connection:
        with open(schema_path) as schema_file:
            schema_sql = schema_file.read()
            connection.execute(text(schema_sql))

@pytest.fixture(scope='session')
def test_app():
    app.config.from_object('project.config.TestingConfig')
    print("SQLALCHEMY_DATABASE_URI:", app.config['SQLALCHEMY_DATABASE_URI'])
    
    with app.app_context():
        db.create_all()  # Ensure the tables are created
        apply_schema(db.engine)  # Apply the schema from the schema.sql file
        yield app
        db.drop_all()  # Drop the tables after the test session

@pytest.fixture(scope='session')
def client(test_app):
    return test_app.test_client()

@pytest.fixture(scope='function')
def init_database():
    with app.app_context():
        with db.engine.connect() as connection:
            connection.execute(text("INSERT INTO users (email, password) VALUES ('testuser@example.com', 'password123')"))
            connection.execute(text("""
                INSERT INTO events (name, description, location, start_time, end_time, organization, contact_information, registration_link, keywords) 
                VALUES ('Test Event', 'This is a test event', 'Test Location', '2024-05-09T00:00:00', '2024-05-09T01:00:00', 'Test Org', 'contact@test.org', 'http://test.org/register', ARRAY['test'])
            """))
            yield
            connection.execute(text("DELETE FROM users"))
            connection.execute(text("DELETE FROM events"))
            connection.execute(text("DELETE FROM user_to_events"))
