-- database_setup.sql
CREATE DATABASE IF NOT EXISTS exam_proctoring;
USE exam_proctoring;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'admin') DEFAULT 'student',
    profile_photo TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exams table
CREATE TABLE IF NOT EXISTS exams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    subject VARCHAR(100),
    duration_minutes INT,
    total_marks INT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Questions table
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
);

-- Exam results table
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
);

-- Captured photos table
CREATE TABLE IF NOT EXISTS captured_photos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_result_id INT,
    photo_data TEXT,
    timestamp DATETIME,
    violations_detected TEXT,
    FOREIGN KEY (exam_result_id) REFERENCES exam_results(id)
);

-- Insert sample data
INSERT INTO users (name, email, password, role, is_verified) VALUES
('Admin User', 'admin@example.com', SHA2('admin123', 256), 'admin', TRUE),
('John Student', 'john@example.com', SHA2('student123', 256), 'student', TRUE);

INSERT INTO exams (title, subject, duration_minutes, total_marks, created_by) VALUES
('Mathematics Final Exam', 'Mathematics', 60, 100, 1),
('Science Quiz', 'Science', 30, 50, 1);

INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer, marks) VALUES
(1, 'What is 2 + 2?', '3', '4', '5', '6', 'B', 10),
(1, 'What is the square root of 16?', '2', '3', '4', '5', 'C', 10),
(2, 'What is H2O?', 'Gold', 'Water', 'Air', 'Fire', 'B', 10);