# FastAPI Application Documentation

This document provides detailed information about each file in the application, explaining its purpose and functionality to help developers understand and maintain the codebase.

## Project Structure

```
├── app
│   ├── auth
│   │   ├── __init__.py
│   │   ├── rbac.py
│   │   └── utils.py
│   ├── database
│   │   ├── database.py
│   │   └── __init__.py
│   ├── __init__.py
│   ├── main.py
│   ├── models
│   │   ├── __init__.py
│   │   └── models.py
│   ├── routers
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── __init__.py
│   │   ├── items.py
│   │   ├── manager.py
│   │   ├── questions.py
│   │   ├── user.py
│   │   └── viewer.py
│   └── schemas
│       ├── __init__.py
│       └── schemas.py
├── README.md
├── requirements.txt
```

## Database

### database.py

This file sets up the database connection and session management:

- **Purpose**: Configure SQLAlchemy ORM connection to the database
- **Key Components**:
  - `SQLALCHEMY_DATABASE_URL`: Connection string from environment variables
  - `engine`: SQLAlchemy engine configured for the appropriate database
  - `SessionLocal`: Session factory for database operations
  - `Base`: Declarative base class for ORM models
  - `get_db`: Dependency function providing database sessions to routes

## Models

### models.py

Defines the database tables using SQLAlchemy ORM:

- **Purpose**: Define data models and their relationships
- **Models**:
  - `UserRole` (Enum): Defines user roles (ADMIN, MANAGER, USER, VIEWER)
  - `User`: User account information including authentication and authorization data
  - `Item`: Basic item model with title, description, and completion status
  - `Question`: Question model with title, content, answer, and active status

## Authentication

### utils.py

Handles user authentication and token management:

- **Purpose**: User authentication, password handling, and JWT token management
- **Key Functions**:
  - `verify_password`: Verify password against hashed version
  - `get_password_hash`: Hash a plaintext password
  - `authenticate_user`: Validate username/password credentials
  - `create_access_token`: Generate JWT token for authentication
  - `get_current_user`: Validate JWT token and retrieve user
  - `get_current_active_user`: Ensure user is active

### rbac.py

Implements Role-Based Access Control:

- **Purpose**: Control access to endpoints based on user roles
- **Key Functions**:
  - `check_user_role`: Validate user has required role
  - `get_admin_user`: Dependency to restrict access to admin users
  - `get_user_with_roles`: Factory to create role-specific dependencies

## Schemas

### schemas.py

Defines Pydantic models for request/response validation:

- **Purpose**: Validate request data, define response structures
- **Key Schemas**:
  - User schemas: `UserBase`, `UserCreate`, `UserResponse`
  - Authentication: `Token`, `TokenData`
  - Item schemas: `ItemBase`, `ItemCreate`, `ItemUpdate`, `Item`
  - Question schemas: `QuestionBase`, `QuestionCreate`, `QuestionUpdate`, `Question`

## Routers

### auth.py

Handles authentication endpoints:

- **Purpose**: User registration and login
- **Endpoints**:
  - `POST /auth/token`: Login to get access token
  - `POST /auth/register`: Register new user
  - `GET /auth/users/me`: Get current user information

### items.py

General item management:

- **Purpose**: Basic CRUD operations for items
- **Endpoints**:
  - `POST /items/`: Create new item
  - `GET /items/`: List all items
  - `GET /items/{item_id}`: Get specific item
  - `PUT /items/{item_id}`: Update item
  - `DELETE /items/{item_id}`: Delete item (admin only)

### admin.py

Admin-specific operations:

- **Purpose**: Administrative functions (restricted to admin role)
- **Endpoints**:
  - `GET /admin/users`: List all users
  - `GET /admin/users/by-role/{role}`: List users by role
  - `PUT /admin/users/{user_id}/toggle-active`: Enable/disable user
  - `PUT /admin/users/{user_id}/set-role`: Change user role
  - `DELETE /admin/items/all`: Delete all items
  - `DELETE /admin/items/{item_id}`: Delete specific item

### manager.py

Manager-specific operations:

- **Purpose**: Operations for manager role and above
- **Endpoints**:
  - `GET /manager/users`: List regular users
  - `GET /manager/items/stats`: Get item statistics
  - `POST /manager/items/bulk`: Bulk create items

### questions.py

Question management (manager role and above):

- **Purpose**: CRUD operations for questions
- **Endpoints**:
  - `POST /questions/`: Create new question
  - `GET /questions/`: List all questions
  - `GET /questions/{question_id}`: Get specific question
  - `PUT /questions/{question_id}`: Update question
  - `DELETE /questions/{question_id}`: Delete question (admin only)
  - `PUT /questions/{question_id}/toggle-active`: Toggle question active status

### user.py

Regular user operations:

- **Purpose**: User-specific item management
- **Endpoints**:
  - `POST /user/items`: Create user item
  - `PUT /user/items/{item_id}`: Update user item
  - `PUT /user/items/{item_id}/toggle-completion`: Toggle item completion

### viewer.py

Viewer-specific operations:

- **Purpose**: Read-only access to items
- **Endpoints**:
  - `GET /viewer/items`: View items
  - `GET /viewer/items/{item_id}`: View specific item
  - `GET /viewer/items/search`: Search items

## Main Application

### main.py

The application entry point:

- **Purpose**: Configure and launch the FastAPI application
- **Key Functions**:
  - Register all routers
  - Set up middleware (CORS, etc.)
  - Configure app metadata (title, version, etc.)

## Supporting Files

### **init**.py

Present in each directory:

- **Purpose**: Make directories importable packages

### requirements.txt

Lists all Python dependencies:

- **Purpose**: Specify project dependencies for installation
