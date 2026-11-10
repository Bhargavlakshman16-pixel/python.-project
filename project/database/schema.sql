-- ============================================================
-- Library Book Usage Analysis System
-- MySQL Database Schema
-- Entities: books, borrowers, loans
-- ============================================================

CREATE DATABASE IF NOT EXISTS library_db;
USE library_db;

-- 1. Table: books
CREATE TABLE IF NOT EXISTS books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    copies_available INT NOT NULL DEFAULT 1,
    total_copies INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Table: borrowers
CREATE TABLE IF NOT EXISTS borrowers (
    borrower_id INT AUTO_INCREMENT PRIMARY KEY,
    borrower_name VARCHAR(255) NOT NULL,
    roll_no VARCHAR(50) NOT NULL UNIQUE,
    borrower_type VARCHAR(50) NOT NULL DEFAULT 'Student', -- Student, Teacher, Business Man, Admin
    email VARCHAR(255) DEFAULT NULL,
    contact VARCHAR(50) DEFAULT NULL,
    password VARCHAR(255) DEFAULT '123456',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 3. Table: loans
CREATE TABLE IF NOT EXISTS loans (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    borrower_id INT NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE DEFAULT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_loans_book FOREIGN KEY (book_id) REFERENCES books (book_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_loans_borrower FOREIGN KEY (borrower_id) REFERENCES borrowers (borrower_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Indexes for quick analytics and filtering
CREATE INDEX idx_loans_issue_date ON loans(issue_date);
CREATE INDEX idx_loans_status ON loans(status);
CREATE INDEX idx_books_category ON books(category);
CREATE INDEX idx_borrowers_type ON borrowers(borrower_type);
