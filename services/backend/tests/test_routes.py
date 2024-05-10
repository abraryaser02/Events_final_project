import pytest
from sqlalchemy import text
from project import db

def client(app):
    """A test client for the Flask app."""
    return app.test_client()


def teardown_function():
    # Clear the database after each test
    with db.engine.connect() as connection:
        connection.execute(text("DELETE FROM users"))
        connection.execute(text("DELETE FROM events"))
        connection.execute(text("DELETE FROM user_to_events"))

def test_create_event(client):
    """Test the create_event endpoint."""
    sample_data = {
        'name': 'Sample Event',
        'description': 'This is a sample event description.',
        'location': 'Sample Location',
        'start_time': '2024-05-09 12:00:00',
        'end_time': '2024-05-09 15:00:00',
        'organization': 'Sample Organization',
        'contact_information': 'sample@example.com',
        'registration_link': 'https://example.com/register',
        'keywords': ['sample, event, testing']
    }

    # Simulate a POST request to the create_event endpoint with sample data
    response = client.post('/create_event', json=sample_data)

    # Check if the response status code is 200
    assert response.status_code == 200

    # Check if the response contains the expected message and event ID
    assert b'Event created successfully' in response.data
    assert b'eventID' in response.data

def test_get_event(client):
    response = client.get('/get_event/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Sample Event'

def test_login(client):
    response = client.post('/login', json={
        'email': 'newuser@example.com',
        'password': 'newpassword123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True

def test_logout(client):
    response = client.post('/logout')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'You have been logged out'



