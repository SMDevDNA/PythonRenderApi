from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import sql

app = Flask(__name__)

# Настройки подключения


from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import sql
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'testKey'
jwt = JWTManager(app)

host = "pg-32b22183-py-api-test-db.c.aivencloud.com"
port = 12811
dbname = "defaultdb"
user = "avnadmin"
password = "AVNS_h1CF9J3jlqE_axHiUEf"

def get_db_connection():
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    return conn

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        age INT
    );
    '''
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()

create_table()

@app.route('/users', methods=['GET'])
@jwt_required()  # Требуется авторизация
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

@app.route('/users', methods=['POST'])
@jwt_required()  # Требуется авторизация
def add_user():
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')

    if not name or not age:
        return jsonify({"error": "Name and age are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    insert_query = '''
    INSERT INTO users (name, age) 
    VALUES (%s, %s)
    RETURNING id;
    '''
    cursor.execute(insert_query, (name, age))
    user_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"id": user_id, "name": name, "age": age}), 201

@app.route('/users/<int:id>', methods=['PUT'])
@jwt_required()  # Требуется авторизация
def update_user(id):
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')

    if not name or not age:
        return jsonify({"error": "Name and age are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    update_query = '''
    UPDATE users SET name = %s, age = %s WHERE id = %s;
    '''
    cursor.execute(update_query, (name, age, id))
    conn.commit()

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404

    cursor.close()
    conn.close()
    return jsonify({"id": id, "name": name, "age": age})

@app.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()  # Требуется авторизация
def delete_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    delete_query = '''
    DELETE FROM users WHERE id = %s;
    '''
    cursor.execute(delete_query, (id,))
    conn.commit()

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404

    cursor.close()
    conn.close()
    return jsonify({"message": "User deleted successfully"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == 'admin' and password == 'password':
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(debug=True)