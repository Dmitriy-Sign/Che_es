from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2 import sql
import os

app = Flask(__name__)

# Подключение к PostgreSQL
DATABASE_URL = "postgresql://blacklist_psql_user:l0XVhvf8TfCbiCz6lL87sMlJhV7filiY@dpg-cuhi6mt2ng1s738717d0-a/blacklist_psql"
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Создание таблицы, если её нет
cursor.execute('''
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(15) NOT NULL,
    description TEXT NOT NULL,
    city VARCHAR(50) NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')
conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_client():
    data = request.json
    phone = ''.join(filter(str.isdigit, data.get('phone', '')))
    description = data.get('description', '').strip()
    city = data.get('city', '').strip()
    
    if not phone or not description or not city:
        return jsonify({"error": "Все поля должны быть заполнены"}), 400
    
    cursor.execute("INSERT INTO clients (phone, description, city) VALUES (%s, %s, %s)", (phone, description, city))
    conn.commit()
    
    return jsonify({"message": "Клиент добавлен успешно"})

@app.route('/search', methods=['GET'])
def search_client():
    query = request.args.get('query', '')
    query = ''.join(filter(str.isdigit, query))
    
    cursor.execute("SELECT date, phone, description, city FROM clients WHERE phone LIKE %s", (f"%{query}%",))
    results = cursor.fetchall()
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
