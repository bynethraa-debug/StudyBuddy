from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
           conn = sqlite3.connect("database.db")
           cursor = conn.cursor()
           cursor.execute("""
           CREATE TABLE IF NOT EXISTS tasks(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          task TEXT,
                          subject TEXT,
                          due_date TEXT,
                          status TEXT
            )
            """)

            conn.commit()
            conn.close()


@app.route("/")
def home():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM materials")
    materials = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        materials=materials
    )


@app.route("/add_material", methods=["POST"])
def add_material():

    subject = request.form["subject"]
    topic = request.form["topic"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO materials(subject, topic) VALUES (?, ?)",
        (subject, topic)
    )

    conn.commit()
    conn.close()

    return redirect("/")

    
@app.route("/tasks")
def tasks():

     conn = sqlite3.connect("database.db")
     cursor = conn.cursor()

     cursor.execute("SELECT * FROM tasks")
     tasks = cursor.fetchall()

     conn.close()

     return render_template(
        "tasks.html",
        tasks=tasks
     )


@app.route("/add_task", methods=["POST"])
def add_task():

    task = request.form["task"]
    subject = request.form["subject"]
    due_date = request.form["due_date"]
    status = request.form["status"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks(task, subject, due_date, status) VALUES (?, ?, ?, ?)",
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
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM materials")
    materials = cursor.fetchall()

    conn.close()

    return render_template(
        "materials.html",
        materials=materials
    )
@app.route("/timer")
def timer():
    return render_template("timer.html")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
