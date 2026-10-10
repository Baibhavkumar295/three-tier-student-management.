
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = "students.db"


# Tier 3: Data layer
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            course TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# Tier 2: Application layer
@app.route("/api/students", methods=["GET"])
def get_students():
    conn = get_db_connection()
    students = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    course = data.get("course", "").strip()

    if not name or not email or not course:
        return jsonify({
            "error": "Name, email and course are required."
        }), 400

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO students (name, email, course) VALUES (?, ?, ?)",
            (name, email, course)
        )
        conn.commit()
        student_id = cursor.lastrowid

        return jsonify({
            "message": "Student added successfully.",
            "id": student_id
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "This email is already registered."
        }), 409

    finally:
        conn.close()


@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    course = data.get("course", "").strip()

    if not name or not email or not course:
        return jsonify({
            "error": "Name, email and course are required."
        }), 400

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            """UPDATE students
               SET name = ?, email = ?, course = ?
               WHERE id = ?""",
            (name, email, course, student_id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found."}), 404

        return jsonify({"message": "Student updated successfully."})

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "This email is already registered."
        }), 409

    finally:
        conn.close()


@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.execute(
        "DELETE FROM students WHERE id = ?", (student_id,)
    )
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"error": "Student not found."}), 404

    return jsonify({"message": "Student deleted successfully."})


# Initialize the database when the application starts
initialize_database()


if __name__ == "__main__":
    app.run(debug=True)
