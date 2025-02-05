import os
import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

# Подключение к базе данных через переменные окружения
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT', '5432'),  # Устанавливаем порт по умолчанию 5432
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

# Пример маршрута для добавления клиента
@app.route('/add_client', methods=['POST'])
def add_client():
    data = request.json
    phone = data.get('phone')
    description = data.get('description')
    city = data.get('city')

    if not phone or not description or not city:
        return jsonify({"error": "Все поля обязательны для заполнения"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Не удалось подключиться к базе данных"}), 500

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO clients (phone, description, city) VALUES (%s, %s, %s)",
                (phone, description, city)
            )
            conn.commit()
        return jsonify({"message": "Клиент успешно добавлен"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# Пример маршрута для поиска клиента
@app.route('/search_client', methods=['GET'])
def search_client():
    phone = request.args.get('phone')

    if not phone:
        return jsonify({"error": "Номер телефона обязателен для поиска"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Не удалось подключиться к базе данных"}), 500

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT date, phone, description, city FROM clients WHERE phone = %s", (phone,))
            clients = cur.fetchall()

            if not clients:
                return jsonify({"message": "Клиенты не найдены"}), 404

            result = [
                {"date": client[0], "phone": client[1], "description": client[2], "city": client[3]}
                for client in clients
            ]
            return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)