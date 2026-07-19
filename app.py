from flask import Flask, render_template, request, redirect
import sqlite3

from collections import defaultdict
from datetime import datetime

from study_data import study_data
from resource_links import resource_links

app = Flask(__name__)


# =====================================================
# DATABASE
# =====================================================

def init_db():

    conn = sqlite3.connect("database.db", timeout=10)
    cursor = conn.cursor()

    # =====================================================
    # TASKS
    # =====================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        task TEXT,

        subject TEXT,

        due_date TEXT,

        status TEXT

    )
    """)

    # =====================================================
    # SUBJECTS
    # =====================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        subject_name TEXT UNIQUE

    )
    """)

    # =====================================================
    # BOOKS
    # =====================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        subject_id INTEGER,

        book_name TEXT,

        FOREIGN KEY(subject_id)
        REFERENCES subjects(id)

    )
    """)

    # =====================================================
    # CHAPTERS
    # =====================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chapters(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        book_id INTEGER,

        chapter_name TEXT,

        FOREIGN KEY(book_id)
        REFERENCES books(id)

    )
    """)

    # =====================================================
    # RESOURCES
    # =====================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resources(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        chapter_id INTEGER,

        resource_name TEXT,

        pdf_link TEXT,

        FOREIGN KEY(chapter_id)
        REFERENCES chapters(id)

    )
    """)

    # =====================================================
    # PLANNER TASKS
    # =====================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS planner_tasks(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        task TEXT,

        subject TEXT,

        priority TEXT,

        due_date TEXT,

        due_time TEXT,

        status TEXT

    )
    """)

    # =====================================================
    # TIME BLOCKS
    # =====================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS time_blocks(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        day TEXT,

        start_time TEXT,

        end_time TEXT,

        title TEXT

    )
    """)

    subjects = [

        "Maths",
        "Physics",
        "Chemistry",
        "English",
        "Computer Science"

    ]

    for subject in subjects:

        cursor.execute("""

        INSERT OR IGNORE
        INTO subjects(subject_name)

        VALUES (?)

        """,(subject,))

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
# STUDY MATERIALS
# =====================================================

@app.route("/materials")
def materials():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

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

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM subjects WHERE id=?",
        (subject_id,)
    )

    subject = cursor.fetchone()

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

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM books WHERE id=?",
        (book_id,)
    )

    book = cursor.fetchone()

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

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM chapters WHERE id=?",
        (chapter_id,)
    )

    chapter = cursor.fetchone()

    cursor.execute(
        """
        SELECT *
        FROM resources
        WHERE chapter_id=?
        """,
        (chapter_id,)
    )

    resources = cursor.fetchall()

    conn.close()

    return render_template(
        "resources.html",
        chapter=chapter,
        resources=resources
    )
# =====================================================
# SETUP EVERYTHING
# =====================================================

@app.route("/setup_everything")
def setup_everything():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Clear old data
    cursor.execute("DELETE FROM resources")
    cursor.execute("DELETE FROM chapters")
    cursor.execute("DELETE FROM books")

    # Loop through every subject
    for subject_name, books in study_data.items():

        cursor.execute(
            "SELECT id FROM subjects WHERE subject_name=?",
            (subject_name,)
        )

        subject = cursor.fetchone()

        if not subject:
            continue

        subject_id = subject[0]

        # Books
        for book_name, chapters in books.items():

            cursor.execute(
                """
                INSERT INTO books(subject_id, book_name)
                VALUES(?,?)
                """,
                (subject_id, book_name)
            )

            book_id = cursor.lastrowid

            # Chapters
            for chapter in chapters:

                cursor.execute(
                    """
                    INSERT INTO chapters(book_id, chapter_name)
                    VALUES(?,?)
                    """,
                    (book_id, chapter)
                )

                chapter_id = cursor.lastrowid

                # Resources
                if chapter in resource_links:

                    for resource_name, pdf_link in resource_links[chapter].items():

                        cursor.execute(
                            """
                            INSERT INTO resources(
                                chapter_id,
                                resource_name,
                                pdf_link
                            )
                            VALUES(?,?,?)
                            """,
                            (
                                chapter_id,
                                resource_name,
                                pdf_link
                            )
                        )

    conn.commit()
    conn.close()

    return "StudyBuddy database populated successfully!"
# =====================================================
# TASKS
# =====================================================

@app.route("/tasks")
def tasks():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

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

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO tasks(task, subject, due_date, status)
        VALUES(?,?,?,?)
        """,
        (
            request.form["task"],
            request.form["subject"],
            request.form["due_date"],
            request.form["status"]
        )
    )

    conn.commit()
    conn.close()

    return redirect("/tasks")


@app.route("/delete_task/<int:id>", methods=["POST"])
def delete_task(id):

    conn = sqlite3.connect("database.db")
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

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM planner_tasks
        ORDER BY due_date,due_time
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

            except:
                pass

    cursor.execute("""
        SELECT *
        FROM time_blocks
        ORDER BY day,start_time
    """)

    time_blocks = cursor.fetchall()

    completed_tasks = len(
        [t for t in planner_tasks if t["status"] == "Completed"]
    )

    study_hours = len(time_blocks)

    weekly_goal = min(
        100,
        int((completed_tasks / max(1, len(planner_tasks))) * 100)
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

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO planner_tasks(
            task,
            subject,
            priority,
            due_date,
            due_time,
            status
        )
        VALUES(?,?,?,?,?,?)
        """,
        (
            request.form["task"],
            request.form["subject"],
            request.form["priority"],
            request.form["due_date"],
            request.form.get("due_time",""),
            "Pending"
        )
    )

    conn.commit()
    conn.close()

    return redirect("/planner")


@app.route("/delete_planner_task/<int:id>", methods=["POST"])
def delete_planner_task(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM planner_tasks WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/planner")
@app.route("/timer")
def timer():
    return render_template("timer.html")
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
