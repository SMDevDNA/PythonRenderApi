from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import sql

app = Flask(__name__)

# Настройки подключения
host = "pg-32b22183-py-api-test-db.c.aivencloud.com"  # замените на ваш хост
port = 12811  # стандартный порт PostgreSQL
dbname = "defaultdb"  # имя базы данных
user = "avnadmin"  # имя пользователя
password = "AVNS_h1CF9J3jlqE_axHiUEf"  # пароль

# Функция для подключения к базе данных
def get_db_connection():
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    return conn

# Стартовое создание таблицы (если она не существует)
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

# Создаём таблицу при запуске приложения
create_table()

# API для получения всех пользователей
@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

# API для добавления нового пользователя
@app.route('/users', methods=['POST'])
def add_user():
    # Получаем данные из запроса
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')

    if not name or not age:
        return jsonify({"error": "Name and age are required"}), 400

    # Подключаемся к базе данных
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

if __name__ == '__main__':
    app.run(debug=True)