from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from datetime import date

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'secret123')

DB_PATH = 'shops.db'

# -------------------------
# DATABASE SETUP
# -------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Shops
    c.execute('''
        CREATE TABLE IF NOT EXISTS shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            owner TEXT,
            category TEXT,
            location TEXT
        )
    ''')

    # Users
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            role TEXT
        )
    ''')

    # Offers
    c.execute('''
        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            discount TEXT,
            start_date TEXT,
            end_date TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# -------------------------
# HOME (SHOW OFFERS + SHOPS)
# -------------------------
@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Shops
    c.execute("SELECT * FROM shops")
    shops = c.fetchall()

    # Active Offers
    today = str(date.today())

    c.execute("""
        SELECT * FROM offers
        WHERE start_date <= ? AND end_date >= ?
    """, (today, today))

    offers = c.fetchall()

    conn.close()

    return render_template(
        'index.html',
        shops=shops,
        offers=offers,
        role=session.get('role'),
        user=session.get('user')
    )

# -------------------------
# REGISTER
# -------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM users")
        count = c.fetchone()[0]

        role = "admin" if count == 0 else "user"

        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role)
        )

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

# -------------------------
# LOGIN
# -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = user[1]
            session['role'] = user[3]
            return redirect('/')
        else:
            return "Invalid Login"

    return render_template('login.html')

# -------------------------
# LOGOUT
# -------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# -------------------------
# ADD SHOP
# -------------------------
@app.route('/add', methods=['GET', 'POST'])
def add_shop():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        owner = session['user']
        category = request.form['category']
        location = request.form['location']

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute(
            "INSERT INTO shops (name, owner, category, location) VALUES (?, ?, ?, ?)",
            (name, owner, category, location)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add_shop.html')

# -------------------------
# ADD OFFER (ADMIN ONLY)
# -------------------------
@app.route('/add-offer', methods=['GET', 'POST'])
def add_offer():
    if session.get('role') != 'admin':
        return "Access Denied"

    if request.method == 'POST':
        title = request.form['title']
        discount = request.form['discount']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute(
            "INSERT INTO offers (title, discount, start_date, end_date) VALUES (?, ?, ?, ?)",
            (title, discount, start_date, end_date)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add_offer.html')

# -------------------------
# DELETE SHOP
# -------------------------
@app.route('/delete/<int:id>')
def delete_shop(id):
    if session.get('role') != 'admin':
        return "Access Denied"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM shops WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/')

# -------------------------
# RUN
# -------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)