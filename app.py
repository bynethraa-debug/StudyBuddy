
from flask import Flask, render_template, request, redirect, jsonify, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from collections import defaultdict
from datetime import datetime

from study_data import study_data
from resource_links import resource_links

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "studybuddy-local-development-key-change-before-deploying"
)

DATABASE = "database.db"


# =====================================================
# DATABASE
# =====================================================

def get_db():
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    # TASKS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            subject TEXT,
            due_date TEXT,
            status TEXT
        )
    """)

    # SUBJECTS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT UNIQUE
        )
    """)

    # BOOKS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            book_name TEXT,
            FOREIGN KEY(subject_id) REFERENCES subjects(id)
        )
    """)

    # CHAPTERS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            chapter_name TEXT,
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
    """)

    # RESOURCES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_id INTEGER,
            resource_name TEXT,
            pdf_link TEXT,
            FOREIGN KEY(chapter_id) REFERENCES chapters(id)
        )
    """)

    # PLANNER TASKS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS planner_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            subject TEXT,
            priority TEXT,
            due_date TEXT,
            due_time TEXT,
            status TEXT
        )
    """)

    # TIME BLOCKS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS time_blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT,
            start_time TEXT,
            end_time TEXT,
            title TEXT
        )
    """)

    # DEFAULT SUBJECTS
    subjects = [
        "Maths",
        "Physics",
        "Chemistry",
        "English",
        "Computer Science"
    ]

    for subject in subjects:
        cursor.execute("""
            INSERT OR IGNORE INTO subjects(subject_name)
            VALUES (?)
        """, (subject,))

    conn.commit()
    conn.close()


init_db()


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():
    return render_template("index.html")


# =====================================================
# LOGIN / REGISTER
# =====================================================

@app.route("/login")
def login():
    if session.get("user_id"):
        return redirect("/materials")
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("login.html")


@app.route("/auth/register", methods=["POST"])
def auth_register():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify(error="Please fill in all fields."), 400

    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify(error="Please enter a valid email address."), 400

    if len(password) < 8:
        return jsonify(error="Password must be at least 8 characters."), 400

    password_hash = generate_password_hash(password)

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password_hash)
        )
        conn.commit()

        user = conn.execute(
            "SELECT id, name FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        session.clear()
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]

        return jsonify(message="Account created successfully.")

    except sqlite3.IntegrityError:
        return jsonify(error="An account with this email already exists."), 409
    finally:
        conn.close()


@app.route("/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify(error="Please enter your email and password."), 400

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()
    conn.close()

    if user is None or not check_password_hash(user["password"], password):
        return jsonify(error="Incorrect email or password."), 401

    session.clear()
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]

    return jsonify(message="Login successful.")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect("/login")
# =====================================================
# ACCOUNT
# =====================================================

@app.route("/account")
def account():
    if not session.get("user_id"):
        return redirect("/login")

    conn = get_db()

    user = conn.execute(
        "SELECT id, name, email FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    conn.close()

    if user is None:
        session.clear()
        return redirect("/login")

    return render_template("account.html", user=user)






# =====================================================
# STUDY MATERIALS
# =====================================================

@app.route("/materials")
def materials():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM subjects
        ORDER BY subject_name
    """)

    subjects = cursor.fetchall()
    conn.close()

    return render_template(
        "materials.html",
        subjects=subjects
    )


# =====================================================
# SUBJECT PAGE
# =====================================================

@app.route("/subject/<int:subject_id>")
def subject(subject_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM subjects WHERE id=?",
        (subject_id,)
    )
    subject = cursor.fetchone()

    if subject is None:
        conn.close()
        return "Subject not found", 404

    cursor.execute(
        "SELECT * FROM books WHERE subject_id=?",
        (subject_id,)
    )
    books = cursor.fetchall()

    conn.close()

    return render_template(
        "books.html",
        subject=subject,
        books=books
    )


# =====================================================
# BOOK PAGE
# =====================================================

@app.route("/book/<int:book_id>")
def book(book_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM books WHERE id=?",
        (book_id,)
    )
    book = cursor.fetchone()

    if book is None:
        conn.close()
        return "Book not found", 404

    cursor.execute(
        "SELECT * FROM chapters WHERE book_id=?",
        (book_id,)
    )
    chapters = cursor.fetchall()

    conn.close()

    return render_template(
        "chapters.html",
        book=book,
        chapters=chapters
    )


# =====================================================
# CHAPTER PAGE
# =====================================================

@app.route("/chapter/<int:chapter_id>")
def chapter(chapter_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM chapters WHERE id=?",
        (chapter_id,)
    )
    chapter = cursor.fetchone()

    if chapter is None:
        conn.close()
        return "Chapter not found", 404

    cursor.execute("""
        SELECT *
        FROM resources
        WHERE chapter_id=?
    """, (chapter_id,))

    resources = cursor.fetchall()
    conn.close()

    return render_template(
        "resources.html",
        chapter=chapter,
        resources=resources
    )


# =====================================================
# SETUP STUDY MATERIALS
# =====================================================

@app.route("/setup_everything")
def setup_everything():
    conn = get_db()
    cursor = conn.cursor()

    # Clear existing study material data before rebuilding.
    cursor.execute("DELETE FROM resources")
    cursor.execute("DELETE FROM chapters")
    cursor.execute("DELETE FROM books")

    for subject_name, books in study_data.items():
        cursor.execute(
            "SELECT id FROM subjects WHERE subject_name=?",
            (subject_name,)
        )
        subject = cursor.fetchone()

        if not subject:
            continue

        subject_id = subject["id"]

        for book_name, chapters in books.items():
            cursor.execute("""
                INSERT INTO books(subject_id, book_name)
                VALUES (?, ?)
            """, (subject_id, book_name))

            book_id = cursor.lastrowid

            for chapter_name in chapters:
                cursor.execute("""
                    INSERT INTO chapters(book_id, chapter_name)
                    VALUES (?, ?)
                """, (book_id, chapter_name))

                chapter_id = cursor.lastrowid

                if chapter_name in resource_links:
                    for resource_name, pdf_link in resource_links[chapter_name].items():
                        cursor.execute("""
                            INSERT INTO resources(
                                chapter_id,
                                resource_name,
                                pdf_link
                            )
                            VALUES (?, ?, ?)
                        """, (
                            chapter_id,
                            resource_name,
                            pdf_link
                        ))

    conn.commit()
    conn.close()

    return "StudyBuddy database populated successfully!"


# =====================================================
# TASKS
# =====================================================

@app.route("/tasks")
def tasks():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM tasks
        ORDER BY due_date
    """)

    tasks = cursor.fetchall()
    conn.close()

    return render_template(
        "tasks.html",
        tasks=tasks
    )


@app.route("/add_task", methods=["POST"])
def add_task():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks(task, subject, due_date, status)
        VALUES (?, ?, ?, ?)
    """, (
        request.form.get("task", ""),
        request.form.get("subject", ""),
        request.form.get("due_date", ""),
        request.form.get("status", "Pending")
    ))

    conn.commit()
    conn.close()

    return redirect("/tasks")


@app.route("/delete_task/<int:id>", methods=["POST"])
def delete_task(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/tasks")


# =====================================================
# PLANNER
# =====================================================

@app.route("/planner")
def planner():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM planner_tasks
        ORDER BY due_date, due_time
    """)

    planner_tasks = cursor.fetchall()
    tasks_by_day = defaultdict(list)

    for task in planner_tasks:
        if task["due_date"]:
            try:
                day = datetime.strptime(
                    task["due_date"],
                    "%Y-%m-%d"
                ).strftime("%A")

                tasks_by_day[day].append(task)
            except ValueError:
                pass

    cursor.execute("""
        SELECT *
        FROM time_blocks
        ORDER BY day, start_time
    """)

    time_blocks = cursor.fetchall()

    completed_tasks = sum(
        1 for task in planner_tasks
        if task["status"] == "Completed"
    )

    study_hours = len(time_blocks)

    weekly_goal = min(
        100,
        int(
            (completed_tasks / max(1, len(planner_tasks))) * 100
        )
    )

    conn.close()

    return render_template(
        "planner.html",
        planner_tasks=planner_tasks,
        tasks_by_day=tasks_by_day,
        time_blocks=time_blocks,
        completed_tasks=completed_tasks,
        study_hours=study_hours,
        weekly_goal=weekly_goal
    )


@app.route("/add_planner_task", methods=["POST"])
def add_planner_task():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO planner_tasks(
            task,
            subject,
            priority,
            due_date,
            due_time,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        request.form.get("task", ""),
        request.form.get("subject", ""),
        request.form.get("priority", ""),
        request.form.get("due_date", ""),
        request.form.get("due_time", ""),
        "Pending"
    ))

    conn.commit()
    conn.close()

    return redirect("/planner")


@app.route("/delete_planner_task/<int:id>", methods=["POST"])
def delete_planner_task(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM planner_tasks WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/planner")


# =====================================================
# TIMER
# =====================================================

@app.route("/timer")
def timer():
    return render_template("timer.html")


# =====================================================
# PROGRESS
# =====================================================

@app.route("/progress")
def progress():
    return render_template("progress.html")


# =====================================================
# RUN APP
# =====================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )

