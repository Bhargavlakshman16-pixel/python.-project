from datetime import date, timedelta
from backend.database import db
import logging

logger = logging.getLogger("DataSeeder")

SAMPLE_BOOKS = [
    ("978-0131103627", "The C Programming Language", "Brian W. Kernighan, Dennis M. Ritchie", "Computer Science", 3, 5),
    ("978-0262033848", "Introduction to Algorithms (CLRS)", "Thomas H. Cormen, Charles E. Leiserson", "Computer Science", 1, 4),
    ("978-0132350884", "Clean Code: A Handbook of Agile Craftsmanship", "Robert C. Martin", "Computer Science", 2, 4),
    ("978-0596007126", "Head First Design Patterns", "Eric Freeman, Elisabeth Robson", "Computer Science", 2, 3),
    ("978-0321573513", "Algorithms (4th Edition)", "Robert Sedgewick, Kevin Wayne", "Computer Science", 3, 3),
    ("978-0134685991", "Effective Java", "Joshua Bloch", "Computer Science", 1, 3),
    ("978-0471543978", "Calculus: Early Transcendentals", "Howard Anton, Irl C. Bivens", "Mathematics", 4, 5),
    ("978-0134689470", "Linear Algebra and Its Applications", "David C. Lay, Steven R. Lay", "Mathematics", 2, 4),
    ("978-0387953854", "Principles of Mathematical Analysis", "Walter Rudin", "Mathematics", 1, 2),
    ("978-0061120084", "To Kill a Mockingbird", "Harper Lee", "Literature", 3, 4),
    ("978-0451524935", "1984", "George Orwell", "Literature", 2, 4),
    ("978-0743273565", "The Great Gatsby", "F. Scott Fitzgerald", "Literature", 1, 3),
    ("978-0131495081", "University Physics with Modern Physics", "Hugh D. Young, Roger A. Freedman", "Physics", 2, 4),
    ("978-0470458310", "Fundamentals of Physics", "David Halliday, Robert Resnick", "Physics", 3, 5),
    ("978-0073523170", "Principles of Economics", "N. Gregory Mankiw", "Economics", 2, 3),
    ("978-0143127741", "Thinking, Fast and Slow", "Daniel Kahneman", "Psychology", 1, 3)
]

SAMPLE_BORROWERS = [
    ("bhargav", "25102a040", "Admin", "bhargav@library.admin", "9876543200", "admin123"),
    ("Aarav Sharma", "STU101", "Student", "aarav.sharma@college.edu", "9876543210", "123456"),
    ("Diya Patel", "STU102", "Student", "diya.patel@college.edu", "9876543211", "123456"),
    ("Rohan Verma", "STU103", "Student", "rohan.verma@college.edu", "9876543212", "123456"),
    ("Prof. Vikram Rao", "TCH201", "Teacher", "vikram.rao@faculty.edu", "9876543213", "123456"),
    ("Dr. Ananya Iyer", "TCH202", "Teacher", "ananya.iyer@faculty.edu", "9876543214", "123456"),
    ("Sneha Kulkarni", "TCH203", "Teacher", "sneha.k@faculty.edu", "9876543215", "123456"),
    ("Rajesh Mehta", "BIZ301", "Business Man", "rajesh.mehta@enterprise.com", "9876543216", "123456"),
    ("Sanjay Singhania", "BIZ302", "Business Man", "sanjay.s@corp.com", "9876543217", "123456")
]

def seed_sample_data(force: bool = False):
    """Populates initial realistic demo data if tables are empty or forced."""
    existing_books = db.fetch_all("SELECT COUNT(*) as count FROM books")
    book_count = existing_books[0]["count"] if existing_books else 0

    if book_count > 0 and not force:
        logger.info("Database already contains data; skipping seed.")
        return

    if force:
        if db.active_engine == "sqlite":
            db.execute("PRAGMA foreign_keys = OFF;")
        # Clear child loans first to preserve integrity
        db.execute("DELETE FROM loans;")
        db.execute("DELETE FROM borrowers;")
        db.execute("DELETE FROM books;")
        if db.active_engine == "sqlite":
            try:
                db.execute("DELETE FROM sqlite_sequence WHERE name IN ('books', 'borrowers', 'loans');")
            except Exception:
                pass
            db.execute("PRAGMA foreign_keys = ON;")

    logger.info("Seeding books...")
    for isbn, title, author, category, copies_available, total_copies in SAMPLE_BOOKS:
        db.execute("""
            INSERT INTO books (isbn, title, author, category, copies_available, total_copies)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (isbn, title, author, category, copies_available, total_copies))

    logger.info("Seeding borrowers...")
    for name, roll_no, b_type, email, contact, pwd in SAMPLE_BORROWERS:
        db.execute("""
            INSERT INTO borrowers (borrower_name, roll_no, borrower_type, email, contact, password)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, roll_no, b_type, email, contact, pwd))

    # Calculate dates dynamically relative to current date
    today = date.today()

    # Loans across the last 5 months
    sample_loans = [
        # Returned loans (past 1-5 months)
        (1, 1, today - timedelta(days=120), today - timedelta(days=106), today - timedelta(days=107), "RETURNED"),
        (2, 2, today - timedelta(days=110), today - timedelta(days=96), today - timedelta(days=97), "RETURNED"),
        (3, 3, today - timedelta(days=95), today - timedelta(days=81), today - timedelta(days=83), "RETURNED"),
        (1, 4, today - timedelta(days=85), today - timedelta(days=71), today - timedelta(days=70), "RETURNED"),
        (2, 5, today - timedelta(days=75), today - timedelta(days=61), today - timedelta(days=62), "RETURNED"),
        (6, 6, today - timedelta(days=70), today - timedelta(days=56), today - timedelta(days=57), "RETURNED"),
        (7, 1, today - timedelta(days=60), today - timedelta(days=46), today - timedelta(days=47), "RETURNED"),
        (10, 7, today - timedelta(days=55), today - timedelta(days=41), today - timedelta(days=43), "RETURNED"),
        (1, 2, today - timedelta(days=50), today - timedelta(days=36), today - timedelta(days=38), "RETURNED"),
        (2, 3, today - timedelta(days=45), today - timedelta(days=31), today - timedelta(days=33), "RETURNED"),
        (4, 4, today - timedelta(days=40), today - timedelta(days=26), today - timedelta(days=27), "RETURNED"),
        (3, 5, today - timedelta(days=35), today - timedelta(days=21), today - timedelta(days=22), "RETURNED"),
        (11, 8, today - timedelta(days=32), today - timedelta(days=18), today - timedelta(days=20), "RETURNED"),
        (1, 6, today - timedelta(days=28), today - timedelta(days=14), today - timedelta(days=14), "RETURNED"),
        (13, 7, today - timedelta(days=25), today - timedelta(days=11), today - timedelta(days=12), "RETURNED"),
        (2, 1, today - timedelta(days=20), today - timedelta(days=6), today - timedelta(days=8), "RETURNED"),
        (8, 2, today - timedelta(days=18), today - timedelta(days=4), today - timedelta(days=5), "RETURNED"),
        (16, 3, today - timedelta(days=16), today - timedelta(days=2), today - timedelta(days=3), "RETURNED"),

        # Overdue loans (due_date is in the past, return_date is NULL)
        (2, 4, today - timedelta(days=24), today - timedelta(days=10), None, "OVERDUE"),
        (3, 5, today - timedelta(days=21), today - timedelta(days=7), None, "OVERDUE"),
        (12, 6, today - timedelta(days=18), today - timedelta(days=4), None, "OVERDUE"),

        # Active loans (due_date in the future, return_date is NULL)
        (1, 7, today - timedelta(days=5), today + timedelta(days=9), None, "ACTIVE"),
        (6, 8, today - timedelta(days=3), today + timedelta(days=11), None, "ACTIVE"),
        (8, 1, today - timedelta(days=2), today + timedelta(days=12), None, "ACTIVE"),
        (16, 2, today - timedelta(days=1), today + timedelta(days=13), None, "ACTIVE"),
    ]

    logger.info("Seeding loans...")
    for book_id, borrower_id, issue_d, due_d, ret_d, status in sample_loans:
        db.execute("""
            INSERT INTO loans (book_id, borrower_id, issue_date, due_date, return_date, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (book_id, borrower_id, issue_d.strftime("%Y-%m-%d"), due_d.strftime("%Y-%m-%d"), ret_d.strftime("%Y-%m-%d") if ret_d else None, status))

    logger.info("Database seeding complete!")

if __name__ == "__main__":
    db.init_database()
    seed_sample_data(force=True)
    print("Seed complete successfully.")
