import sqlite3

DATABASE_NAME = "students.db"


# --- SGPA Logic ---
def get_grade_point(marks: float) -> int:
    if marks >= 90: return 10
    elif marks >= 80: return 9
    elif marks >= 70: return 8
    elif marks >= 60: return 7
    elif marks >= 50: return 6
    elif marks >= 40: return 5
    return 0


# --- Database Core Setup ---
def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    # Crucial: Enforce foreign key constraints in SQLite
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def create_tables():
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                course TEXT,
                semester INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS marks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                subject TEXT NOT NULL,
                marks REAL NOT NULL,
                credits INTEGER DEFAULT 3,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            )
        """)


# --- Student Operations ---
def add_student(name: str, email: str, course: str, semester: int):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO students (name, email, course, semester)
            VALUES (?, ?, ?, ?)
        """, (name, email, course, semester))


def get_students() -> list:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id, name, email, course, semester
            FROM students
            ORDER BY id DESC
        """)
        return cursor.fetchall()


def update_student(student_id: int, name: str, email: str, course: str, semester: int):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE students
            SET name = ?, email = ?, course = ?, semester = ?
            WHERE id = ?
        """, (name, email, course, semester, student_id))


def delete_student(student_id: int):
    with get_connection() as connection:
        cursor = connection.cursor()
        # Clean up marks first (though ON DELETE CASCADE handles this if configured)
        cursor.execute("DELETE FROM marks WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))


# --- Marks Operations ---
def add_marks(student_id: int, subject: str, marks: float, credits: int):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO marks (student_id, subject, marks, credits)
            VALUES (?, ?, ?, ?)
        """, (student_id, subject, marks, credits))


def get_marks(student_id: int) -> list:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id, subject, marks, credits
            FROM marks
            WHERE student_id = ?
        """, (student_id,))
        return cursor.fetchall()


def delete_marks(mark_id: int):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM marks WHERE id = ?", (mark_id,))


# --- SGPA Calculation from DB ---
def calculate_student_sgpa(student_id: int) -> float:
    """Fetches marks from DB for a student and calculates their SGPA."""
    marks_list = get_marks(student_id)
    if not marks_list:
        return 0.0

    total_points = 0
    total_credits = 0

    for row in marks_list:
        # row layout: (id, subject, marks, credits)
        marks = row[2]
        credits = row[3]

        grade_point = get_grade_point(marks)
        total_points += grade_point * credits
        total_credits += credits

    if total_credits == 0:
        return 0.0

    return round(total_points / total_credits, 2)


# --- Quick Test Execution ---
if __name__ == "__main__":
    create_tables()
    print("Database and tables verified successfully.")
