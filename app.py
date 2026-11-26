import os  # Read environment variables and build file paths
import sqlite3  # Connect to and run queries on the SQLite database
from flask import (  # Import Flask web framework helpers
    Flask, render_template, request,  # App class, HTML renderer, form/request data
    redirect, url_for, flash, jsonify, g  # Redirects, URL builder, messages, JSON, request storage
)

app = Flask(__name__)  # Create the Flask web application

app.config["SECRET_KEY"] = os.environ.get(  # Set secret key needed for flash messages
    "SECRET_KEY", "mevi-workshop-development-key"  # Use env var SECRET_KEY or default dev key
)

# Database configuration
os.makedirs(app.instance_path, exist_ok=True)  # Ensure the 'instance' folder exists

DATABASE = os.environ.get(  # Set path to the SQLite database file
    "DATABASE_PATH",  # Check if custom DATABASE_PATH env var is set
    os.path.join(app.instance_path, "management.db")  # Otherwise use instance/management.db
)


# Database connection
def get_db():  # Get or open a database connection for the current request
    if "db" not in g:  # Check if this request already has a DB connection
        g.db = sqlite3.connect(DATABASE)  # Open a new SQLite connection
        g.db.row_factory = sqlite3.Row  # Return rows like dicts (access columns by name)

    return g.db  # Return the active connection


@app.teardown_appcontext  # Run automatically when a request finishes
def close_db(exception=None):  # Close the database connection safely
    db = g.pop("db", None)  # Remove and fetch connection from 'g' if it exists

    if db is not None:  # Only close if a connection was opened
        db.close()  # Close the SQLite connection


# Create database table
def init_db():  # Create the 'students' table if it does not exist yet
    with sqlite3.connect(DATABASE) as db:  # Open DB and auto-commit on exit
        # Create students table with id, name, unique email, course, and timestamp
        db.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                course TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


init_db()  # Ensure database table exists even when started via Gunicorn


# Dashboard
@app.route("/")  # Handle GET requests to the home page '/'
def dashboard():  # Render dashboard summary page
    db = get_db()  # Get active DB connection

    total_students = db.execute(  # Run SQL to count all students
        "SELECT COUNT(*) FROM students"  # Count total rows in students table
    ).fetchone()[0]  # Grab the first number from the result

    total_courses = db.execute(  # Run SQL to count unique courses
        "SELECT COUNT(DISTINCT course) FROM students"  # Count distinct course names
    ).fetchone()[0]  # Grab the first number from the result

    recent_students = db.execute(  # Fetch the 5 newest student records
        "SELECT * FROM students ORDER BY id DESC LIMIT 5"  # Sort newest first, limit 5
    ).fetchall()  # Return all matching rows as a list

    return render_template(  # Render HTML template with dashboard data
        "index.html",  # Template file to render
        total_students=total_students,  # Pass total student count to HTML
        total_courses=total_courses,  # Pass total course count to HTML
        recent_students=recent_students  # Pass recent students list to HTML
    )


# Student management page
@app.route("/students")  # Handle GET requests to '/students'
def students():  # Show all students and the add-student form
    db = get_db()  # Get active DB connection

    all_students = db.execute(  # Fetch every student, newest first
        "SELECT * FROM students ORDER BY id DESC"  # Select all columns sorted by newest ID
    ).fetchall()  # Get list of student rows

    return render_template(  # Render the students page
        "students.html",  # Template file to render
        students=all_students  # Pass all student rows to HTML
    )


# Add student
@app.route("/students/add", methods=["POST"])  # Handle form POST to '/students/add'
def add_student():  # Validate input and save a new student
    name = request.form.get("name", "").strip()  # Read and trim 'name' from form
    email = request.form.get("email", "").strip().lower()  # Read, trim, and lowercase 'email'
    course = request.form.get("course", "").strip()  # Read and trim 'course' from form

    if not name or not email or not course:  # Check if any field is empty
        flash("Please fill in all fields.", "error")  # Show red error banner
        return redirect(url_for("students"))  # Go back to students page

    if "@" not in email:  # Basic check that email contains '@'
        flash("Please enter a valid email address.", "error")  # Show red error banner
        return redirect(url_for("students"))  # Go back to students page

    db = get_db()  # Get active DB connection

    try:  # Try inserting the new student
        db.execute(  # Insert row safely using '?' placeholders
            """
            INSERT INTO students (name, email, course)
            VALUES (?, ?, ?)
            """,
            (name, email, course)  # Values mapped to the three '?' placeholders
        )
        db.commit()  # Save changes permanently to the database

        flash("Student added successfully!", "success")  # Show green success banner

    except sqlite3.IntegrityError:  # Triggered if email already exists (UNIQUE rule)
        flash("This email address is already registered.", "error")  # Show duplicate email error

    return redirect(url_for("students"))  # Reload the students page


# Delete student
@app.route("/students/<int:student_id>/delete", methods=["POST"])  # Handle POST delete for a student ID
def delete_student(student_id):  # Remove one student by their ID
    db = get_db()  # Get active DB connection

    db.execute(  # Run DELETE query for matching ID
        "DELETE FROM students WHERE id = ?",  # SQL delete using '?' placeholder
        (student_id,)  # Tuple with the student ID to delete
    )
    db.commit()  # Save the deletion to the database

    flash("Student record deleted.", "success")  # Show confirmation banner

    return redirect(url_for("students"))  # Reload the students page


# JSON API
@app.route("/api/students")  # Handle GET requests to '/api/students'
def students_api():  # Return all students as JSON data
    db = get_db()  # Get active DB connection

    records = db.execute(  # Fetch student fields sorted newest first
        "SELECT id, name, email, course FROM students ORDER BY id DESC"  # Query student records
    ).fetchall()  # Get all rows

    return jsonify([  # Convert list of dicts into a JSON HTTP response
        dict(record) for record in records  # Convert each SQLite Row into a Python dict
    ])


# Health check
@app.route("/health")  # Handle GET requests to '/health'
def health():  # Simple endpoint to check if server is alive
    return jsonify({  # Return JSON status response
        "status": "healthy",  # App status string
        "application": "MEVI Management Portal"  # App name
    })


if __name__ == "__main__":  # Run only when executed directly (python app.py)
    init_db()  # Create database table before starting server
    port = int(os.environ.get("PORT", "5001"))  # Read PORT env var or default to 5001
    app.run(  # Start the built-in Flask web server
        host="0.0.0.0",  # Listen on all local network interfaces
        port=port,  # Port number to serve on
        debug=False  # Run with debug mode turned off
    )
