# FastAPI CRUD Application with Advanced RBAC

A simple CRUD application built with FastAPI, SQLite/PostgreSQL, JWT authentication, and Advanced Role-Based Access Control (RBAC).

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

## Authentication and Authorization

### User Roles

The application supports four user roles with increasing levels of permissions:

1. **Viewer**: Read-only access to items
   - Can view and search items
   - Cannot create, update, or delete items

2. **User**: Basic item management
   - Can view, search, create, and update items
   - Can toggle item completion status
   - Cannot delete items

3. **Manager**: Enhanced management capabilities
   - All User permissions
   - Can view item statistics
   - Can create items in bulk
   - Can view regular and viewer users
   - Cannot manage other managers or admins

4. **Admin**: Full system access
   - All Manager permissions
   - Can manage all users (view, update roles, enable/disable)
   - Can delete items
   - Can perform all administrative functions

The first registered user is automatically assigned the admin role.

### Authentication

The API uses JWT token-based authentication:

1. Register a new user:
```bash
curl -X 'POST' \
  'http://localhost:8000/auth/register' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "user@example.com",
  "username": "testuser",
  "password": "password123",
  "role": "user"
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

### Items (General Endpoints)
- `GET /items`: List all items
- `POST /items`: Create a new item
- `GET /items/{item_id}`: Get a specific item
- `PUT /items/{item_id}`: Update an item
- `DELETE /items/{item_id}`: Delete an item (Admin only)

### Viewer Endpoints (All Roles)
- `GET /viewer/items`: View items with optional filtering
- `GET /viewer/items/{item_id}`: View a specific item
- `GET /viewer/items/search`: Search items by title or description

### User Endpoints (User, Manager, Admin)
- `POST /user/items`: Create a new item
- `PUT /user/items/{item_id}`: Update an item
- `PUT /user/items/{item_id}/toggle-completion`: Toggle item completion status

### Manager Endpoints (Manager, Admin)
- `GET /manager/users`: List regular and viewer users
- `GET /manager/items/stats`: Get statistics about items
- `POST /manager/items/bulk`: Create multiple items at once

### Admin Endpoints (Admin only)
- `GET /admin/users`: List all users
- `GET /admin/users/by-role/{role}`: List users by role
- `PUT /admin/users/{user_id}/toggle-active`: Enable/disable a user
- `PUT /admin/users/{user_id}/set-role`: Change a user's role
- `DELETE /admin/items/all`: Delete all items
- `DELETE /admin/items/{item_id}`: Delete a specific item

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