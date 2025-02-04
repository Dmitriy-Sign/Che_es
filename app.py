from flask import Flask, request, render_template
import sqlite3
import re
from datetime import datetime

app = Flask(__name__)
DB_FILE = "blacklist.db"

# Инициализация базы данных
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                phone TEXT,
                description TEXT,
                city TEXT
            )
        """)
    conn.close()

# Основной маршрут
@app.route("/", methods=["GET", "POST"])
def index():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if request.method == "POST":
        # Очистка номера телефона от лишних символов
        phone = re.sub(r"[^0-9+]", "", request.form.get("phone", ""))
        description = request.form.get("description", "")[:50]
        city = request.form.get("city", "")
        date = datetime.now().strftime("%d.%m.%y")

        # Вставка новой записи
        cursor.execute(
            "INSERT INTO blacklist (date, phone, description, city) VALUES (?, ?, ?, ?)",
            (date, phone, description, city)
        )
        conn.commit()

    # Поиск в базе данных
    search_query = request.args.get("search", "")
    if search_query:
        cursor.execute("SELECT id, date, phone, description, city FROM blacklist WHERE phone LIKE ?", (f"%{search_query}%",))
    else:
        cursor.execute("SELECT id, date, phone, description, city FROM blacklist")

    results = cursor.fetchall()
    conn.close()
    return render_template("index.html", results=results)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
