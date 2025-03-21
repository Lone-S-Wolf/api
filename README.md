# FastAPI CRUD Application with Authentication

A simple CRUD application built with FastAPI, SQLite/PostgreSQL, and JWT authentication.

## Setup

1. Install dependencies:
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic pydantic python-jose[cryptography] passlib[bcrypt] python-multipart python-dotenv
```

2. Environment Configuration:
   - The application uses environment variables stored in a `.env` file
   - A sample `.env` file is provided with default values
   - For production, make sure to change the `SECRET_KEY` value

3. Database Configuration:
   - By default, the application uses SQLite for simplicity
   - To use PostgreSQL, update the `DATABASE_URL` in the `.env` file
   - For PostgreSQL, create a database:
     ```sql
     CREATE DATABASE fastapi_crud;
     ```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

5. Access the API documentation at: http://localhost:8000/docs

## Authentication

The API uses JWT token-based authentication:

1. Register a new user:
```bash
curl -X 'POST' \
  'http://localhost:8000/auth/register' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "user@example.com",
  "username": "testuser",
  "password": "password123"
}'
```

2. Get an access token:
```bash
curl -X 'POST' \
  'http://localhost:8000/auth/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=testuser&password=password123'
```

3. Use the token in subsequent requests:
```bash
curl -X 'GET' \
  'http://localhost:8000/items/' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

## API Endpoints

### Authentication
- `POST /auth/register`: Register a new user
- `POST /auth/token`: Login and get access token
- `GET /auth/users/me`: Get current user information

### Items (requires authentication)
- `GET /`: Welcome message
- `GET /items`: List all items
- `POST /items`: Create a new item
- `GET /items/{item_id}`: Get a specific item
- `PUT /items/{item_id}`: Update an item
- `DELETE /items/{item_id}`: Delete an item

## Example API Usage

### Create an item
```bash
curl -X 'POST' \
  'http://localhost:8000/items/' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "is_completed": false
}'
```

### List all items
```bash
curl -X 'GET' 'http://localhost:8000/items/' 