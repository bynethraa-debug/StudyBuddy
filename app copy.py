from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # ---------------- TASKS ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        subject TEXT,
        due_date TEXT,
        status TEXT
    )
    """)

    # ---------------- SUBJECTS ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_name TEXT UNIQUE NOT NULL
    )
    """)

    # ---------------- CHAPTERS ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chapters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        chapter_name TEXT NOT NULL,
        favorite INTEGER DEFAULT 0,
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
    )
    """)

    # ---------------- RESOURCES ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chapter_id INTEGER NOT NULL,
        resource_name TEXT NOT NULL,
        pdf_link TEXT NOT NULL,
        FOREIGN KEY(chapter_id) REFERENCES chapters(id)
    )
    """)

    # ---------- DEFAULT SUBJECTS ----------
    default_subjects = [
        "Maths",
        "Physics",
        "Chemistry",
        "English",
        "Computer Science"
    ]

    for subject in default_subjects:
        cursor.execute("""
        INSERT OR IGNORE INTO subjects(subject_name)
        VALUES (?)
        """, (subject,))

    conn.commit()
    conn.close()
 
 
@app.route("/")

def home():
    return render_template("index.html")


def tasks():

     conn = sqlite3.connect("database.db")
     cursor = conn.cursor()

     cursor.execute("SELECT * FROM tasks")
     tasks = cursor.fetchall()

     conn.close()

     return render_template("tasks.html", tasks=tasks)

 
    


@app.route("/add_task", methods=["POST"])
def add_task():

    task = request.form["task"]
    subject = request.form["subject"]
    due_date = request.form["due_date"]
    status = request.form["status"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks(task, subject, due_date, status) VALUES (?,?,?,?)",
        (task, subject, due_date, status)
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


init_db()

@app.route("/materials")
def materials():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM subjects ORDER BY subject_name")
    subjects = cursor.fetchall()

    conn.close()

    return render_template(
        "materials.html",
        subjects=subjects
    )

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
        "SELECT * FROM chapters WHERE subject_id=? ORDER BY chapter_name",
        (subject_id,)
    )

    chapters = cursor.fetchall()

    conn.close()

    return render_template(
        "subject.html",
        subject=subject,
        chapters=chapters
    )
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
        "SELECT * FROM resources WHERE chapter_id=?",
        (chapter_id,)
    )

    resources = cursor.fetchall()

    conn.close()

    return render_template(
        "chapter.html",
        chapter=chapter,
        resources=resources
    )
@app.route("/add_resource/<int:chapter_id>", methods=["POST"])
def add_resource(chapter_id):

    resource_name = request.form["resource_name"]
    pdf_link = request.form["pdf_link"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO resources(chapter_id, resource_name, pdf_link)
        VALUES (?,?,?)
        """,
        (chapter_id, resource_name, pdf_link)
    )

    conn.commit()
    conn.close()

    return redirect(f"/chapter/{chapter_id}")
@app.route("/setup_maths")
def setup_maths():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    chapters = [

    (1, "Relations and Functions"),
    (2, "Inverse Trigonometric Functions"),
    (3, "Matrices"),
    (4, "Determinants"),
    (5, "Continuity and Differentiability"),
    (6, "Application of Derivatives"),
    (7, "Integrals"),
    (8, "Application of Integrals"),
    (9, "Differential Equations"),
    (10, "Vector Algebra"),
    (11, "Three-Dimensional Geometry"),
    (12, "Linear Programming"),
    (13, "Probability")

]
@app.route("/reset_maths")
def reset_maths():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Find the Maths subject
    cursor.execute(
        "SELECT id FROM subjects WHERE subject_name=?",
        ("Maths",)
    )

    maths = cursor.fetchone()

    if maths:

        subject_id = maths[0]

        # Get all Maths chapter IDs
        cursor.execute(
            "SELECT id FROM chapters WHERE subject_id=?",
            (subject_id,)
        )

        chapter_ids = cursor.fetchall()

        # Delete resources for each chapter
        for chapter in chapter_ids:
            cursor.execute(
                "DELETE FROM resources WHERE chapter_id=?",
                (chapter[0],)
            )

        # Delete the chapters
        cursor.execute(
            "DELETE FROM chapters WHERE subject_id=?",
            (subject_id,)
        )

    conn.commit()
    conn.close()

    return "Maths has been reset! Now visit /setup_maths"

    



    # Find the Maths subject
 cursor.execute(
        "SELECT id FROM subjects WHERE subject_name=?",
        ("Maths",)
    )

    maths = cursor.fetchone()

    if maths:

        subject_id = maths[0]

        for number, chapter in chapters:

            cursor.execute("""
            SELECT * FROM chapters
            WHERE subject_id=? AND chapter_name=?
            """, (subject_id, chapter))

            if cursor.fetchone() is None:

                cursor.execute("""
                INSERT INTO chapters(subject_id, chapter_name)
                VALUES (?,?)
                """, (subject_id, chapter))
            chapter_id = cursor.lastrowid

            default_resources = [

                 ("📘 NCERT Textbook", "#"),
                ("📝 Notes", "#"),
                ("📚 PYQs", "#"),
                ("📋 Formula Sheet", "#"),
                ("📄 Sample Papers", "#")

            ]

        for resource_name, pdf in default_resources:

             cursor.execute("""

             INSERT INTO resources(
                    chapter_id,
                    resource_name,
                    pdf_link
             )

             VALUES (?,?,?)

             """, (chapter_id, resource_name, pdf))

    conn.commit()
    conn.close()

    return redirect("/materials")

@app.route("/timer")
def timer():
    return render_template("timer.html")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)