import psycopg2
from psycopg2 import sql

# Настройки подключения
host = "pg-32b22183-py-api-test-db.c.aivencloud.com"  # замените на ваш хост
port = 12811  # стандартный порт PostgreSQL
dbname = "defaultdb"  # имя базы данных
user = "avnadmin"  # имя пользователя
password = "AVNS_h1CF9J3jlqE_axHiUEf"  # пароль

# Устанавливаем подключение к базе данных
conn = psycopg2.connect(
    host=host,
    port=port,
    dbname=dbname,
    user=user,
    password=password
)

# Создаем курсор
cursor = conn.cursor()

# Пример создания таблицы (если еще не создана)
create_table_query = '''
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    age INT
);
'''

cursor.execute(create_table_query)
conn.commit()

# Пример вставки данных в таблицу
insert_query = '''
INSERT INTO users (name, age) 
VALUES (%s, %s)
'''

# Данные для добавления
data = [
    ('Alice', 30),
    ('Bob', 25),
    ('Charlie', 35)
]

# Добавление данных
cursor.executemany(insert_query, data)
conn.commit()

# Закрываем курсор и соединение
cursor.close()
conn.close()

print("Данные успешно добавлены!")