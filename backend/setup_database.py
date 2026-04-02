# backend/setup_database.py
import mysql.connector
from mysql.connector import Error

def create_database():
    try:
        # First connect without specifying database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Opensql@nitish1234'  # Enter your MySQL password here
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS exam_proctoring")
            print("Database created successfully")
            
            # Use the database
            cursor.execute("USE exam_proctoring")
            
            # Create tables
            tables_sql = [
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role ENUM('student', 'admin') DEFAULT 'student',
                    profile_photo TEXT,
                    is_verified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS exams (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    subject VARCHAR(100),
                    duration_minutes INT,
                    total_marks INT,
                    created_by INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS questions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    exam_id INT,
                    question_text TEXT NOT NULL,
                    option_a VARCHAR(255),
                    option_b VARCHAR(255),
                    option_c VARCHAR(255),
                    option_d VARCHAR(255),
                    correct_answer CHAR(1),
                    marks INT,
                    FOREIGN KEY (exam_id) REFERENCES exams(id)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS exam_results (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id INT,
                    exam_id INT,
                    score INT,
                    total_marks INT,
                    start_time DATETIME,
                    end_time DATETIME,
                    status VARCHAR(20),
                    violations INT DEFAULT 0,
                    FOREIGN KEY (student_id) REFERENCES users(id),
                    FOREIGN KEY (exam_id) REFERENCES exams(id)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS captured_photos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    exam_result_id INT,
                    photo_data TEXT,
                    timestamp DATETIME,
                    violations_detected TEXT,
                    FOREIGN KEY (exam_result_id) REFERENCES exam_results(id)
                )
                """
            ]
            
            for sql in tables_sql:
                cursor.execute(sql)
            
            # Insert sample data
            sample_data_sql = [
                """
                INSERT INTO users (name, email, password, role, is_verified) 
                VALUES ('Admin User', 'admin@example.com', SHA2('admin123', 256), 'admin', TRUE)
                ON DUPLICATE KEY UPDATE email=email
                """,
                """
                INSERT INTO users (name, email, password, role, is_verified) 
                VALUES ('John Student', 'student@example.com', SHA2('student123', 256), 'student', TRUE)
                ON DUPLICATE KEY UPDATE email=email
                """
            ]
            
            for sql in sample_data_sql:
                cursor.execute(sql)
            
            connection.commit()
            print("Tables created and sample data inserted successfully")
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    create_database()