from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("shops.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            owner TEXT,
            category TEXT,
            location TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------
@app.route("/")
def home():
    category = request.args.get("category")
    search = request.args.get("search")

    conn = sqlite3.connect("shops.db")
    c = conn.cursor()

    query = "SELECT * FROM shops WHERE 1=1"
    params = []

    if category and category != "All":
        query += " AND category=?"
        params.append(category)

    if search:
        query += " AND name LIKE ?"
        params.append("%" + search + "%")

    c.execute(query, params)
    shops = c.fetchall()
    conn.close()

    return render_template("index.html", shops=shops)

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            session["user"] = username
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# ---------------- ADD SHOP ----------------
@app.route("/add", methods=["GET", "POST"])
def add():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        owner = request.form["owner"]
        category = request.form["category"]
        location = request.form["location"]

        conn = sqlite3.connect("shops.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO shops (name, owner, category, location)
            VALUES (?, ?, ?, ?)
        """, (name, owner, category, location))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add.html")

# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def delete(id):
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("shops.db")
    c = conn.cursor()
    c.execute("DELETE FROM shops WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")

# ---------------- DEPLOYMENT ENTRY ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)