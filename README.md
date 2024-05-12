
# Events Final Project

This project is a scalable web application for managing and displaying events happening near you globally. It is built with a React frontend and a Python backend, and uses PostgreSQL for data storage. Docker is used to containerize the application for easy deployment and scalability.

## Project Structure

- **services/backend**: Contains the backend API built with Python.
- **services/client/my-app**: Contains the React frontend application.
- **postgres**: Contains the Dockerfile and SQL schema for the PostgreSQL database.

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Running the Application

1. **Clone the repository:**
    ```sh
    git clone <repository-url>
    cd Events_final_project_2
    ```

2. **Build and run the containers:**
    ```sh
    docker-compose -f docker-compose-dev.yml up --build
    ```

3. **Access the application:**
    - The frontend will be available at `http://localhost:3000`
    - The backend API will be available at `http://localhost:5001`

### Stopping the Application

To stop the running containers, use:

```sh
docker-compose -f docker-compose-dev.yml down
```

## Database Indexing and Scalability

### Indexes

Efficient indexing is crucial for optimizing query performance, especially when dealing with large datasets. This project leverages PostgreSQL's powerful indexing capabilities:

- **B-tree Indexes**: Used on primary keys, foreign keys, and other frequently queried columns. B-tree indexes are optimal for equality and range queries.
- **Full-text Search Indexes**: Implemented using PostgreSQL's `GIN` (Generalized Inverted Index) or `RUM` (Rum Universal Index) indexes to enable fast full-text searches on event descriptions and titles. This allows for efficient searching through large text fields.
- **Composite Indexes**: Created on multiple columns to support complex queries, ensuring that the database can quickly locate rows that match multiple criteria.
- **Partial Indexes**: Applied to subsets of data to optimize queries that frequently access a particular subset of rows.

### SQL Optimization and Scalability

The backend of this project utilizes SQLAlchemy Core for interacting with the PostgreSQL database. SQLAlchemy Core provides a high level of flexibility and performance by allowing the construction of complex SQL queries programmatically.
