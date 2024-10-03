import unittest
import json
import os
from dotenv import load_dotenv
from app import app, mysql
from flask_jwt_extended import create_access_token

load_dotenv()

class TestTodoAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        # Create tables for testing
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS users 
                           (id INT AUTO_INCREMENT PRIMARY KEY, 
                            name VARCHAR(100) NOT NULL, 
                            email VARCHAR(100) UNIQUE NOT NULL, 
                            password VARCHAR(255) NOT NULL)''')
            cur.execute('''CREATE TABLE IF NOT EXISTS todos 
                           (id INT AUTO_INCREMENT PRIMARY KEY, 
                            user_id INT NOT NULL, 
                            title VARCHAR(100) NOT NULL, 
                            description TEXT, 
                            FOREIGN KEY (user_id) REFERENCES users(id))''')
            mysql.connection.commit()
            cur.close()

    def tearDown(self):
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("DROP TABLE IF EXISTS todos")
            cur.execute("DROP TABLE IF EXISTS users")
            mysql.connection.commit()
            cur.close()
        self.app_context.pop()

    def test_register(self):
        response = self.app.post('/register',
                                 data=json.dumps({'name': 'Test User', 'email': 'test@example.com', 'password': 'password123'}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201, f"Expected 201, got {response.status_code}. Response: {response.data}")
        self.assertIn('token', json.loads(response.data))

    def test_login(self):
        # First register a user
        self.app.post('/register',
                      data=json.dumps({'name': 'Test User', 'email': 'test@example.com', 'password': 'password123'}),
                      content_type='application/json')
        
        # Then try to login
        response = self.app.post('/login',
                                 data=json.dumps({'email': 'test@example.com', 'password': 'password123'}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}. Response: {response.data}")
        self.assertIn('access_token', json.loads(response.data))

    def test_create_todo(self):
        try:
            # First register and login to get a token
            register_response = self.app.post('/register',
                          data=json.dumps({'name': 'Test User', 'email': 'test@example.com', 'password': 'password123'}),
                          content_type='application/json')
            print(f"Register response: {register_response.data}")
            
            login_response = self.app.post('/login',
                                           data=json.dumps({'email': 'test@example.com', 'password': 'password123'}),
                                           content_type='application/json')
            print(f"Login response: {login_response.data}")
            
            token = json.loads(login_response.data)['access_token']
            
            # Then create a todo
            response = self.app.post('/todos',
                                     data=json.dumps({'title': 'Test Todo', 'description': 'This is a test todo item'}),
                                     headers={'Authorization': f'Bearer {token}'},
                                     content_type='application/json')
            print(f"Create todo response: {response.data}")
            
            self.assertEqual(response.status_code, 201, f"Expected 201, got {response.status_code}. Response: {response.data}")
            self.assertIn('id', json.loads(response.data))
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise

    def test_update_todo(self):
        # Register, login, and create a todo
        self.app.post('/register',
                      data=json.dumps({'name': 'Test User', 'email': 'test@example.com', 'password': 'password123'}),
                      content_type='application/json')
        login_response = self.app.post('/login',
                                       data=json.dumps({'email': 'test@example.com', 'password': 'password123'}),
                                       content_type='application/json')
        token = json.loads(login_response.data)['access_token']
        create_response = self.app.post('/todos',
                                        data=json.dumps({'title': 'Test Todo', 'description': 'This is a test todo item'}),
                                        headers={'Authorization': f'Bearer {token}'},
                                        content_type='application/json')
        todo_id = json.loads(create_response.data)['id']
        
        # Update the todo
        update_response = self.app.put(f'/todos/{todo_id}',
                                       data=json.dumps({'title': 'Updated Todo', 'description': 'This is an updated todo item'}),
                                       headers={'Authorization': f'Bearer {token}'},
                                       content_type='application/json')
        self.assertEqual(update_response.status_code, 200)
        updated_todo = json.loads(update_response.data)
        self.assertEqual(updated_todo['title'], 'Updated Todo')
        self.assertEqual(updated_todo['description'], 'This is an updated todo item')

    def test_delete_todo(self):
        # Register, login, and create a todo
        self.app.post('/register',
                      data=json.dumps({'name': 'Test User', 'email': 'test@example.com', 'password': 'password123'}),
                      content_type='application/json')
        login_response = self.app.post('/login',
                                       data=json.dumps({'email': 'test@example.com', 'password': 'password123'}),
                                       content_type='application/json')
        token = json.loads(login_response.data)['access_token']
        create_response = self.app.post('/todos',
                                        data=json.dumps({'title': 'Test Todo', 'description': 'This is a test todo item'}),
                                        headers={'Authorization': f'Bearer {token}'},
                                        content_type='application/json')
        todo_id = json.loads(create_response.data)['id']
        
        # Delete the todo
        delete_response = self.app.delete(f'/todos/{todo_id}',
                                          headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(delete_response.status_code, 204)

    def test_get_todos(self):
        # Register, login, and create multiple todos
        self.app.post('/register',
                      data=json.dumps({'name': 'Test User', 'email': 'test@example.com', 'password': 'password123'}),
                      content_type='application/json')
        login_response = self.app.post('/login',
                                       data=json.dumps({'email': 'test@example.com', 'password': 'password123'}),
                                       content_type='application/json')
        token = json.loads(login_response.data)['access_token']
        for i in range(5):
            self.app.post('/todos',
                          data=json.dumps({'title': f'Todo {i}', 'description': f'Description {i}'}),
                          headers={'Authorization': f'Bearer {token}'},
                          content_type='application/json')
        
        # Get todos
        get_response = self.app.get('/todos',
                                    headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(get_response.status_code, 200)
        todos_data = json.loads(get_response.data)
        self.assertEqual(len(todos_data['data']), 5)
        self.assertEqual(todos_data['total'], 5)
        self.assertEqual(todos_data['page'], 1)
        self.assertEqual(todos_data['limit'], 10)

    def test_get_todos_with_pagination_and_search(self):
        # Register, login, and create multiple todos
        self.app.post('/register',
                      data=json.dumps({'name': 'Test User', 'email': 'test@example.com', 'password': 'password123'}),
                      content_type='application/json')
        login_response = self.app.post('/login',
                                       data=json.dumps({'email': 'test@example.com', 'password': 'password123'}),
                                       content_type='application/json')
        token = json.loads(login_response.data)['access_token']
        for i in range(15):
            self.app.post('/todos',
                          data=json.dumps({'title': f'Todo {i}', 'description': f'Description {i}'}),
                          headers={'Authorization': f'Bearer {token}'},
                          content_type='application/json')
        
        # Test pagination
        get_response = self.app.get('/todos?page=2&limit=5',
                                    headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(get_response.status_code, 200)
        todos_data = json.loads(get_response.data)
        self.assertEqual(len(todos_data['data']), 5)
        self.assertEqual(todos_data['total'], 15)
        self.assertEqual(todos_data['page'], 2)
        self.assertEqual(todos_data['limit'], 5)

        # Test search
        search_response = self.app.get('/todos?search=Todo 1',
                                       headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(search_response.status_code, 200)
        search_data = json.loads(search_response.data)
        self.assertGreater(len(search_data['data']), 0)
        self.assertLess(len(search_data['data']), 15)
        for todo in search_data['data']:
            self.assertIn('Todo 1', todo['title'])

if __name__ == '__main__':
    unittest.main()
