from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# -------------------------
# DATABASE SETUP
# -------------------------
def init_db():
    conn = sqlite3.connect('shops.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            owner TEXT,
            category TEXT,
            location TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# -------------------------
# HOME PAGE (WITH FILTER)
# -------------------------
@app.route('/')
def index():
    category = request.args.get('category')

    conn = sqlite3.connect('shops.db')
    c = conn.cursor()

    if category:
        c.execute("SELECT * FROM shops WHERE category=?", (category,))
    else:
        c.execute("SELECT * FROM shops")

    shops = c.fetchall()
    conn.close()

    return render_template('index.html', shops=shops)

# -------------------------
# ADD SHOP
# -------------------------
@app.route('/add', methods=['GET', 'POST'])
def add_shop():
    if request.method == 'POST':
        name = request.form['name']
        owner = request.form['owner']
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
# DELETE SHOP
# -------------------------
@app.route('/delete/<int:id>')
def delete_shop(id):
    conn = sqlite3.connect('shops.db')
    c = conn.cursor()
    c.execute("DELETE FROM shops WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

# -------------------------
# EDIT SHOP
# -------------------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_shop(id):
    conn = sqlite3.connect('shops.db')
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        owner = request.form['owner']
        category = request.form['category']
        location = request.form['location']

        c.execute("""
            UPDATE shops 
            SET name=?, owner=?, category=?, location=? 
            WHERE id=?
        """, (name, owner, category, location, id))

        conn.commit()
        conn.close()
        return redirect('/')

    c.execute("SELECT * FROM shops WHERE id=?", (id,))
    shop = c.fetchone()
    conn.close()

    return render_template('edit_shop.html', shop=shop)

# -------------------------
# RUN APP
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)