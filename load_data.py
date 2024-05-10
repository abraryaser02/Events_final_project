#!/usr/bin/python3

import argparse
import sqlalchemy
from sqlalchemy.dialects.postgresql import insert
from faker import Faker
import random
from tqdm import tqdm
import time
from datetime import datetime, timedelta

fake = Faker()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', required=True)
    parser.add_argument('--event_rows', default=1000000, type=int)
    parser.add_argument('--user_rows', default=1000000, type=int)
    return parser.parse_args()

def connect_database(db_url):
    engine = sqlalchemy.create_engine(db_url, echo=False)
    return engine

# Load words from the English dictionary file
def load_dictionary(file_path='./services/postgres/words_alpha.txt'):
    with open(file_path, 'r') as file:
        words = file.read().splitlines()
    return words

dictionary_words = load_dictionary()

def generate_event_name(event_type):
    thematic_words = {
        "Talk": ["Lecture", "Discussion", "Seminar", "Panel"],
        "Festival": ["Gala", "Fest", "Celebration"],
        "Awards Ceremony": ["Awards Night", "Recognition Gala", "Honors Evening"]
    }
    word = random.choice(thematic_words.get(event_type, ["Event"]))
    return f"{fake.bs().title()} {word}"

def generate_event_description(event_name):
    # Select random words from the dictionary to create a longer description
    random_words = ' '.join(random.choices(dictionary_words, k=20))
    contexts = [
        f"Join us for the {event_name}, an opportunity to engage with leading experts and enthusiasts from the industry. {random_words}",
        f"This year's {event_name} features a series of immersive experiences designed to inspire and educate attendees. {random_words}",
        f"Don't miss out on the {event_name}! It will be a gathering of minds and ideas that promises to be unforgettable. {random_words}"
    ]
    return random.choice(contexts)

def generate_future_datetime():
    time_ranges = [
        ('next week', 7),
        ('next two weeks', 14),
        ('next month', 30),
        ('within the next three months', 90),
        ('within the next six months', 180)
    ]
    description, days = random.choice(time_ranges)
    return fake.future_datetime(end_date=f"+{days}d")

def insert_events(connection, num_events):
    event_types = [
        "Talk", "Awards Ceremony", "Info Session", "Gala", "Screening",
        "Colloquium", "Radio Play", "Class", "Lecture", "Festival"
    ]
    keywords = [
        "academics and graduate school", "networking and career development", "workshops and seminars",
        "volunteering and fundraising", "affinity groups and cultural events", "activism and social justice", "athletics",
        "wellness", "recreation and nightlife", "clubs and organizations", "science and technology", "arts and theater",
        "food and snacks", "pre-professional events", "sustainability"
    ]
    sql = sqlalchemy.sql.text("""
    INSERT INTO events (name, description, location, start_time, end_time, organization, contact_information, registration_link, keywords, tsv)
    VALUES (:name, :description, :location, :start_time, :end_time, :organization, :contact_information, :registration_link, :keywords, to_tsvector('english', :name || ' ' || :description))
    RETURNING id_events;
    """)
    event_ids = []
    for _ in tqdm(range(num_events), desc="Inserting events"):
        event_type = random.choice(event_types)
        event_name = generate_event_name(event_type)
        description = generate_event_description(event_name)
        start_time = generate_future_datetime()
        end_time = start_time + timedelta(hours=random.choice([1, 2, 3, 4, 5, 6]))
        event_keywords = random.sample(keywords, k=random.randint(1, 5))  # Select 1-5 random keywords
        event = {
            'name': event_name,
            'description': description,
            'location': fake.address(),
            'start_time': start_time,
            'end_time': end_time,
            'organization': fake.company(),
            'contact_information': fake.phone_number(),
            'registration_link': fake.url(),
            'keywords': event_keywords
        }
        try:
            result = connection.execute(sql, event)
            event_id = result.fetchone()[0]
            event_ids.append(event_id)
        except sqlalchemy.exc.IntegrityError as e:
            print(f"Failed to insert event: {e}")
    return event_ids

def generate_users(connection, num_users):
    sql = sqlalchemy.sql.text("""
    INSERT INTO users (email, password)
    VALUES (:email, :password)
    RETURNING id_users;
    """)
    user_ids = []
    for _ in tqdm(range(num_users), desc="Inserting users"):
        user = {
            'email': fake.email(),
            'password': fake.password()
        }
        try:
            result = connection.execute(sql, user)
            user_id = result.fetchone()[0]
            user_ids.append(user_id)
        except sqlalchemy.exc.IntegrityError as e:
            print(f"Failed to insert user: {e}")
    return user_ids

def insert_user_to_events(connection, user_ids, event_ids):
    sql = sqlalchemy.sql.text("""
    INSERT INTO user_to_events (user_id, event_id)
    VALUES (:user_id, :event_id);
    """)
    num_users = len(user_ids)
    num_events = len(event_ids)
    popular_event_ids = random.choices(event_ids, k=int(num_events * 0.1))  # 10% of events are way more favorited
    for user_id in tqdm(user_ids, desc="Inserting user_to_events"):
        # Each user favorites 10 events
        favorite_event_ids = random.sample(event_ids, k=5) + random.sample(popular_event_ids, k=5)
        for event_id in favorite_event_ids:
            try:
                connection.execute(sql, {'user_id': user_id, 'event_id': event_id})
            except sqlalchemy.exc.IntegrityError as e:
                print(f"Failed to insert user_to_event: {e}")

def insert_data(engine, num_events, num_users):
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            event_ids = insert_events(connection, num_events)
            user_ids = generate_users(connection, num_users)
            insert_user_to_events(connection, user_ids, event_ids)
            transaction.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            transaction.rollback()
        finally:
            connection.close()

def main():
    args = parse_args()
    engine = connect_database(args.db)
    start_time = time.time()

    insert_data(engine, args.event_rows, args.user_rows)

    end_time = time.time()
    print('Runtime =', end_time - start_time)

if __name__ == "__main__":
    main()
