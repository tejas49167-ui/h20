from datetime import datetime
import sqlite3
from flask import Flask, g, redirect, render_template, request, session, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key"
DATABASE = "chat.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )
    db.commit()


@app.before_request
def ensure_db_initialized():
    init_db()


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None

    db = get_db()
    return db.execute("SELECT id, username FROM users WHERE id = ?", (user_id,)).fetchone()


@app.route("/")
def home():
    if current_user() is None:
        return redirect(url_for("login"))
    return redirect(url_for("chat_room"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        if len(username) < 3:
            flash("Username must be at least 3 characters.")
            return render_template("register.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.")
            return render_template("register.html")

        db = get_db()
        existing_user = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if existing_user:
            flash("Username already exists. Please choose another one.")
            return render_template("register.html")

        db.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), datetime.utcnow().isoformat()),
        )
        db.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.")
            return render_template("login.html")

        session["user_id"] = user["id"]
        flash(f"Welcome, {user['username']}!")
        return redirect(url_for("chat_room"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))


@app.route("/chat", methods=["GET", "POST"])
def chat_room():
    user = current_user()
    if user is None:
        return redirect(url_for("login"))

    db = get_db()

    if request.method == "POST":
        content = request.form.get("message", "").strip()
        if content:
            db.execute(
                "INSERT INTO messages (user_id, content, created_at) VALUES (?, ?, ?)",
                (user["id"], content[:500], datetime.utcnow().isoformat()),
            )
            db.commit()
        return redirect(url_for("chat_room"))

    messages = db.execute(
        """
        SELECT messages.content, messages.created_at, users.username
        FROM messages
        JOIN users ON users.id = messages.user_id
        ORDER BY messages.id DESC
        LIMIT 100
        """
    ).fetchall()

    return render_template("chat.html", user=user, messages=reversed(messages))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
