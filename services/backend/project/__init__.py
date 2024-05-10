# services/backend/project/__init__.py

import os
from datetime import datetime, timedelta
from random import choice
from flask import Flask, jsonify, request, make_response, session, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Database configuration

app.config.from_object(os.getenv('APP_SETTINGS', 'project.config.DevelopmentConfig'))
engine = create_engine(app.config['DATABASE_URI'])

db = SQLAlchemy(app)

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
        response = make_response(jsonify({'message': 'Login successful', 'userId': user.id_users}))
        response.set_cookie('user_id', str(user.id_users), httponly=True)  
        return jsonify({'success': True, 'message': 'Login successful', 'userId': user.id_users, 'email': email})
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    
@app.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({'message': 'You have been logged out'}))
    response.delete_cookie('user_id') 
    return response


@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'email or password missing'}), 400

    with engine.connect() as connection:
        existing_user = connection.execute(text("SELECT id_users FROM users WHERE email = :email"), {'email': email}).first()
        if existing_user:
            return jsonify({'message': 'User already exists'}), 409

        # Insert the new user
        connection.execute(text("INSERT INTO users (email, password) VALUES (:email, :password)"), {'email': email, 'password': password})
        connection.commit()  

        # Fetch the new user to confirm insertion
        new_user = connection.execute(text("SELECT id_users FROM users WHERE email = :email"), {'email': email}).first()
        if new_user:
            response = make_response(jsonify({'message': 'User created successfully', 'userId': new_user.id_users}))
            response.set_cookie('user_id', str(new_user.id_users), httponly=True)
            return jsonify({'message': 'User created successfully'}), 201
        else:
            return jsonify({'message': 'Failed to create user', 'details': 'Failed to create user'}), 500
    

@app.route('/all_users', methods=['GET'])
def get_users():
    with engine.connect() as connection:
        users = connection.execute(text("SELECT id_users, email FROM users")).fetchall()
        users_list = [{'id_users': user.id_users, 'email': user.email} for user in users]
        return jsonify(users_list)


#get user by id
@app.route('/get_user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    with engine.connect() as connection:
        user = connection.execute(text('SELECT * FROM user WHERE id_users=:user_id'), {'user_id': user_id}).first()
        if user is None:
            return jsonify({'message': 'User not found'}), 404
        user_data = {
            'id_users': user.id_users,
            'email': user.email,
            'password': user.password
        }
    return jsonify(user_data)


@app.route('/create_event', methods=['POST'])
def create_event():
    data = request.get_json()

    sql = """
        INSERT INTO events 
            (name, description, location, start_time, end_time, organization, 
             contact_information, registration_link, keywords, tsv)
        VALUES 
            (:name, :description, :location, :start_time, :end_time, :organization, 
             :contact_information, :registration_link, :keywords, to_tsvector('english', :name || ' ' || :description))
        RETURNING id_events;
    """
    
    try:
        with engine.connect() as connection:
            # Execute the insert statement and fetch the newly created event ID
            result = connection.execute(text(sql), {
                'name': data['name'],
                'description': data['description'],
                'location': data['location'],
                'start_time': data['start_time'],
                'end_time': data['end_time'],
                'organization': data['organization'],
                'contact_information': data['contact_information'],
                'registration_link': data['registration_link'],
                'keywords': data['keywords']
            })
            connection.commit()
            new_event_id = result.fetchone()[0]
            return jsonify({'message': 'Event created successfully', 'eventID': new_event_id}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to create event', 'details': str(e)}), 500


@app.route('/all_events', methods=['GET'])
def get_events():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page

    with engine.connect() as connection:
        current_time = datetime.utcnow()
        events = connection.execute(text("""
            SELECT * FROM events 
            WHERE start_time >= :current_time 
            ORDER BY start_time 
            LIMIT :per_page OFFSET :offset
        """), {'current_time': current_time, 'per_page': per_page, 'offset': offset}).fetchall()
        
        events_list = [{'id': event.id_events,
                        'name': event.name,
                        'description': event.description,
                        'location': event.location,
                        'start_time': event.start_time,
                        'end_time': event.end_time,
                        'organization': event.organization,
                        'contact_information': event.contact_information,
                        'registration_link': event.registration_link,
                        'keywords': event.keywords} for event in events]
    return jsonify(events_list)


@app.route('/get_event/<int:event_id>', methods=['GET'])
def get_event(event_id):
    with engine.connect() as connection:
        event = connection.execute(text("SELECT * FROM events WHERE id_events = :event_id"), {'event_id': event_id}).first()
        if event:
            return jsonify({
                'id': event.id_events, 
                'name': event.name, 
                'description': event.description,
                'location': event.location, 
                'start_time': event.start_time, 
                'end_time': event.end_time,
                'organization': event.organization, 
                'contact_information': event.contact_information,
                'registration_link': event.registration_link,
                'keywords': event.keywords
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
           e.organization, e.contact_information, e.registration_link, e.keywords
    FROM events e
    JOIN user_to_events ue ON ue.event_id = e.id_events
    WHERE ue.user_id = :user_id
    """
    with engine.connect() as connection:
        events = connection.execute(text(query), {'user_id': user_id}).fetchall()
        if not events:
            return jsonify({'message': 'User not found'}), 404

        events_list = [{'id': event.id_events, 
                        'name': event.name, 
                        'description': event.description,
                        'location': event.location, 
                        'start_time': event.start_time, 
                        'end_time': event.end_time,
                        'organization': event.organization, 
                        'contact_information': event.contact_information,
                        'registration_link': event.registration_link,
                        'keywords': event.keywords
                    } for event in events]

    return jsonify(events_list)


@app.route('/events_by_favorites', methods=['GET'])
def get_top_favorited_events():
    try:
        # SQL query to select the top 10 most favorited events
        query = """
            SELECT e.id_events, e.name, e.description, e.location, e.start_time, e.end_time, 
                   e.organization, e.contact_information, e.registration_link, e.keywords,
                   COUNT(ue.event_id) AS likes
            FROM events e
            LEFT JOIN user_to_events ue ON e.id_events = ue.event_id
            GROUP BY e.id_events
            ORDER BY likes DESC
            LIMIT 10
        """
        with engine.connect() as connection:
            # Execute the SQL query
            events = connection.execute(text(query)).fetchall()
            if not events:
                return jsonify({'message': 'No events found'}), 404

            # Convert the result to a list of dictionaries for JSON serialization
            events_list = [{'id': event.id_events, 
                            'name': event.name, 
                            'description': event.description,
                            'location': event.location, 
                            'start_time': event.start_time, 
                            'end_time': event.end_time,
                            'organization': event.organization, 
                            'contact_information': event.contact_information,
                            'registration_link': event.registration_link,
                            'keywords': event.keywords,
                            'favorites': event.likes
                        } for event in events]

        return jsonify(events_list)
    except Exception as e:
        # Handle exceptions gracefully
        return jsonify({'error': str(e)}), 500


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
            connection.execute(text("DELETE FROM user_to_events WHERE id_favorites = :id"), {'id': existing_association.id_favorites})
            connection.commit()
            return jsonify({'message': 'User removed from event successfully', 'isFavorited': False}), 200
        else:
            # Create new association
            connection.execute(text("""
                INSERT INTO user_to_events (user_id, event_id)
                VALUES (:user_id, :event_id)
            """), {'user_id': user_id, 'event_id': event_id})
            connection.commit()
            return jsonify({'message': 'User added to event successfully', 'isFavorited': True}), 201
        
    # @app.route(get favorites by event)
    # view friends on about page 

    # most recent messages view, prev next toggle buttons

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page

    with engine.connect() as connection:
        if query:
            # FTS query
            search_query = text("""
                SELECT id_events, 
                       ts_headline('english', name, plainto_tsquery(:query)) AS name,
                       ts_headline('english', description, plainto_tsquery(:query)) AS description,
                       location, start_time, end_time, organization, contact_information, 
                       registration_link, keywords
                FROM events 
                WHERE to_tsvector('english', name || ' ' || description) @@ plainto_tsquery(:query)
                ORDER BY ts_rank(to_tsvector('english', name || ' ' || description), plainto_tsquery(:query)) DESC
                LIMIT :per_page OFFSET :offset;
            """)
            events = connection.execute(search_query, {'query': query, 'per_page': per_page, 'offset': offset}).fetchall()
            
            # Spelling suggestion query
            suggestions_query = text("""
                SELECT suggestion FROM get_spelling_suggestions(:query);
            """)
            suggestions = connection.execute(suggestions_query, {'query': query}).fetchall()
        else:
            # If query is empty, return all events
            events_query = text("""
                SELECT id_events, name, description, location, start_time, end_time, organization, contact_information, 
                       registration_link, keywords
                FROM events
                ORDER BY start_time
                LIMIT :per_page OFFSET :offset;
            """)
            events = connection.execute(events_query, {'per_page': per_page, 'offset': offset}).fetchall()
            suggestions = []

    events_list = [{'id': event.id_events, 'name': event.name, 'description': event.description,
                    'location': event.location, 'start_time': event.start_time, 'end_time': event.end_time,
                    'organization': event.organization, 'contact_information': event.contact_information,
                    'registration_link': event.registration_link, 'keywords': event.keywords} 
                   for event in events]
    suggestions_list = [suggestion.suggestion for suggestion in suggestions]

    return jsonify({'events': events_list, 'suggestions': suggestions_list})
    


if __name__ == '__main__':
    socketio.run(app, debug=True)

