from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager,create_access_token, jwt_required, get_jwt_identity
from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', '')
jwt = JWTManager(app)

app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'blog_user')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '')  # This line reads the password
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'todo_api')

mysql = MySQL(app)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not all([data.get('name'), data.get('email'), data.get('password')]):
        return jsonify({"error": "Missing required fields"}), 400
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM todo_api WHERE email = %s", (data['email'],))
    if cur.fetchone():
        cur.close()
        return jsonify({"error": "Email already exists"}), 400
    
    cur.execute("INSERT INTO todo_api (name, email, password) VALUES (%s, %s, %s)",
                (data['name'], data['email'], generate_password_hash(data['password'])))
    mysql.connection.commit()
    user_id = cur.lastrowid
    cur.close()
    
    access_token = create_access_token(identity=user_id)
    return jsonify({"token": access_token}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not all([data['email'], data['password']]):
        return jsonify({"error": "Missing required fields"}), 400
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM todo_api WHERE email = %s", (data['email'],))
    user = cur.fetchone()
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({"error": "Invalid credentials"}), 401
    access_token = create_access_token(identity=user['id'])
    cur.close()
    return jsonify(access_token=access_token), 200

@jwt.unauthorized_loader
def unauthorized_response():
    return jsonify({"message": "Unauthorized"}), 401

@app.route('/todos', methods=['POST'])
@jwt_required()
def create_todo():
    # Get the new todo data from the request body
    data = request.json
    # Get the user id from the jwt token
    user_id = get_jwt_identity()
    
    # Validate required fields
    if not all([data.get('title'), data.get('description')]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Insert the new todo into the database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO todos (user_id, title, description) VALUES (%s, %s, %s)",
                (user_id, data['title'], data['description']))
    mysql.connection.commit()
    new_todo_id = cur.lastrowid
    cur.close()
    
    return jsonify({
        "id": new_todo_id,
        "title": data['title'],
        "description": data['description']
    }), 201


@app.route('/todos/<int:todo_id>', methods=['PUT'])
@jwt_required()
def update_todo(todo_id):
    user_id = get_jwt_identity()
    # get the updated todo data from the request body
    data =request.json
    if not any([data.get('title'), data.get('description')]):
        return jsonify({"error": "Missing required fields"}), 400
    
    cur = mysql.connection.cursor()
    cur.execute('select * from todos where id=%s', (todo_id,))
    todo = cur.fetchone()
    if not todo or todo['user_id'] != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    cur.execute('update todos set title=%s, description=%s where id=%s', (data['title'], data['description'], todo_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({
        "id":  todo_id,
        "title": data['title'],
        "description": data['description']
    }), 200

@app.route('todos/<int:todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    cur =mysql.connection.cursor()
    user_id = get_jwt_identity()
    cur.execute('select * from todos where id=%s', (todo_id,))
    todo = cur.fetchone()
    if not todo or todo['user_id'] != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    cur.execute('delete from todos where id=%s', (todo_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Todo deleted successfully'}), 204

@app.route('/todos', methods=['GET'])
@jwt_required()
def get_todos():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    search = request.args.get('search', '')
    
    # Ensure page and limit are positive
    page = max(1, page)
    limit = max(1, min(limit, 100))  # Cap limit at 100
    
    offset = (page - 1) * limit
    
    cur = mysql.connection.cursor()
    if search:
        cur.execute('SELECT * FROM todos WHERE user_id = %s AND (title LIKE %s OR description LIKE %s) ORDER BY id LIMIT %s OFFSET %s', 
                    (user_id, f'%{search}%', f'%{search}%', limit, offset))
    else:
        cur.execute('SELECT * FROM todos WHERE user_id = %s ORDER BY id LIMIT %s OFFSET %s', 
                    (user_id, limit, offset))
    todos = [{'id': row[0], 'title': row[1], 'description': row[2]} for row in cur.fetchall()]
    
    # Get total count
    if search:
        cur.execute('SELECT COUNT(*) FROM todos WHERE user_id = %s AND (title LIKE %s OR description LIKE %s)', 
                    (user_id, f'%{search}%', f'%{search}%'))
    else:
        cur.execute('SELECT COUNT(*) FROM todos WHERE user_id = %s', (user_id,))
    total = cur.fetchone()[0]
        
    cur.close()
    
    return jsonify({
        'data': todos,
        'page': page,
        'limit': limit,
        'total': total
    }), 200

if __name__ == '__main__':
    app.run(debug=True)

