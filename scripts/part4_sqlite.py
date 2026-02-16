from pathlib import Path
import sqlite3

import pandas as pd


STUDENTS_PATH = Path("data/Part4/students.csv")
ENROLL_PATH = Path("data/Part4/enrollment.csv")
DEGREES_PATH = Path("data/Part4/degrees.csv")
OUTPUT_DIR = Path("outputs")
DB_PATH = OUTPUT_DIR / "institutional_records.db"


DDL_STUDENTS = """
CREATE TABLE IF NOT EXISTS Students (
    student_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    entry_term TEXT NOT NULL,
    state_residence TEXT,
    athlete_flag TEXT CHECK (athlete_flag IN ('Y', 'N'))
);
"""

DDL_ENROLLMENTS = """
CREATE TABLE IF NOT EXISTS Enrollments (
    enrollment_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    term TEXT NOT NULL,
    credits_enrolled INTEGER,
    registered_flag TEXT CHECK (registered_flag IN ('Y', 'N')),
    FOREIGN KEY (student_id) REFERENCES Students(student_id)
);
"""

DDL_DEGREES = """
CREATE TABLE IF NOT EXISTS Degrees (
    degree_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    grad_term TEXT,
    degree_awarded TEXT,
    FOREIGN KEY (student_id) REFERENCES Students(student_id)
);
"""

SQL_ATTRITION = """
SELECT
    s.student_id,
    s.first_name || ' ' || s.last_name AS full_name,
    s.state_residence,
    s.athlete_flag,
    e_fall.credits_enrolled
FROM Students s
JOIN Enrollments e_fall
    ON s.student_id = e_fall.student_id
    AND e_fall.term = 'Fall 2025'
    AND e_fall.registered_flag = 'Y'
LEFT JOIN Enrollments e_spring
    ON s.student_id = e_spring.student_id
    AND e_spring.term = 'Spring 2026'
    AND e_spring.registered_flag = 'Y'
WHERE s.entry_term = 'Fall 2025'
  AND e_spring.student_id IS NULL;
"""


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Delete existing database if it exists
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    conn.execute(DDL_STUDENTS)
    conn.execute(DDL_ENROLLMENTS)
    conn.execute(DDL_DEGREES)

    students = pd.read_csv(STUDENTS_PATH, dtype=str)
    enrollments = pd.read_csv(ENROLL_PATH, dtype=str)
    degrees = pd.read_csv(DEGREES_PATH, dtype=str)

    students = students[[
        "student_id",
        "first_name",
        "last_name",
        "entry_term",
        "state_residence",
        "athlete_flag",
    ]]

    enrollments = enrollments[[
        "enrollment_id",
        "student_id",
        "term",
        "credits_enrolled",
        "registered_flag",
    ]]

    degrees = degrees[[
        "degree_id",
        "student_id",
        "grad_term",
        "degree_awarded",
    ]]

    students.to_sql("Students", conn, if_exists="append", index=False)
    enrollments.to_sql("Enrollments", conn, if_exists="append", index=False)
    degrees.to_sql("Degrees", conn, if_exists="append", index=False)

    results = pd.read_sql_query(SQL_ATTRITION, conn)
    results.to_csv(OUTPUT_DIR / "part4_attrition_results.csv", index=False)

    conn.close()


if __name__ == "__main__":
    main()
