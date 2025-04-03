import sqlite3
from sqlite3 import Error
import json

def create_connection():
    """Create a database connection to SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect('career_counseling.db')
        print("Connection to SQLite DB successful")
        return conn
    except Error as e:
        print(f"The error '{e}' occurred")
    return conn

def initialize_database():
    """Initialize the database with required tables"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            
            # Create assessments table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS career_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                education TEXT,
                experience TEXT,
                skills TEXT,
                interests TEXT,
                work_life_balance INTEGER,
                salary_importance INTEGER,
                location_preference TEXT,
                results TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """)
            
            conn.commit()
            print("Database initialized successfully")
        except Error as e:
            print(f"Error initializing database: {e}")
        finally:
            conn.close()

def register_user(username, email, password):
    """Register a new user"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )  # Added missing closing parenthesis here
            conn.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error registering user: {e}")
            return None
        finally:
            conn.close()
    return None

def get_user_by_email(email):
    """Get user by email"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error getting user: {e}")
            return None
        finally:
            conn.close()
    return None

def save_assessment(user_id, assessment_data):
    """Save career assessment results"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO career_assessments 
                (user_id, education, experience, skills, interests, 
                 work_life_balance, salary_importance, location_preference, results)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                assessment_data.get('education'),
                assessment_data.get('experience'),
                ','.join(assessment_data.get('skills', [])),
                assessment_data.get('interests'),
                assessment_data.get('workLifeBalance'),
                assessment_data.get('salaryImportance'),
                assessment_data.get('location'),
                json.dumps(assessment_data.get('results', []))
            ))
            conn.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error saving assessment: {e}")
            return None
        finally:
            conn.close()
    return None