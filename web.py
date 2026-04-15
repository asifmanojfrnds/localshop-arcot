from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret123'

# -------------------------
# DATABASE SETUP
# -------------------------
def init_db():
    conn = sqlite3.connect('shops.db')
    c = conn.cursor()

    # Shops table
    c.execute('''
        CREATE TABLE IF NOT EXISTS shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            owner TEXT,
            category TEXT,
            location TEXT
        )
    ''')

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            role TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# -------------------------
# HOME
# -------------------------
@app.route('/')
def index():
    conn = sqlite3.connect('shops.db')
    c = conn.cursor()
    c.execute("SELECT * FROM shops")
    shops = c.fetchall()
    conn.close()

    return render_template(
        'index.html',
        shops=shops,
        role=session.get('role'),
        user=session.get('user')
    )

# -------------------------
# REGISTER (AUTO ADMIN)
# -------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('shops.db')
        c = conn.cursor()

        # Check if any user exists
        c.execute("SELECT COUNT(*) FROM users")
        count = c.fetchone()[0]

        # First user becomes admin
        if count == 0:
            role = 'admin'
        else:
            role = 'user'

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

        conn = sqlite3.connect('shops.db')
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
# ADD SHOP (USER LOGIN REQUIRED)
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

        conn = sqlite3.connect('shops.db')
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
# DELETE (ADMIN ONLY)
# -------------------------
@app.route('/delete/<int:id>')
def delete_shop(id):
    if session.get('role') != 'admin':
        return "Access Denied"

    conn = sqlite3.connect('shops.db')
    c = conn.cursor()
    c.execute("DELETE FROM shops WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/')

# -------------------------
# EDIT (ADMIN ONLY)
# -------------------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_shop(id):
    if session.get('role') != 'admin':
        return "Access Denied"

    conn = sqlite3.connect('shops.db')
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        owner = request.form['owner']
        category = request.form['category']
        location = request.form['location']

        c.execute(
            "UPDATE shops SET name=?, owner=?, category=?, location=? WHERE id=?",
            (name, owner, category, location, id)
        )
        conn.commit()
        conn.close()
        return redirect('/')

    c.execute("SELECT * FROM shops WHERE id=?", (id,))
    shop = c.fetchone()
    conn.close()

    return render_template('edit_shop.html', shop=shop)

# -------------------------
# RUN
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)
