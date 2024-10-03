import MySQLdb
from dotenv import load_dotenv
import os

load_dotenv()

try:
    connection = MySQLdb.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        passwd=os.getenv('MYSQL_PASSWORD'),
        db=os.getenv('MYSQL_DB')
    )
    print("Successfully connected to the database!")
    cursor = connection.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"Database version: {version[0]}")
    connection.close()
except MySQLdb.Error as e:
    print(f"Error connecting to MySQL: {e}")
