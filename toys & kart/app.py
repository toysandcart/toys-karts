from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "toys_and_karts_secret"

DB_NAME = "store.db"
UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# ---------- DATABASE INIT ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price TEXT,
            category TEXT,
            image TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("home.html")

# ---------- ADMIN LOGIN ----------
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USERNAME and request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin/dashboard")
        return "Invalid login"
    return render_template("admin_login.html")

# ---------- ADMIN DASHBOARD ----------
@app.route("/admin/dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        category = request.form["category"]
        image = request.files["image"]

        if image:
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], image.filename))

        c.execute(
            "INSERT INTO products (name, price, category, image) VALUES (?, ?, ?, ?)",
            (name, price, category, image.filename)
        )
        conn.commit()

    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()

    return render_template("admin_dashboard.html", products=products)

# ---------- CATEGORY PAGE ----------
@app.route("/category/<cat>")
def category(cat):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name, price, image FROM products WHERE category=?", (cat,))
    items = c.fetchall()
    conn.close()

    return render_template("category.html", items=items, category=cat)

# ---------- LOGOUT ----------
@app.route("/admin/logout")
def logout():
    session.pop("admin", None)
    return redirect("/admin")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

