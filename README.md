# Todo List API

## Project Overview
This project is a RESTful API that allows users to manage their to-do lists. It provides a set of endpoints for user authentication and CRUD operations on todo items.

## Features
- User registration and login
- JWT-based authentication
- Create, read, update, and delete todo items
- Search and pagination for todo items

## Technology Stack
- Python
- Flask (Web framework)
- MySQL (Database)
- Flask-JWT-Extended (JWT authentication)
- Flask-MySQLdb (MySQL database integration)
- Werkzeug (Password hashing)

## API Endpoints

### Authentication
- POST /register: Register a new user
- POST /login: Authenticate a user and receive a JWT token

### Todo Operations
- POST /todos: Create a new todo item
- GET /todos: Retrieve all todo items for the authenticated user (with pagination and search)
- PUT /todos/<todo_id>: Update a specific todo item
- DELETE /todos/<todo_id>: Delete a specific todo item

## Setup and Installation
1. Clone the repository
2. Install the required dependencies: `pip install -r requirements.txt`
3. Set up a MySQL database
4. Create a `.env` file with the following variables:
   ```
   MYSQL_HOST=your_mysql_host
   MYSQL_USER=your_mysql_user
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DB=your_database_name
   JWT_SECRET_KEY=your_jwt_secret_key
   ```
5. Run the application: `python app.py`

## Usage
1. Register a new user using the /register endpoint
2. Login with the registered user to receive a JWT token
3. Use the JWT token in the Authorization header for subsequent requests
4. Perform CRUD operations on todo items using the provided endpoints

## Security Considerations
- Passwords are hashed before storing in the database
- JWT tokens are used for authentication
- Environment variables are used for sensitive information

## Future Improvements
- Implement refresh tokens for enhanced security
- Add user profile management
- Implement task categories or labels
- Add due dates and reminders for todo items



Source: [Todo List API Project](https://roadmap.sh/projects/todo-list-api)