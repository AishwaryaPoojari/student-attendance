from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL UNIQUE,
            course TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    return render_template("index.html", students=students)


@app.route("/add_student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form["name"]
        roll_no = request.form["roll_no"]
        course = request.form["course"]

        conn = get_db_connection()

        try:
            conn.execute(
                "INSERT INTO students (name, roll_no, course) VALUES (?, ?, ?)",
                (name, roll_no, course)
            )
            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return "Roll number already exists."

        conn.close()

        return redirect("/")

    return render_template("add_student.html")


@app.route("/attendance", methods=["GET", "POST"])
def attendance():

    conn = get_db_connection()

    students = conn.execute(
        "SELECT * FROM students"
    ).fetchall()

    if request.method == "POST":

        date = request.form["date"]

        for student in students:

            status = request.form.get(
                f"status_{student['id']}"
            )

            conn.execute(
                """
                INSERT INTO attendance
                (student_id, date, status)
                VALUES (?, ?, ?)
                """,
                (student["id"], date, status)
            )

        conn.commit()
        conn.close()

        return redirect("/view_attendance")

    conn.close()

    return render_template(
        "attendance.html",
        students=students
    )


@app.route("/view_attendance")
def view_attendance():

    conn = get_db_connection()

    records = conn.execute("""
        SELECT
            students.name,
            students.roll_no,
            attendance.date,
            attendance.status
        FROM attendance
        JOIN students
        ON students.id = attendance.student_id
        ORDER BY attendance.date DESC
    """).fetchall()

    conn.close()

    return render_template(
        "view_attendance.html",
        records=records
    )


if __name__ == "__main__":
    create_database()
    app.run(debug=True)