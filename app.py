from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import sql

app = Flask(__name__)

# Настройка соединения с PostgreSQL
conn = psycopg2.connect(
    host="your_host",
    database="your_db",
    user="your_user",
    password="your_password"
)
cursor = conn.cursor()

@app.route('/add_client', methods=['POST'])
def add_client():
    try:
        # Получаем данные из запроса
        data = request.json
        phone = ''.join(filter(str.isdigit, data.get('phone', '')))
        description = data.get('description', '').strip()
        city = data.get('city', '').strip()

        # Проверяем, что все поля заполнены
        if not phone or not description or not city:
            return jsonify({"error": "Все поля должны быть заполнены"}), 400

        # Добавляем клиента в базу данных
        cursor.execute("INSERT INTO clients (phone, description, city) VALUES (%s, %s, %s)", (phone, description, city))
        conn.commit()

        # Успешный ответ
        return jsonify({"message": "Клиент добавлен успешно"}), 200
    
    except psycopg2.Error as e:
        conn.rollback()  # Откатываем изменения в случае ошибки
        return jsonify({"error": "Ошибка базы данных"}), 500
    
    except Exception as e:
        return jsonify({"error": "Неизвестная ошибка"}), 500

@app.route('/search_client', methods=['GET'])
def search_client():
    try:
        phone = request.args.get('phone', '').strip()

        # Проверка на пустой запрос
        if not phone:
            return jsonify([])

        # Поиск клиента по номеру телефона
        cursor.execute("SELECT date, phone, description, city FROM clients WHERE phone LIKE %s", (f"%{phone}%",))
        clients = cursor.fetchall()

        result = [{"date": row[0], "phone": row[1], "description": row[2], "city": row[3]} for row in clients]
        return jsonify(result)

    except psycopg2.Error as e:
        return jsonify({"error": "Ошибка базы данных"}), 500
    
    except Exception as e:
        return jsonify({"error": "Неизвестная ошибка"}), 500

if __name__ == '__main__':
    app.run(debug=True)