-- ============================================================
-- Library Book Usage Analysis System
-- MySQL Initial Sample Data Seed with 3 Personas
-- Personas: Student (7 days), Teacher (14 days), Business Man (30 days)
-- ============================================================

USE library_db;

-- Insert Books
INSERT INTO books (isbn, title, author, category, copies_available, total_copies) VALUES
('978-0131103627', 'The C Programming Language', 'Brian W. Kernighan, Dennis M. Ritchie', 'Computer Science', 3, 5),
('978-0262033848', 'Introduction to Algorithms (CLRS)', 'Thomas H. Cormen, Charles E. Leiserson', 'Computer Science', 1, 4),
('978-0132350884', 'Clean Code: A Handbook of Agile Craftsmanship', 'Robert C. Martin', 'Computer Science', 2, 4),
('978-0596007126', 'Head First Design Patterns', 'Eric Freeman, Elisabeth Robson', 'Computer Science', 2, 3),
('978-0321573513', 'Algorithms', 'Robert Sedgewick, Kevin Wayne', 'Computer Science', 3, 3),
('978-0134685991', 'Effective Java', 'Joshua Bloch', 'Computer Science', 1, 3),
('978-0471543978', 'Calculus: Early Transcendentals', 'Howard Anton, Irl C. Bivens', 'Mathematics', 4, 5),
('978-0134689470', 'Linear Algebra and Its Applications', 'David C. Lay, Steven R. Lay', 'Mathematics', 2, 4),
('978-0387953854', 'Principles of Mathematical Analysis', 'Walter Rudin', 'Mathematics', 1, 2),
('978-0061120084', 'To Kill a Mockingbird', 'Harper Lee', 'Literature', 3, 4),
('978-0451524935', '1984', 'George Orwell', 'Literature', 2, 4),
('978-0743273565', 'The Great Gatsby', 'F. Scott Fitzgerald', 'Literature', 1, 3),
('978-0131495081', 'University Physics with Modern Physics', 'Hugh D. Young, Roger A. Freedman', 'Physics', 2, 4),
('978-0470458310', 'Fundamentals of Physics', 'David Halliday, Robert Resnick', 'Physics', 3, 5),
('978-0073523170', 'Principles of Economics', 'N. Gregory Mankiw', 'Economics', 2, 3),
('978-0143127741', 'Thinking, Fast and Slow', 'Daniel Kahneman', 'Psychology', 1, 3)
ON DUPLICATE KEY UPDATE title=VALUES(title);

-- Insert Borrowers with 3 Personas (Student, Teacher, Business Man)
INSERT INTO borrowers (borrower_name, roll_no, borrower_type, email, contact) VALUES
('Aarav Sharma', 'STU101', 'Student', 'aarav.sharma@college.edu', '9876543210'),
('Diya Patel', 'STU102', 'Student', 'diya.patel@college.edu', '9876543211'),
('Rohan Verma', 'STU103', 'Student', 'rohan.verma@college.edu', '9876543212'),
('Prof. Vikram Rao', 'TCH201', 'Teacher', 'vikram.rao@faculty.edu', '9876543213'),
('Dr. Ananya Iyer', 'TCH202', 'Teacher', 'ananya.iyer@faculty.edu', '9876543214'),
('Sneha Kulkarni', 'TCH203', 'Teacher', 'sneha.k@faculty.edu', '9876543215'),
('Rajesh Mehta', 'BIZ301', 'Business Man', 'rajesh.mehta@enterprise.com', '9876543216'),
('Sanjay Singhania', 'BIZ302', 'Business Man', 'sanjay.s@corp.com', '9876543217')
ON DUPLICATE KEY UPDATE borrower_name=VALUES(borrower_name);

-- Insert Historical and Active Loans
INSERT INTO loans (book_id, borrower_id, issue_date, due_date, return_date, status) VALUES
(1, 1, '2026-06-05', '2026-06-12', '2026-06-11', 'RETURNED'),
(2, 2, '2026-06-12', '2026-06-19', '2026-06-18', 'RETURNED'),
(3, 4, '2026-06-20', '2026-07-04', '2026-07-02', 'RETURNED'),
(1, 7, '2026-07-02', '2026-08-01', '2026-07-28', 'RETURNED'),
(2, 5, '2026-07-08', '2026-07-22', '2026-07-21', 'RETURNED'),
(6, 6, '2026-07-15', '2026-07-29', '2026-07-28', 'RETURNED'),
(7, 1, '2026-08-01', '2026-08-08', '2026-08-07', 'RETURNED'),
(10, 8, '2026-08-04', '2026-09-03', '2026-09-01', 'RETURNED'),
(1, 2, '2026-08-10', '2026-08-17', '2026-08-16', 'RETURNED'),
(2, 3, '2026-08-18', '2026-08-25', '2026-08-24', 'RETURNED'),
(4, 4, '2026-08-25', '2026-09-08', '2026-09-07', 'RETURNED'),
(3, 5, '2026-09-02', '2026-09-16', '2026-09-15', 'RETURNED'),
(11, 7, '2026-09-10', '2026-10-10', '2026-10-08', 'RETURNED'),
(1, 6, '2026-09-15', '2026-09-29', '2026-09-28', 'RETURNED'),
(13, 8, '2026-09-22', '2026-10-22', '2026-10-21', 'RETURNED'),
(2, 1, '2026-10-02', '2026-10-09', '2026-10-08', 'RETURNED'),
(8, 2, '2026-10-08', '2026-10-15', '2026-10-14', 'RETURNED'),
(16, 3, '2026-10-14', '2026-10-21', '2026-10-20', 'RETURNED'),

-- Overdue Loans
(2, 1, '2026-10-10', '2026-10-17', NULL, 'OVERDUE'),
(3, 4, '2026-10-05', '2026-10-19', NULL, 'OVERDUE'),
(12, 7, '2026-09-20', '2026-10-20', NULL, 'OVERDUE'),

-- Active Loans
(1, 2, '2026-10-31', '2026-11-07', NULL, 'ACTIVE'),
(6, 5, '2026-10-25', '2026-11-08', NULL, 'ACTIVE'),
(8, 8, '2026-10-15', '2026-11-14', NULL, 'ACTIVE'),
(16, 3, '2026-11-01', '2026-11-08', NULL, 'ACTIVE');
