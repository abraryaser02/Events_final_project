# services/backend/project/__init__.py

import os
from datetime import datetime, timedelta
from random import choice
from flask import Flask, jsonify, request, make_response
from sqlalchemy import create_engine, text
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Database configuration

app.config.from_object(os.getenv('APP_SETTINGS', 'project.config.DevelopmentConfig'))
engine = create_engine(app.config['DATABASE_URI'])

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password required'}), 400

    query = text("SELECT id_users FROM users WHERE email = :email AND password = :password")
    with engine.connect() as connection:
        result = connection.execute(query, {'email': email, 'password': password})
        user = result.fetchone()

    if user:
        response = make_response(jsonify({'message': 'Login successful', 'userId': user['id_users']}))
        response.set_cookie('user_id', str(user['id_users']), httponly=True)
        return response
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password required'}), 400

    with engine.connect() as connection:
        existing_user = connection.execute(text("SELECT id_users FROM users WHERE email = :email"), {'email': email}).first()
        if existing_user:
            return jsonify({'message': 'User already exists'}), 409

        connection.execute(text("INSERT INTO users (email, password) VALUES (:email, :password)"), {'email': email, 'password': password})
        return jsonify({'message': 'User created successfully'}), 201

@app.route('/all_users', methods=['GET'])
def get_users():
    with engine.connect() as connection:
        users = connection.execute(text("SELECT * FROM users")).fetchall()
        users_list = [{'id': user['id_users'], 'email': user['email']} for user in users]
    return jsonify(users_list)

@app.route('/create_event', methods=['POST'])
def create_event():
    data = request.json
    with engine.connect() as connection:
        connection.execute(text("""
            INSERT INTO events (name, description, location, start_time, end_time, organization, contact_information, registration_link)
            VALUES (:name, :description, :location, :start_time, :end_time, :organization, :contact_information, :registration_link)
        """), data)
        return jsonify({'message': 'Event created successfully'}), 201

@app.route('/all_events', methods=['GET'])
def get_events():
    with engine.connect() as connection:
        events = connection.execute(text("SELECT * FROM events")).fetchall()
        events_list = [{'id': event['id_events'], 'name': event['name'], 'description': event['description']} for event in events]
    return jsonify(events_list)

@app.route('/get_event/<int:event_id>', methods=['GET'])
def get_event(event_id):
    with engine.connect() as connection:
        event = connection.execute(text("SELECT * FROM events WHERE id_events = :event_id"), {'event_id': event_id}).first()
        if event:
            return jsonify({
                'id': event['id_events'], 'name': event['name'], 'description': event['description'],
                'location': event['location'], 'start_time': event['start_time'], 'end_time': event['end_time'],
                'organization': event['organization'], 'contact_information': event['contact_information'],
                'registration_link': event['registration_link']
            })
        else:
            return jsonify({'message': 'Event not found'}), 404

@app.route('/delete_event/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM events WHERE id_events = :event_id"), {'event_id': event_id})
        return jsonify({'message': 'Event deleted successfully'}), 200

@app.route('/events_by_user/<int:user_id>', methods=['GET'])
def events_by_user(user_id):
    query = """
    SELECT e.id_events, e.name, e.description, e.location, e.start_time, e.end_time, 
           e.organization, e.contact_information
    FROM events e
    JOIN user_to_events ue ON ue.event_id = e.id_events
    WHERE ue.user_id = :user_id
    """
    with engine.connect() as connection:
        events = connection.execute(text(query), {'user_id': user_id}).fetchall()
        if not events:
            return jsonify({'message': 'No events or user not found'}), 404

        events_list = [{
            'id': event['id_events'],
            'name': event['name'],
            'description': event['description'],
            'location': event['location'],
            'start_time': event['start_time'].isoformat() if event['start_time'] else None,
            'end_time': event['end_time'].isoformat() if event['end_time'] else None,
            'organization': event['organization'],
            'contact_information': event['contact_information']
        } for event in events]

    return jsonify(events_list)

@app.route('/toggle_user_event', methods=['POST'])
def toggle_user_event():
    data = request.json
    user_id = data.get('user_id')
    event_id = data.get('event_id')

    if not user_id or not event_id:
        return jsonify({'message': 'Missing user_id or event_id'}), 400

    with engine.connect() as connection:
        # Check if both user and event exist
        user_exists = connection.execute(text("SELECT id_users FROM users WHERE id_users = :user_id"), {'user_id': user_id}).first()
        event_exists = connection.execute(text("SELECT id_events FROM events WHERE id_events = :event_id"), {'event_id': event_id}).first()

        if not user_exists or not event_exists:
            return jsonify({'message': 'User or event not found'}), 404

        # Check for existing association
        existing_association = connection.execute(text("""
            SELECT id_favorites FROM user_to_events
            WHERE user_id = :user_id AND event_id = :event_id
        """), {'user_id': user_id, 'event_id': event_id}).first()

        if existing_association:
            # Delete existing association
            connection.execute(text("DELETE FROM user_to_events WHERE id_favorites = :id"), {'id': existing_association['id_favorites']})
            return jsonify({'message': 'User removed from event successfully', 'isFavorited': False}), 200
        else:
            # Create new association
            connection.execute(text("""
                INSERT INTO user_to_events (user_id, event_id)
                VALUES (:user_id, :event_id)
            """), {'user_id': user_id, 'event_id': event_id})
            return jsonify({'message': 'User added to event successfully', 'isFavorited': True}), 201


if __name__ == '__main__':
    socketio.run(app, debug=True)

