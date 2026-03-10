import os
import sqlite3
from functools import wraps

from flask import Flask, g, jsonify, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
app.config["DATABASE"] = os.path.join(app.root_path, "app.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db():
    db = sqlite3.connect(app.config["DATABASE"])
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            body TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """
    )
    db.commit()
    db.close()


@app.before_request
def ensure_db():
    init_db()


@app.teardown_appcontext
def close_db(_exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required."}), 401
        return view(*args, **kwargs)

    return wrapped_view


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None

    row = get_db().execute(
        "SELECT id, username FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    return dict(row) if row else None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/session", methods=["GET"])
def get_session():
    user = current_user()
    return jsonify({"authenticated": bool(user), "user": user})


@app.route("/api/register", methods=["POST"])
def register():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    db = get_db()
    existing_user = db.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    if existing_user:
        return jsonify({"error": "Username already exists."}), 409

    cursor = db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, generate_password_hash(password)),
    )
    db.commit()

    session["user_id"] = cursor.lastrowid
    return jsonify(
        {
            "message": "Registration successful.",
            "user": {"id": cursor.lastrowid, "username": username},
        }
    ), 201


@app.route("/api/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    user = get_db().execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid username or password."}), 401

    session["user_id"] = user["id"]
    return jsonify(
        {
            "message": "Login successful.",
            "user": {"id": user["id"], "username": user["username"]},
        }
    )


@app.route("/api/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return jsonify({"message": "Logged out."})


@app.route("/api/messages", methods=["GET"])
@login_required
def list_messages():
    rows = get_db().execute(
        """
        SELECT messages.id, messages.body, messages.created_at, users.username
        FROM messages
        JOIN users ON users.id = messages.user_id
        ORDER BY messages.id DESC
        LIMIT 50
        """
    ).fetchall()

    messages = [
        {
            "id": row["id"],
            "body": row["body"],
            "created_at": row["created_at"],
            "username": row["username"],
        }
        for row in reversed(rows)
    ]
    return jsonify({"messages": messages, "user": current_user()})


@app.route("/api/messages", methods=["POST"])
@login_required
def create_message():
    payload = request.get_json(silent=True) or {}
    body = (payload.get("message") or "").strip()
    if not body:
        return jsonify({"error": "Message cannot be empty."}), 400
    if len(body) > 400:
        return jsonify({"error": "Message must be 400 characters or fewer."}), 400

    user = current_user()
    db = get_db()
    cursor = db.execute(
        "INSERT INTO messages (user_id, body) VALUES (?, ?)",
        (user["id"], body),
    )
    db.commit()

    message = db.execute(
        """
        SELECT messages.id, messages.body, messages.created_at, users.username
        FROM messages
        JOIN users ON users.id = messages.user_id
        WHERE messages.id = ?
        """,
        (cursor.lastrowid,),
    ).fetchone()

    return jsonify(
        {
            "message": {
                "id": message["id"],
                "body": message["body"],
                "created_at": message["created_at"],
                "username": message["username"],
            }
        }
    ), 201


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
