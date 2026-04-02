# backend/app.py - CORRECTED VERSION
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import hashlib
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Opensql@nitish1234',
    'database': 'exam_proctoring'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        if "Unknown database" in str(e):
            create_database()
            return mysql.connector.connect(**db_config)
        raise e

def create_database():
    """Create database and tables if they don't exist"""
    try:
        # Connect without specifying database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Opensql@nitish1234'
        )
        
        cursor = connection.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS exam_proctoring")
        print("✅ Database created successfully")
        
        # Use the database
        cursor.execute("USE exam_proctoring")
        
        # Create tables WITH FOREIGN KEYS
        tables = [
            """CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('student', 'admin') DEFAULT 'student',
                profile_photo TEXT,
                is_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS exams (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                subject VARCHAR(100),
                duration_minutes INT,
                total_marks INT,
                created_by INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                exam_id INT,
                question_text TEXT NOT NULL,
                option_a VARCHAR(255),
                option_b VARCHAR(255),
                option_c VARCHAR(255),
                option_d VARCHAR(255),
                correct_answer CHAR(1),
                marks INT,
                FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS exam_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                exam_id INT,
                score INT,
                total_marks INT,
                start_time DATETIME,
                end_time DATETIME,
                status VARCHAR(20),
                violations INT DEFAULT 0,
                FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS captured_photos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                exam_result_id INT,
                photo_data TEXT,
                timestamp DATETIME,
                violations_detected TEXT,
                FOREIGN KEY (exam_result_id) REFERENCES exam_results(id) ON DELETE CASCADE
            )"""
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
        
        # Insert sample admin if not exists
        cursor.execute("""
            INSERT IGNORE INTO users (name, email, password, role, is_verified) 
            VALUES ('Admin User', 'admin@example.com', SHA2('admin123', 256), 'admin', TRUE)
        """)
        
        cursor.execute("""
            INSERT IGNORE INTO users (name, email, password, role, is_verified) 
            VALUES ('John Student', 'student@example.com', SHA2('student123', 256), 'student', TRUE)
        """)
        
        connection.commit()
        print("✅ Tables created successfully")
        
    except Error as e:
        print(f"❌ Error creating database: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    return True

# ✅ FIX: Use application context to initialize database
with app.app_context():
    print("🔄 Initializing database...")
    if not create_database():
        print("⚠️ Database initialization failed")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def home():
    return jsonify({"message": "Exam Proctoring API"})

@app.route('/api/test', methods=['GET'])
def test():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({
            "status": "success",
            "message": "Database connected successfully",
            "data": result[0]
        })
    except Error as e:
        return jsonify({"error": str(e)}), 500

# User Registration
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        
        # Validate input
        if not data.get('name') or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Name, email and password are required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (data['email'],))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Email already exists"}), 400
        
        # Hash password
        hashed_password = hash_password(data['password'])
        
        # Insert user
        cursor.execute('''
            INSERT INTO users (name, email, password, role, profile_photo)
            VALUES (%s, %s, %s, %s, %s)
        ''', (
            data['name'], 
            data['email'], 
            hashed_password, 
            data.get('role', 'student'), 
            data.get('profile_photo', '')
        ))
        
        conn.commit()
        user_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Registration successful", 
            "user_id": user_id,
            "email": data['email']
        }), 201
        
    except Error as e:
        print(f"Registration error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# User Login
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        
        if not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email and password are required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        hashed_password = hash_password(data['password'])
        
        cursor.execute('''
            SELECT id, name, email, role, profile_photo 
            FROM users 
            WHERE email = %s AND password = %s
        ''', (data['email'], hashed_password))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            return jsonify({
                "message": "Login successful", 
                "user": user
            })
        else:
            return jsonify({"error": "Invalid email or password"}), 401
            
    except Error as e:
        print(f"Login error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Get all users (for testing)
@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, name, email, role, created_at FROM users")
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(users)
        
    except Error as e:
        print(f"Get users error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Get Exams
@app.route('/api/exams', methods=['GET'])
def get_exams():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT e.*, u.name as created_by_name 
            FROM exams e 
            JOIN users u ON e.created_by = u.id 
            WHERE e.created_at <= NOW()
        ''')
        
        exams = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(exams)
        
    except Error as e:
        print(f"Get exams error: {e}")
        return jsonify({"error": "Database error occurred"}), 500
@app.route('/api/exam/<int:exam_id>/info', methods=['GET'])
def get_exam_info(exam_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('''
            SELECT e.*, u.name as created_by_name
            FROM exams e
            JOIN users u ON e.created_by = u.id
            WHERE e.id = %s
        ''', (exam_id,))

        exam = cursor.fetchone()

        cursor.close()
        conn.close()

        if not exam:
            return jsonify({"error": "Exam not found"}), 404

        return jsonify(exam)

    except Error as e:
        print(f"Get exam info error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Get Exam Questions
@app.route('/api/exam/<int:exam_id>/questions', methods=['GET'])
def get_exam_questions(exam_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM questions WHERE exam_id = %s', (exam_id,))
        questions = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(questions)
        
    except Error as e:
        print(f"Get questions error: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    
# ====================
# ADMIN ROUTES
# ====================

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.json
        
        if not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email and password are required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        hashed_password = hash_password(data['password'])
        
        cursor.execute('''
            SELECT id, name, email, role, profile_photo 
            FROM users 
            WHERE email = %s AND password = %s AND role = 'admin'
        ''', (data['email'], hashed_password))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            return jsonify({
                "message": "Admin login successful", 
                "user": user
            })
        else:
            return jsonify({"error": "Invalid admin credentials"}), 401
            
    except Error as e:
        print(f"Admin login error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Get all students
@app.route('/api/admin/students', methods=['GET'])
def get_all_students():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, name, email, created_at, is_verified 
            FROM users 
            WHERE role = 'student'
            ORDER BY created_at DESC
        """)
        
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(students)
        
    except Error as e:
        print(f"Get students error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Create new exam (RENAME THIS since you already have a create_exam function)
@app.route('/api/admin/exam/create-new', methods=['POST'])  # Changed endpoint
def admin_create_exam():
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['title', 'subject', 'duration_minutes', 'total_marks', 'admin_id', 'questions']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert exam
        cursor.execute('''
            INSERT INTO exams (title, subject, duration_minutes, total_marks, created_by)
            VALUES (%s, %s, %s, %s, %s)
        ''', (
            data['title'], 
            data['subject'], 
            data['duration_minutes'], 
            data['total_marks'], 
            data['admin_id']
        ))
        
        exam_id = cursor.lastrowid
        
        # Insert questions
        for question in data['questions']:
            cursor.execute('''
                INSERT INTO questions 
                (exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer, marks)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                exam_id,
                question['question_text'],
                question.get('option_a'),
                question.get('option_b'),
                question.get('option_c'),
                question.get('option_d'),
                question['correct_answer'],
                question['marks']
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Exam created successfully",
            "exam_id": exam_id
        }), 201
        
    except Error as e:
        print(f"Create exam error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Get all exams (admin view)
@app.route('/api/admin/exams', methods=['GET'])
def admin_get_exams():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT e.*, 
                   u.name as admin_name,
                   COUNT(q.id) as question_count,
                   COUNT(DISTINCT er.id) as attempts_count
            FROM exams e
            LEFT JOIN users u ON e.created_by = u.id
            LEFT JOIN questions q ON e.id = q.exam_id
            LEFT JOIN exam_results er ON e.id = er.exam_id
            GROUP BY e.id
            ORDER BY e.created_at DESC
        ''')
        
        exams = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(exams)
        
    except Error as e:
        print(f"Get admin exams error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Get exam details with questions
@app.route('/api/admin/exam/<int:exam_id>', methods=['GET'])
def admin_get_exam_details(exam_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get exam details
        cursor.execute('''
            SELECT e.*, u.name as admin_name
            FROM exams e
            JOIN users u ON e.created_by = u.id
            WHERE e.id = %s
        ''', (exam_id,))
        
        exam = cursor.fetchone()
        
        if not exam:
            return jsonify({"error": "Exam not found"}), 404
        
        # Get questions
        cursor.execute('SELECT * FROM questions WHERE exam_id = %s', (exam_id,))
        questions = cursor.fetchall()
        
        exam['questions'] = questions
        
        cursor.close()
        conn.close()
        
        return jsonify(exam)
        
    except Error as e:
        print(f"Get exam details error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Get exam results
@app.route('/api/admin/exam/<int:exam_id>/results', methods=['GET'])
def get_exam_results(exam_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT er.*, u.name as student_name, u.email as student_email
            FROM exam_results er
            JOIN users u ON er.student_id = u.id
            WHERE er.exam_id = %s
            ORDER BY er.score DESC
        ''', (exam_id,))
        
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(results)
        
    except Error as e:
        print(f"Get exam results error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Get all exam results (for all exams)
@app.route('/api/admin/all-results', methods=['GET'])
def get_all_exam_results():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT 
                er.*,
                e.title as exam_title,
                e.subject as exam_subject,
                u.name as student_name,
                u.email as student_email,
                admin.name as admin_name
            FROM exam_results er
            JOIN exams e ON er.exam_id = e.id
            JOIN users u ON er.student_id = u.id
            JOIN users admin ON e.created_by = admin.id
            ORDER BY er.end_time DESC
        ''')
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(results)
        
    except Error as e:
        print(f"Get all results error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Get system statistics
@app.route('/api/admin/statistics', methods=['GET'])
def get_statistics():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        statistics = {}
        
        # Total students
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'student'")
        statistics['total_students'] = cursor.fetchone()['count']
        
        # Total admins
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
        statistics['total_admins'] = cursor.fetchone()['count']
        
        # Total exams
        cursor.execute("SELECT COUNT(*) as count FROM exams")
        statistics['total_exams'] = cursor.fetchone()['count']
        
        # Total exam attempts
        cursor.execute("SELECT COUNT(*) as count FROM exam_results")
        statistics['total_attempts'] = cursor.fetchone()['count']
        
        # Recent exams (last 5)
        cursor.execute("""
            SELECT title, created_at, subject 
            FROM exams 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        statistics['recent_exams'] = cursor.fetchall()
        
        # Recent results (last 5)
        cursor.execute("""
            SELECT er.score, er.total_marks, e.title, u.name as student_name
            FROM exam_results er
            JOIN exams e ON er.exam_id = e.id
            JOIN users u ON er.student_id = u.id
            ORDER BY er.end_time DESC 
            LIMIT 5
        """)
        statistics['recent_results'] = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(statistics)
        
    except Error as e:
        print(f"Get statistics error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Delete exam
@app.route('/api/admin/exam/<int:exam_id>', methods=['DELETE'])
def delete_exam(exam_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if exam exists
        cursor.execute("SELECT id FROM exams WHERE id = %s", (exam_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Exam not found"}), 404
        
        # Delete exam (cascade will delete questions and results)
        cursor.execute("DELETE FROM exams WHERE id = %s", (exam_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Exam deleted successfully"})
        
    except Error as e:
        print(f"Delete exam error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Update exam
@app.route('/api/admin/exam/<int:exam_id>', methods=['PUT'])
def update_exam(exam_id):
    try:
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update exam details
        cursor.execute('''
            UPDATE exams 
            SET title = %s, subject = %s, duration_minutes = %s, total_marks = %s
            WHERE id = %s
        ''', (
            data.get('title'),
            data.get('subject'),
            data.get('duration_minutes'),
            data.get('total_marks'),
            exam_id
        ))
        
        # Update questions if provided
        if 'questions' in data:
            # Delete existing questions
            cursor.execute("DELETE FROM questions WHERE exam_id = %s", (exam_id,))
            
            # Insert new questions
            for question in data['questions']:
                cursor.execute('''
                    INSERT INTO questions 
                    (exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer, marks)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    exam_id,
                    question['question_text'],
                    question.get('option_a'),
                    question.get('option_b'),
                    question.get('option_c'),
                    question.get('option_d'),
                    question['correct_answer'],
                    question['marks']
                ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Exam updated successfully"})
        
    except Error as e:
        print(f"Update exam error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Verify student account
@app.route('/api/admin/student/<int:student_id>/verify', methods=['POST'])
def verify_student(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users 
            SET is_verified = TRUE 
            WHERE id = %s AND role = 'student'
        """, (student_id,))
        
        conn.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"error": "Student not found"}), 404
        
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Student verified successfully"})
        
    except Error as e:
        print(f"Verify student error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Get captured photos for an exam attempt
@app.route('/api/admin/attempt/<int:attempt_id>/photos', methods=['GET'])
def get_attempt_photos(attempt_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT * FROM captured_photos 
            WHERE exam_result_id = %s 
            ORDER BY timestamp
        ''', (attempt_id,))
        
        photos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(photos)
        
    except Error as e:
        print(f"Get photos error: {e}")
        return jsonify({"error": "Database error occurred"}), 500


# Delete student
@app.route('/api/admin/student/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if student exists
        cursor.execute("SELECT id FROM users WHERE id = %s AND role = 'student'", (student_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Student not found"}), 404
        
        # Delete student (cascade will delete their exam results)
        cursor.execute("DELETE FROM users WHERE id = %s", (student_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Student deleted successfully"})
        
    except Error as e:
        print(f"Delete student error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Bulk verify students
@app.route('/api/admin/students/bulk-verify', methods=['POST'])
def bulk_verify_students():
    try:
        data = request.json
        
        if not data.get('student_ids') or not isinstance(data['student_ids'], list):
            return jsonify({"error": "student_ids array is required"}), 400
        
        student_ids = data['student_ids']
        
        if len(student_ids) == 0:
            return jsonify({"error": "No student IDs provided"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create placeholders for SQL query
        placeholders = ', '.join(['%s'] * len(student_ids))
        
        # Update multiple students
        cursor.execute(f"""
            UPDATE users 
            SET is_verified = TRUE 
            WHERE id IN ({placeholders}) AND role = 'student'
        """, tuple(student_ids))
        
        updated_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": f"Successfully verified {updated_count} student(s)",
            "verified_count": updated_count
        })
        
    except Error as e:
        print(f"Bulk verify error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Send email to students
@app.route('/api/admin/students/send-email', methods=['POST'])
def send_email_to_students():
    try:
        data = request.json
        
        required_fields = ['subject', 'message', 'student_ids']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400
        
        subject = data['subject']
        message = data['message']
        student_ids = data['student_ids']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get student emails
        if student_ids == ['all']:
            cursor.execute("SELECT email, name FROM users WHERE role = 'student'")
        else:
            placeholders = ', '.join(['%s'] * len(student_ids))
            cursor.execute(f"""
                SELECT email, name FROM users 
                WHERE id IN ({placeholders}) AND role = 'student'
            """, tuple(student_ids))
        
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if len(students) == 0:
            return jsonify({"error": "No students found"}), 404
        
        # In a real application, you would send emails here
        # For demo, we'll just return the email details
        
        email_list = [student['email'] for student in students]
        
        return jsonify({
            "message": f"Email prepared for {len(students)} student(s)",
            "subject": subject,
            "message_preview": message[:100] + "..." if len(message) > 100 else message,
            "recipient_count": len(students),
            "recipients": email_list[:10],  # Return first 10 emails
            "note": "In production, this would actually send emails using SMTP"
        })
        
    except Error as e:
        print(f"Send email error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Performance report
@app.route('/api/admin/reports/performance', methods=['GET'])
def get_performance_report():
    try:
        # Get query parameters
        date_from = request.args.get('date_from', None)
        date_to = request.args.get('date_to', None)
        exam_id = request.args.get('exam_id', None)
        student_id = request.args.get('student_id', None)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Build query dynamically based on filters
        query = """
            SELECT 
                er.id as attempt_id,
                er.score,
                er.total_marks,
                er.violations,
                er.start_time,
                er.end_time,
                er.status,
                ROUND((er.score / er.total_marks) * 100, 2) as percentage,
                TIMESTAMPDIFF(MINUTE, er.start_time, er.end_time) as duration_minutes,
                e.id as exam_id,
                e.title as exam_title,
                e.subject as exam_subject,
                u.id as student_id,
                u.name as student_name,
                u.email as student_email
            FROM exam_results er
            JOIN exams e ON er.exam_id = e.id
            JOIN users u ON er.student_id = u.id
            WHERE 1=1
        """
        
        params = []
        
        if date_from:
            query += " AND er.end_time >= %s"
            params.append(date_from)
        
        if date_to:
            query += " AND er.end_time <= %s"
            params.append(date_to + " 23:59:59")
        
        if exam_id and exam_id != 'all':
            query += " AND e.id = %s"
            params.append(int(exam_id))
        
        if student_id and student_id != 'all':
            query += " AND u.id = %s"
            params.append(int(student_id))
        
        query += " ORDER BY er.end_time DESC"
        
        cursor.execute(query, tuple(params))
        results = cursor.fetchall()
        
        # Calculate statistics
        total_attempts = len(results)
        total_score = sum(r['score'] for r in results)
        total_possible = sum(r['total_marks'] for r in results)
        avg_percentage = (total_score / total_possible * 100) if total_possible > 0 else 0
        
        # Pass count (assuming 40% passing)
        pass_count = sum(1 for r in results if (r['score'] / r['total_marks'] * 100) >= 40)
        pass_rate = (pass_count / total_attempts * 100) if total_attempts > 0 else 0
        
        # Subject-wise performance
        subject_performance = {}
        for result in results:
            subject = result['exam_subject']
            if subject not in subject_performance:
                subject_performance[subject] = {
                    'total_attempts': 0,
                    'total_score': 0,
                    'total_marks': 0,
                    'pass_count': 0
                }
            
            subject_performance[subject]['total_attempts'] += 1
            subject_performance[subject]['total_score'] += result['score']
            subject_performance[subject]['total_marks'] += result['total_marks']
            
            if (result['score'] / result['total_marks'] * 100) >= 40:
                subject_performance[subject]['pass_count'] += 1
        
        # Calculate subject averages
        subject_summary = []
        for subject, data in subject_performance.items():
            avg_score = (data['total_score'] / data['total_marks'] * 100) if data['total_marks'] > 0 else 0
            pass_rate = (data['pass_count'] / data['total_attempts'] * 100) if data['total_attempts'] > 0 else 0
            
            subject_summary.append({
                'subject': subject,
                'attempts': data['total_attempts'],
                'average_score': round(avg_score, 2),
                'pass_rate': round(pass_rate, 2)
            })
        
        # Top performers
        top_performers = sorted(results, key=lambda x: x['percentage'], reverse=True)[:10]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "summary": {
                "total_attempts": total_attempts,
                "average_percentage": round(avg_percentage, 2),
                "pass_rate": round(pass_rate, 2),
                "total_students": len(set(r['student_id'] for r in results)),
                "total_exams": len(set(r['exam_id'] for r in results))
            },
            "subject_performance": subject_summary,
            "top_performers": top_performers[:5],
            "recent_attempts": results[:20],
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to,
                "exam_id": exam_id,
                "student_id": student_id
            }
        })
        
    except Error as e:
        print(f"Performance report error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Attendance report
@app.route('/api/admin/reports/attendance', methods=['GET'])
def get_attendance_report():
    try:
        date_from = request.args.get('date_from', None)
        date_to = request.args.get('date_to', None)
        exam_id = request.args.get('exam_id', None)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all exams in the period
        exam_query = """
            SELECT 
                e.id,
                e.title,
                e.subject,
                e.created_at,
                COUNT(DISTINCT er.id) as attempts_count,
                COUNT(DISTINCT er.student_id) as students_count
            FROM exams e
            LEFT JOIN exam_results er ON e.id = er.exam_id
            WHERE 1=1
        """
        
        exam_params = []
        
        if date_from:
            exam_query += " AND e.created_at >= %s"
            exam_params.append(date_from)
        
        if date_to:
            exam_query += " AND e.created_at <= %s"
            exam_params.append(date_to + " 23:59:59")
        
        if exam_id and exam_id != 'all':
            exam_query += " AND e.id = %s"
            exam_params.append(int(exam_id))
        
        exam_query += " GROUP BY e.id ORDER BY e.created_at DESC"
        
        cursor.execute(exam_query, tuple(exam_params))
        exams = cursor.fetchall()
        
        # Get total students
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'student'")
        total_students = cursor.fetchone()['total']
        
        # Calculate attendance rates
        for exam in exams:
            if total_students > 0:
                exam['attendance_rate'] = round((exam['students_count'] / total_students) * 100, 2)
            else:
                exam['attendance_rate'] = 0
            
            if exam['attempts_count'] > 0:
                # Get completion rate
                cursor.execute("""
                    SELECT COUNT(*) as completed_count 
                    FROM exam_results 
                    WHERE exam_id = %s AND status = 'completed'
                """, (exam['id'],))
                completed_count = cursor.fetchone()['completed_count']
                exam['completion_rate'] = round((completed_count / exam['attempts_count']) * 100, 2)
            else:
                exam['completion_rate'] = 0
        
        cursor.close()
        conn.close()
        
        total_exams = len(exams)
        total_attempts = sum(e['attempts_count'] for e in exams)
        avg_attendance = sum(e['attendance_rate'] for e in exams) / total_exams if total_exams > 0 else 0
        avg_completion = sum(e['completion_rate'] for e in exams) / total_exams if total_exams > 0 else 0
        
        return jsonify({
            "summary": {
                "total_exams": total_exams,
                "total_students": total_students,
                "total_attempts": total_attempts,
                "average_attendance_rate": round(avg_attendance, 2),
                "average_completion_rate": round(avg_completion, 2)
            },
            "exams": exams,
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to,
                "exam_id": exam_id
            }
        })
        
    except Error as e:
        print(f"Attendance report error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Violation report

@app.route('/api/admin/reports/violations', methods=['GET'])
def get_violation_report():
    try:
        date_from = request.args.get('date_from', None)
        date_to = request.args.get('date_to', None)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Build query for violations
        query = """
            SELECT 
                er.id as attempt_id,
                er.violations,
                er.start_time,
                er.end_time,
                e.title as exam_title,
                e.subject as exam_subject,
                u.name as student_name,
                u.email as student_email,
                cp.timestamp as violation_time,
                cp.violations_detected
            FROM exam_results er
            JOIN exams e ON er.exam_id = e.id
            JOIN users u ON er.student_id = u.id
            LEFT JOIN captured_photos cp ON er.id = cp.exam_result_id
            WHERE er.violations > 0
        """
        
        params = []
        
        if date_from:
            query += " AND er.end_time >= %s"
            params.append(date_from)
        
        if date_to:
            query += " AND er.end_time <= %s"
            params.append(date_to + " 23:59:59")
        
        query += " ORDER BY er.end_time DESC"
        
        cursor.execute(query, tuple(params))
        violations = cursor.fetchall()
        
        # Parse violations_detected JSON
        for violation in violations:
            if violation['violations_detected']:
                try:
                    violation['violations_list'] = json.loads(violation['violations_detected'])
                except:
                    violation['violations_list'] = []
            else:
                violation['violations_list'] = []
        
        # Count violation types
        violation_types = {}
        for violation in violations:
            for v_type in violation['violations_list']:
                if v_type in violation_types:
                    violation_types[v_type] += 1
                else:
                    violation_types[v_type] = 1
        
        # Count by exam
        exam_violations = {}
        for violation in violations:
            exam_title = violation['exam_title']
            if exam_title in exam_violations:
                exam_violations[exam_title] += violation['violations']
            else:
                exam_violations[exam_title] = violation['violations']
        
        # Count by student
        student_violations = {}
        for violation in violations:
            student_name = violation['student_name']
            if student_name in student_violations:
                student_violations[student_name] += violation['violations']
            else:
                student_violations[student_name] = violation['violations']
        
        total_violations = sum(v['violations'] for v in violations)
        flagged_attempts = len(violations)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "summary": {
                "total_violations": total_violations,
                "flagged_attempts": flagged_attempts,
                "unique_students": len(student_violations),
                "unique_exams": len(exam_violations)
            },
            "violation_types": violation_types,
            "exam_violations": exam_violations,
            "student_violations": student_violations,
            "recent_violations": violations[:50],
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to
            }
        })
        
    except Error as e:
        print(f"Violation report error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# System usage report
@app.route('/api/admin/reports/usage', methods=['GET'])
def get_usage_report():
    try:
        date_from = request.args.get('date_from', None)
        date_to = request.args.get('date_to', None)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Daily activity
        daily_query = """
            SELECT 
                DATE(er.end_time) as date,
                COUNT(DISTINCT er.student_id) as active_students,
                COUNT(DISTINCT er.id) as exam_attempts,
                COUNT(DISTINCT e.id) as exams_taken,
                HOUR(er.end_time) as peak_hour
            FROM exam_results er
            JOIN exams e ON er.exam_id = e.id
            WHERE 1=1
        """
        
        params = []
        
        if date_from:
            daily_query += " AND er.end_time >= %s"
            params.append(date_from)
        
        if date_to:
            daily_query += " AND er.end_time <= %s"
            params.append(date_to + " 23:59:59")
        
        daily_query += " GROUP BY DATE(er.end_time) ORDER BY date DESC LIMIT 30"
        
        cursor.execute(daily_query, tuple(params))
        daily_activity = cursor.fetchall()
        
        # User statistics
        cursor.execute("""
            SELECT 
                role,
                COUNT(*) as count,
                COUNT(CASE WHEN is_verified = 1 THEN 1 END) as verified_count,
                MIN(created_at) as first_registration,
                MAX(created_at) as last_registration
            FROM users 
            GROUP BY role
        """)
        user_stats = cursor.fetchall()
        
        # Storage usage (estimate)
        cursor.execute("""
            SELECT 
                'users' as type,
                COUNT(*) as count,
                COUNT(*) * 0.001 as storage_mb
            FROM users
            UNION ALL
            SELECT 
                'exams' as type,
                COUNT(*) as count,
                COUNT(*) * 0.01 as storage_mb
            FROM exams
            UNION ALL
            SELECT 
                'exam_results' as type,
                COUNT(*) as count,
                COUNT(*) * 0.005 as storage_mb
            FROM exam_results
            UNION ALL
            SELECT 
                'captured_photos' as type,
                COUNT(*) as count,
                COUNT(*) * 0.1 as storage_mb
            FROM captured_photos
        """)
        storage_data = cursor.fetchall()
        
        total_storage = sum(item['storage_mb'] for item in storage_data)
        
        # Peak hours analysis
        cursor.execute("""
            SELECT 
                HOUR(end_time) as hour,
                COUNT(*) as attempts_count
            FROM exam_results 
            WHERE end_time IS NOT NULL
            GROUP BY HOUR(end_time)
            ORDER BY attempts_count DESC
            LIMIT 5
        """)
        peak_hours = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        total_days = len(daily_activity)
        total_attempts = sum(d['exam_attempts'] for d in daily_activity)
        avg_daily_attempts = total_attempts / total_days if total_days > 0 else 0
        
        return jsonify({
            "summary": {
                "total_storage_mb": round(total_storage, 2),
                "total_days_analyzed": total_days,
                "total_attempts": total_attempts,
                "average_daily_attempts": round(avg_daily_attempts, 2),
                "peak_usage_hours": peak_hours
            },
            "user_statistics": user_stats,
            "storage_breakdown": storage_data,
            "daily_activity": daily_activity,
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to
            }
        })
        
    except Error as e:
        print(f"Usage report error: {e}")
        return jsonify({"error": "Database error occurred"}), 500

# Settings management
# Store settings in a dictionary (in production, use database)
system_settings = {
    "general": {
        "system_name": "Exam Proctoring System",
        "system_url": "http://localhost:5000",
        "time_zone": "IST",
        "date_format": "DD/MM/YYYY",
        "language": "en",
        "maintenance_mode": False
    },
    "exams": {
        "default_duration": 60,
        "default_marks": 100,
        "auto_submit": True,
        "photo_interval": 5,
        "max_violations": 3,
        "allow_retake": False,
        "show_results": True,
        "passing_percentage": 40
    },
    "security": {
        "require_verification": True,
        "enable_2fa": False,
        "password_policy": "medium",
        "session_timeout": 30,
        "max_login_attempts": 5,
        "ip_whitelist": "",
        "enable_https": True,
        "api_rate_limit": 100
    },
    "notifications": {
        "email_enabled": True,
        "email_host": "",
        "email_port": 587,
        "email_username": "",
        "email_password": "",
        "send_welcome_email": True,
        "send_exam_reminders": True,
        "send_results_email": True
    }
}

# Get all settings
@app.route('/api/admin/settings', methods=['GET'])
def get_settings():
    try:
        category = request.args.get('category', None)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if category:
            cursor.execute("SELECT * FROM system_settings WHERE category = %s", (category,))
        else:
            cursor.execute("SELECT * FROM system_settings")
        
        settings_rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert to nested dictionary
        settings_dict = {}
        for row in settings_rows:
            cat = row['category']
            key = row['setting_key']
            value = row['setting_value']
            
            # Convert value based on type
            if row['setting_type'] == 'number':
                value = float(value) if '.' in value else int(value)
            elif row['setting_type'] == 'boolean':
                value = value.lower() in ('true', '1', 'yes')
            
            if cat not in settings_dict:
                settings_dict[cat] = {}
            settings_dict[cat][key] = value
        
        return jsonify(settings_dict)
        
    except Error as e:
        print(f"Get settings error: {e}")
        return jsonify({"error": "Error retrieving settings"}), 500

# Update settings
@app.route('/api/admin/settings', methods=['PUT'])
def update_settings():
    try:
        data = request.json
        
        if not data.get('category') or not data.get('settings'):
            return jsonify({"error": "category and settings are required"}), 400
        
        category = data['category']
        new_settings = data['settings']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for key, value in new_settings.items():
            # Determine type
            if isinstance(value, bool):
                setting_type = 'boolean'
                db_value = '1' if value else '0'
            elif isinstance(value, (int, float)):
                setting_type = 'number'
                db_value = str(value)
            else:
                setting_type = 'string'
                db_value = str(value)
            
            # Update or insert
            cursor.execute("""
                INSERT INTO system_settings (category, setting_key, setting_value, setting_type)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                setting_value = VALUES(setting_value),
                setting_type = VALUES(setting_type)
            """, (category, key, db_value, setting_type))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Settings updated successfully",
            "category": category,
            "updated_count": len(new_settings)
        })
        
    except Error as e:
        print(f"Update settings error: {e}")
        return jsonify({"error": "Error updating settings"}), 500

# Backup system data
@app.route('/api/admin/system/backup', methods=['POST'])
def backup_system():
    try:
        data = request.json
        backup_type = data.get('type', 'full')  # full, partial
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        backup_data = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if backup_type in ['full', 'users']:
            cursor.execute("SELECT * FROM users")
            backup_data['users'] = cursor.fetchall()
        
        if backup_type in ['full', 'exams']:
            cursor.execute("SELECT * FROM exams")
            backup_data['exams'] = cursor.fetchall()
        
        if backup_type in ['full', 'questions']:
            cursor.execute("SELECT * FROM questions")
            backup_data['questions'] = cursor.fetchall()
        
        if backup_type in ['full', 'results']:
            cursor.execute("SELECT * FROM exam_results")
            backup_data['exam_results'] = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # In production, you would save this to a file or cloud storage
        # For demo, we'll just return the data count
        
        total_records = sum(len(data) for data in backup_data.values())
        
        return jsonify({
            "message": f"Backup created successfully",
            "backup_id": f"backup_{timestamp}",
            "backup_type": backup_type,
            "timestamp": timestamp,
            "total_records": total_records,
            "tables_backed_up": list(backup_data.keys()),
            "note": "In production, this would save to a file or cloud storage"
        })
        
    except Error as e:
        print(f"Backup error: {e}")
        return jsonify({"error": "Error creating backup"}), 500

# Restore system data
@app.route('/api/admin/system/restore', methods=['POST'])
def restore_system():
    try:
        data = request.json
        
        # In a real application, you would:
        # 1. Upload backup file
        # 2. Validate backup data
        # 3. Restore to database
        
        # For demo purposes, we'll just return a success message
        backup_id = data.get('backup_id', 'unknown')
        
        return jsonify({
            "message": f"Restore initiated for backup: {backup_id}",
            "status": "pending",
            "note": "In production, this would restore data from backup file to database"
        })
        
    except Error as e:
        print(f"Restore error: {e}")
        return jsonify({"error": "Error restoring backup"}), 500

# Clear all system data (DANGEROUS - use with caution)
@app.route('/api/admin/system/clear-data', methods=['POST'])
def clear_all_data():
    try:
        data = request.json
        confirmation = data.get('confirmation', '')
        
        if confirmation != 'DELETE ALL':
            return jsonify({"error": "Confirmation phrase 'DELETE ALL' is required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Clear tables in correct order (due to foreign keys)
        tables = ['captured_photos', 'exam_results', 'questions', 'exams', 'users']
        
        for table in tables:
            if table == 'users':
                # Keep admin users
                cursor.execute("DELETE FROM users WHERE role = 'student'")
            else:
                cursor.execute(f"DELETE FROM {table}")
        
        conn.commit()
        
        # Reset auto-increment counters
        for table in tables:
            cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")
        
        conn.commit()
        
        # Re-add admin user
        cursor.execute("""
            INSERT IGNORE INTO users (name, email, password, role, is_verified) 
            VALUES ('Admin User', 'admin@example.com', SHA2('admin123', 256), 'admin', TRUE)
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "All data cleared successfully. System reset to initial state.",
            "admin_credentials": {
                "email": "admin@example.com",
                "password": "admin123"
            }
        })
        
    except Error as e:
        print(f"Clear data error: {e}")
        return jsonify({"error": "Error clearing data"}), 500

# Add more routes as needed...

@app.route("/api/exam/submit", methods=["POST"])
def submit_exam():
    try:
        data = request.json

        student_id = data.get("student_id")
        exam_id = data.get("exam_id")
        answers = data.get("answers")   # comes from frontend JS

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch correct answers
        cursor.execute(
            "SELECT correct_answer, marks FROM questions WHERE exam_id = %s",
            (exam_id,)
        )
        questions = cursor.fetchall()

        score = 0
        total_marks = 0

        # Answer evaluation (index-based, same as frontend)
        for index, q in enumerate(questions):
            total_marks += q["marks"]
            if str(index) in answers and answers[str(index)] == q["correct_answer"]:
                score += q["marks"]

        # Update exam_results
        cursor.execute(
            """
            UPDATE exam_results
            SET score = %s,
                total_marks = %s,
                end_time = %s,
                status = 'completed'
            WHERE student_id = %s AND exam_id = %s
            """,
            (score, total_marks, datetime.now(), student_id, exam_id)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Exam submitted successfully",
            "score": score,
            "total_marks": total_marks
        })

    except Exception as e:
        print("Submit Exam Error:", e)
        return jsonify({"success": False, "error": "Exam submission failed"}), 500


if __name__ == '__main__':
    print("🚀 Starting Exam Proctoring System...")
    print("📡 API will be available at: http://localhost:5000")
    print("📊 Test database connection: http://localhost:5000/api/test")
    print("👥 View users: http://localhost:5000/api/users")
    app.run(debug=True, port=5000)

