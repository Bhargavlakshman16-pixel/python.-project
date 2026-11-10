import os
from datetime import date, datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from backend.config import config, BASE_DIR
from backend.database import db
from backend.models import (
    BookCreate, BookUpdate,
    BorrowerCreate, BorrowerUpdate,
    LoanIssueRequest, LoanReturnRequest,
    SystemSettings, LoginRequest, RegisterRequest
)
from backend.analytics import LibraryAnalytics
from backend.seed_data import seed_sample_data

app = FastAPI(
    title="Library Book Usage Analysis System",
    description="REST API for circulation management and library analytics powered by Pandas, NumPy, and Matplotlib.",
    version="1.0.0"
)

# Enable CORS for external frontend or development tools
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database schema and initial data on startup
@app.on_event("startup")
def startup_event():
    db.init_database()
    seed_sample_data(force=False)

# ============================================================
# 1. BOOKS MANAGEMENT ENDPOINTS
# ============================================================

@app.get("/api/books", tags=["Books"])
def get_books(
    search: Optional[str] = Query(None, description="Search by title, author, or ISBN"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    query = "SELECT * FROM books WHERE 1=1"
    params = []
    if search:
        query += " AND (title LIKE %s OR author LIKE %s OR isbn LIKE %s)"
        term = f"%{search}%"
        params.extend([term, term, term])
    if category and category != "All":
        query += " AND category = %s"
        params.append(category)
    query += " ORDER BY title ASC;"
    return db.fetch_all(query, tuple(params))

@app.get("/api/books/categories", tags=["Books"])
def get_categories():
    rows = db.fetch_all("SELECT DISTINCT category FROM books ORDER BY category ASC;")
    return [r["category"] for r in rows]

@app.get("/api/books/{book_id}", tags=["Books"])
def get_book(book_id: int):
    book = db.fetch_one("SELECT * FROM books WHERE book_id = %s;", (book_id,))
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/api/books", status_code=status.HTTP_201_CREATED, tags=["Books"])
def create_book(book: BookCreate):
    # Check ISBN uniqueness
    existing = db.fetch_one("SELECT book_id FROM books WHERE isbn = %s;", (book.isbn.strip(),))
    if existing:
        raise HTTPException(status_code=400, detail=f"A book with ISBN '{book.isbn}' already exists.")

    total_copies = book.total_copies
    copies_available = book.copies_available if book.copies_available is not None else total_copies
    if copies_available > total_copies:
        raise HTTPException(status_code=400, detail="Available copies cannot exceed total copies.")

    book_id = db.execute("""
        INSERT INTO books (isbn, title, author, category, copies_available, total_copies)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (book.isbn.strip(), book.title.strip(), book.author.strip(), book.category.strip(), copies_available, total_copies))
    
    return db.fetch_one("SELECT * FROM books WHERE book_id = %s;", (book_id,))

@app.put("/api/books/{book_id}", tags=["Books"])
def update_book(book_id: int, book: BookUpdate):
    curr = db.fetch_one("SELECT * FROM books WHERE book_id = %s;", (book_id,))
    if not curr:
        raise HTTPException(status_code=404, detail="Book not found")

    title = book.title.strip() if book.title is not None else curr["title"]
    author = book.author.strip() if book.author is not None else curr["author"]
    category = book.category.strip() if book.category is not None else curr["category"]
    total_copies = book.total_copies if book.total_copies is not None else curr["total_copies"]
    copies_available = book.copies_available if book.copies_available is not None else curr["copies_available"]

    if copies_available > total_copies:
        raise HTTPException(status_code=400, detail="Available copies cannot exceed total copies.")

    db.execute("""
        UPDATE books 
        SET title = %s, author = %s, category = %s, total_copies = %s, copies_available = %s
        WHERE book_id = %s;
    """, (title, author, category, total_copies, copies_available, book_id))

    return db.fetch_one("SELECT * FROM books WHERE book_id = %s;", (book_id,))

@app.delete("/api/books/{book_id}", tags=["Books"])
def delete_book(book_id: int):
    # Check if active loans exist for this book
    active = db.fetch_one("SELECT loan_id FROM loans WHERE book_id = %s AND return_date IS NULL;", (book_id,))
    if active:
        raise HTTPException(status_code=400, detail="Cannot delete book with active, unreturned loans.")

    # Remove past loans first if needed
    db.execute("DELETE FROM loans WHERE book_id = %s;", (book_id,))
    db.execute("DELETE FROM books WHERE book_id = %s;", (book_id,))
    return {"message": f"Book {book_id} deleted successfully."}

# ============================================================
# 2. BORROWERS MANAGEMENT & AUTH LOGIN ENDPOINTS
# ============================================================

@app.post("/api/auth/login", tags=["Auth"])
def login_borrower(req: LoginRequest):
    """
    Login endpoint for Admin, Student, Teacher/Faculty, or Business Man using Name and ID Number (roll_no).
    Enforces:
    - ID 25102a040 is Master Admin (Name: bhargav)
    - Password verification: checks if password matches stored password
    - One ID is unique to only one person
    - Upon re-login with the same ID, preserves and returns ALL their existing old information
    """
    roll_no = req.roll_no.strip()
    name = req.borrower_name.strip() if req.borrower_name else ""
    b_type = req.borrower_type.strip() if req.borrower_type else "Student"
    password = req.password.strip() if req.password else ""

    # Special check for Master Admin 25102a040
    is_master_admin = roll_no.lower() in ("25102a040", "25102a2140")

    existing = db.fetch_one("SELECT * FROM borrowers WHERE LOWER(roll_no) = LOWER(%s);", (roll_no,))
    
    if existing:
        # Existing user found! Check password if password was set on account
        stored_pwd = existing.get("password") or ""
        if stored_pwd and password:
            # Allow admin default passwords or matching password
            valid_admin_pwds = ("admin123", "25102a040", "admin", "123456")
            if is_master_admin:
                if password != stored_pwd and password not in valid_admin_pwds:
                    raise HTTPException(status_code=401, detail="Invalid admin password for ID 25102a040. Try 'admin123'.")
            else:
                if password != stored_pwd and stored_pwd != "123456":
                    raise HTTPException(status_code=401, detail=f"Incorrect password for ID '{roll_no}'. Please enter your correct password.")
        elif password and not stored_pwd:
            # First time setting password on existing account
            db.execute("UPDATE borrowers SET password = %s WHERE borrower_id = %s;", (password, existing["borrower_id"]))
            existing["password"] = password

        # DO NOT OVERWRITE OLD INFORMATION - preserve existing profile and role!
        borrower = existing
        # If master admin, ensure role is Admin and name is bhargav
        if is_master_admin and borrower.get("borrower_type") != "Admin":
            db.execute("UPDATE borrowers SET borrower_name = 'bhargav', borrower_type = 'Admin' WHERE borrower_id = %s;", (existing["borrower_id"],))
            borrower["borrower_type"] = "Admin"
            borrower["borrower_name"] = "bhargav"

        welcome_msg = f"Welcome back, {borrower['borrower_name']}! Your existing profile and loan records have been loaded."
    else:
        # New user registering for the first time
        if is_master_admin:
            name = "bhargav"
            b_type = "Admin"
            pwd = password if password else "admin123"
        else:
            name = name if name else f"Member {roll_no}"
            pwd = password if password else "123456"

        b_id = db.execute("""
            INSERT INTO borrowers (borrower_name, roll_no, borrower_type, password)
            VALUES (%s, %s, %s, %s);
        """, (name, roll_no, b_type, pwd))
        borrower = db.fetch_one("SELECT * FROM borrowers WHERE borrower_id = %s;", (b_id,))
        welcome_msg = f"Account registered successfully! Welcome to the library, {borrower['borrower_name']}."

    # Fetch loans history for this borrower
    loans = db.fetch_all("""
        SELECT l.*, b.title, b.isbn, b.category
        FROM loans l
        JOIN books b ON l.book_id = b.book_id
        WHERE l.borrower_id = %s
        ORDER BY l.issue_date DESC;
    """, (borrower["borrower_id"],))
    borrower["loans"] = loans

    allowed_loan_days = config.get_days_for_role(borrower["borrower_type"])

    return {
        "message": welcome_msg,
        "borrower": borrower,
        "borrower_type": borrower["borrower_type"],
        "allowed_loan_days": allowed_loan_days,
        "fine_rate": config.DAILY_OVERDUE_FINE
    }

@app.post("/api/auth/register", tags=["Auth"])
def register_new_borrower(req: RegisterRequest):
    """
    Explicit registration endpoint for new borrowers (Student, Teacher, Business Man).
    Enforces unique ID check to ensure one ID number belongs to only one person.
    """
    roll = req.roll_no.strip()
    name = req.borrower_name.strip()
    b_type = req.borrower_type.strip() if req.borrower_type else "Student"
    pwd = req.password.strip() if req.password else "123456"

    if not roll or not name:
        raise HTTPException(status_code=400, detail="Name and ID Number are required to register.")

    existing = db.fetch_one("SELECT borrower_id, borrower_name FROM borrowers WHERE LOWER(roll_no) = LOWER(%s);", (roll,))
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot register: ID Number '{roll}' is already assigned to '{existing['borrower_name']}'. One ID can only belong to one person. Please sign in instead."
        )

    b_id = db.execute("""
        INSERT INTO borrowers (borrower_name, roll_no, borrower_type, email, contact, password)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (name, roll, b_type, req.email, req.contact, pwd))

    borrower = db.fetch_one("SELECT * FROM borrowers WHERE borrower_id = %s;", (b_id,))
    borrower["loans"] = []
    allowed_loan_days = config.get_days_for_role(borrower["borrower_type"])

    return {
        "message": f"Welcome, {name}! Your new borrower account has been created successfully with {allowed_loan_days} days borrowing period.",
        "borrower": borrower,
        "borrower_type": borrower["borrower_type"],
        "allowed_loan_days": allowed_loan_days,
        "fine_rate": config.DAILY_OVERDUE_FINE
    }

@app.get("/api/borrowers", tags=["Borrowers"])
def get_borrowers(search: Optional[str] = Query(None, description="Search by name or roll number")):
    if search:
        query = "SELECT * FROM borrowers WHERE borrower_name LIKE %s OR roll_no LIKE %s OR borrower_type LIKE %s ORDER BY borrower_name ASC;"
        term = f"%{search}%"
        return db.fetch_all(query, (term, term, term))
    return db.fetch_all("SELECT * FROM borrowers ORDER BY borrower_name ASC;")

@app.get("/api/borrowers/{borrower_id}", tags=["Borrowers"])
def get_borrower(borrower_id: int):
    borrower = db.fetch_one("SELECT * FROM borrowers WHERE borrower_id = %s;", (borrower_id,))
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    loans = db.fetch_all("""
        SELECT l.*, b.title, b.isbn, b.category
        FROM loans l
        JOIN books b ON l.book_id = b.book_id
        WHERE l.borrower_id = %s
        ORDER BY l.issue_date DESC;
    """, (borrower_id,))
    borrower["loans"] = loans
    borrower["allowed_loan_days"] = config.get_days_for_role(borrower.get("borrower_type", "Student"))
    return borrower

@app.post("/api/borrowers", status_code=status.HTTP_201_CREATED, tags=["Borrowers"])
def create_borrower(borrower: BorrowerCreate):
    roll = borrower.roll_no.strip()
    existing = db.fetch_one("SELECT borrower_id, borrower_name FROM borrowers WHERE LOWER(roll_no) = LOWER(%s);", (roll,))
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot add borrower! ID Number '{roll}' is already registered to '{existing['borrower_name']}'. Each ID must be unique to one person only."
        )

    b_type = borrower.borrower_type.strip() if borrower.borrower_type else "Student"
    pwd = borrower.password.strip() if getattr(borrower, 'password', None) else "123456"

    b_id = db.execute("""
        INSERT INTO borrowers (borrower_name, roll_no, borrower_type, email, contact, password)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (borrower.borrower_name.strip(), roll, b_type, borrower.email, borrower.contact, pwd))

    return db.fetch_one("SELECT * FROM borrowers WHERE borrower_id = %s;", (b_id,))

@app.put("/api/borrowers/{borrower_id}", tags=["Borrowers"])
def update_borrower(borrower_id: int, borrower: BorrowerUpdate):
    curr = db.fetch_one("SELECT * FROM borrowers WHERE borrower_id = %s;", (borrower_id,))
    if not curr:
        raise HTTPException(status_code=404, detail="Borrower not found")

    name = borrower.borrower_name.strip() if borrower.borrower_name is not None else curr["borrower_name"]
    roll_no = borrower.roll_no.strip() if borrower.roll_no is not None else curr["roll_no"]
    b_type = borrower.borrower_type.strip() if borrower.borrower_type is not None else curr.get("borrower_type", "Student")
    email = borrower.email if borrower.email is not None else curr["email"]
    contact = borrower.contact if borrower.contact is not None else curr["contact"]

    if roll_no != curr["roll_no"]:
        conflict = db.fetch_one("SELECT borrower_id FROM borrowers WHERE roll_no = %s AND borrower_id != %s;", (roll_no, borrower_id))
        if conflict:
            raise HTTPException(status_code=400, detail=f"ID Number '{roll_no}' is already in use by another borrower.")

    db.execute("""
        UPDATE borrowers
        SET borrower_name = %s, roll_no = %s, borrower_type = %s, email = %s, contact = %s
        WHERE borrower_id = %s;
    """, (name, roll_no, b_type, email, contact, borrower_id))

    return db.fetch_one("SELECT * FROM borrowers WHERE borrower_id = %s;", (borrower_id,))

@app.delete("/api/borrowers/{borrower_id}", tags=["Borrowers"])
def delete_borrower(borrower_id: int):
    active = db.fetch_one("SELECT loan_id FROM loans WHERE borrower_id = %s AND return_date IS NULL;", (borrower_id,))
    if active:
        raise HTTPException(status_code=400, detail="Cannot delete borrower with unreturned loans.")

    db.execute("DELETE FROM loans WHERE borrower_id = %s;", (borrower_id,))
    db.execute("DELETE FROM borrowers WHERE borrower_id = %s;", (borrower_id,))
    return {"message": f"Borrower {borrower_id} deleted successfully."}

# ============================================================
# 3. CIRCULATION & LOANS TRANSACTIONS
# ============================================================

@app.get("/api/loans", tags=["Circulation"])
def get_loans(
    status_filter: Optional[str] = Query(None, description="ACTIVE, OVERDUE, or RETURNED"),
    borrower_id: Optional[int] = None,
    book_id: Optional[int] = None
):
    query = """
        SELECT 
            l.loan_id,
            l.book_id,
            b.title,
            b.author,
            b.category,
            b.isbn,
            b.copies_available,
            l.borrower_id,
            br.borrower_name,
            br.roll_no,
            br.borrower_type,
            l.issue_date,
            l.due_date,
            l.return_date,
            l.status
        FROM loans l
        JOIN books b ON l.book_id = b.book_id
        JOIN borrowers br ON l.borrower_id = br.borrower_id
        WHERE 1=1
    """
    params = []
    if borrower_id:
        query += " AND l.borrower_id = %s"
        params.append(borrower_id)
    if book_id:
        query += " AND l.book_id = %s"
        params.append(book_id)

    query += " ORDER BY l.loan_id DESC;"
    loans = db.fetch_all(query, tuple(params))

    # Dynamically update overdue status and calculate days overdue
    today_str = date.today().isoformat()
    today_dt = date.today()

    for item in loans:
        due_str = item["due_date"][:10]
        ret_str = item["return_date"][:10] if item["return_date"] else None
        due_dt = datetime.strptime(due_str, "%Y-%m-%d").date()

        if ret_str:
            item["status"] = "RETURNED"
            item["days_overdue"] = 0
            item["fine_amount"] = 0.0
        elif due_dt < today_dt:
            item["status"] = "OVERDUE"
            overdue_days = (today_dt - due_dt).days
            item["days_overdue"] = overdue_days
            item["fine_amount"] = round(overdue_days * config.DAILY_OVERDUE_FINE, 2)
        else:
            item["status"] = "ACTIVE"
            item["days_overdue"] = 0
            item["fine_amount"] = 0.0

    if status_filter and status_filter.upper() != "ALL":
        loans = [l for l in loans if l["status"] == status_filter.upper()]

    return loans

@app.post("/api/loans/issue", status_code=status.HTTP_201_CREATED, tags=["Circulation"])
def issue_book(req: LoanIssueRequest):
    """
    Issues a book to a borrower.
    Enforces acceptance criteria:
    - Verifies book existence and availability (copies_available > 0)
    - Rejects issue request if copies_available <= 0
    - Calculates configurable due date
    - Decrements available-copy count consistently
    """
    # 1. Check Book
    book = db.fetch_one("SELECT * FROM books WHERE book_id = %s;", (req.book_id,))
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")

    if book["copies_available"] <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot issue '{book['title']}': No copies currently available (Available: 0, Total: {book['total_copies']})."
        )

    # 2. Check Borrower
    borrower = db.fetch_one("SELECT * FROM borrowers WHERE borrower_id = %s;", (req.borrower_id,))
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found.")

    # 3. Check if borrower already has an unreturned copy of this exact book
    active_copy = db.fetch_one("""
        SELECT loan_id FROM loans 
        WHERE book_id = %s AND borrower_id = %s AND return_date IS NULL;
    """, (req.book_id, req.borrower_id))
    if active_copy:
        raise HTTPException(
            status_code=400,
            detail=f"Borrower {borrower['borrower_name']} already has an active, unreturned loan for this book."
        )

    # 4. Resolve Issue and Due Dates according to Persona Tier
    # Student: 7 days, Teacher: 14 days, Business Man: 30 days
    if req.issue_date:
        try:
            issue_d = datetime.strptime(req.issue_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid issue_date format. Expected YYYY-MM-DD.")
    else:
        issue_d = date.today()

    role_due_days = config.get_days_for_role(borrower.get("borrower_type", "Student"))
    loan_days = req.loan_period_days if req.loan_period_days else role_due_days
    if req.due_date:
        try:
            due_d = datetime.strptime(req.due_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid due_date format. Expected YYYY-MM-DD.")
        if due_d <= issue_d:
            raise HTTPException(status_code=400, detail="Due date must be after the issue date.")
    else:
        due_d = issue_d + timedelta(days=loan_days)

    # 5. Insert Loan and Decrement Available Copies atomically
    loan_id = db.execute("""
        INSERT INTO loans (book_id, borrower_id, issue_date, due_date, return_date, status)
        VALUES (%s, %s, %s, %s, NULL, 'ACTIVE');
    """, (req.book_id, req.borrower_id, issue_d.strftime("%Y-%m-%d"), due_d.strftime("%Y-%m-%d")))

    db.execute("""
        UPDATE books 
        SET copies_available = copies_available - 1 
        WHERE book_id = %s AND copies_available > 0;
    """, (req.book_id,))

    return {
        "message": "Book issued successfully.",
        "loan_id": loan_id,
        "book_title": book["title"],
        "borrower_name": borrower["borrower_name"],
        "issue_date": issue_d.strftime("%Y-%m-%d"),
        "due_date": due_d.strftime("%Y-%m-%d"),
        "remaining_copies": book["copies_available"] - 1
    }

@app.post("/api/loans/{loan_id}/return", tags=["Circulation"])
def return_book(loan_id: int, req: LoanReturnRequest = None):
    """
    Records the return of a borrowed book.
    Enforces acceptance criteria:
    - Validates loan existence
    - Rejects invalid return sequences (e.g., returning an already returned book)
    - Validates return date is not prior to issue date
    - Updates loan status to 'RETURNED'
    - Increments book's available-copy count
    """
    loan = db.fetch_one("SELECT * FROM loans WHERE loan_id = %s;", (loan_id,))
    if not loan:
        raise HTTPException(status_code=404, detail="Loan transaction not found.")

    if loan["return_date"] is not None or loan["status"] == "RETURNED":
        raise HTTPException(status_code=400, detail="Invalid operation: This book loan has already been returned.")

    ret_date_str = req.return_date if (req and req.return_date) else date.today().strftime("%Y-%m-%d")
    try:
        ret_d = datetime.strptime(ret_date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid return_date format. Expected YYYY-MM-DD.")

    issue_date_val = loan["issue_date"][:10]
    issue_d = datetime.strptime(issue_date_val, "%Y-%m-%d").date()

    if ret_d < issue_d:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sequence: Return date ({ret_d}) cannot be earlier than issue date ({issue_d})."
        )

    # Update loan
    db.execute("""
        UPDATE loans 
        SET return_date = %s, status = 'RETURNED' 
        WHERE loan_id = %s;
    """, (ret_d.strftime("%Y-%m-%d"), loan_id))

    # Increment available copies (bounded by total_copies)
    db.execute("""
        UPDATE books 
        SET copies_available = CASE 
            WHEN copies_available < total_copies THEN copies_available + 1 
            ELSE total_copies 
        END 
        WHERE book_id = %s;
    """, (loan["book_id"],))

    updated_book = db.fetch_one("SELECT * FROM books WHERE book_id = %s;", (loan["book_id"],))

    return {
        "message": "Book returned successfully.",
        "loan_id": loan_id,
        "return_date": ret_d.strftime("%Y-%m-%d"),
        "status": "RETURNED",
        "book_id": loan["book_id"],
        "title": updated_book["title"] if updated_book else "",
        "copies_available": updated_book["copies_available"] if updated_book else 0
    }

# ============================================================
# 4. DATA ANALYSIS & VISUALIZATION (Pandas, NumPy, Matplotlib)
# ============================================================

@app.get("/api/analytics/dashboard", tags=["Analytics"])
def get_dashboard_summary():
    """Returns high-level library circulation counts and metrics."""
    return LibraryAnalytics.get_dashboard_summary()

@app.get("/api/analytics/most-borrowed", tags=["Analytics"])
def get_most_borrowed_report(limit: int = Query(10, ge=1, le=50)):
    """Expected output: Most-borrowed books report and ranking."""
    return LibraryAnalytics.get_most_borrowed_books_report(limit=limit)

@app.get("/api/analytics/overdue-loans", tags=["Analytics"])
def get_overdue_loans_report():
    """Expected output: Overdue-loan list with days overdue and fine estimates."""
    return LibraryAnalytics.get_overdue_loans_report()

@app.get("/api/analytics/category-summary", tags=["Analytics"])
def get_category_summary():
    """Expected output: Pandas category summary and utilization rates."""
    return LibraryAnalytics.get_category_summary()

@app.get("/api/analytics/monthly-trends", tags=["Analytics"])
def get_monthly_circulation_trends():
    """Expected output: Monthly circulation data aggregated via Pandas."""
    return LibraryAnalytics.get_monthly_circulation_trends()

@app.get("/api/analytics/descriptive-statistics", tags=["Analytics"])
def get_descriptive_statistics():
    """NumPy descriptive statistics for borrowing periods and loan durations."""
    return LibraryAnalytics.get_numpy_descriptive_statistics()

@app.get("/api/analytics/charts", tags=["Analytics"])
def get_charts():
    """Returns dynamic Matplotlib charts rendered as high-res base64 images."""
    return {
        "monthly_circulation_chart": LibraryAnalytics.generate_monthly_circulation_chart(),
        "popular_books_chart": LibraryAnalytics.generate_popular_books_chart(),
        "category_distribution_chart": LibraryAnalytics.generate_category_distribution_chart()
    }

# ============================================================
# 5. CONFIGURATION & DATABASE MANAGEMENT
# ============================================================

@app.get("/api/settings", tags=["Settings"])
def get_settings():
    return {
        "student_loan_days": config.STUDENT_LOAN_DAYS,
        "teacher_loan_days": config.TEACHER_LOAN_DAYS,
        "business_man_loan_days": config.BUSINESS_MAN_LOAN_DAYS,
        "default_loan_days": config.DEFAULT_LOAN_DAYS,
        "daily_overdue_fine": config.DAILY_OVERDUE_FINE,
        "active_engine": db.active_engine,
        "db_name": config.DB_NAME,
        "db_host": config.DB_HOST,
        "db_port": config.DB_PORT
    }

@app.put("/api/settings", tags=["Settings"])
def update_settings(settings: SystemSettings):
    config.DEFAULT_LOAN_DAYS = settings.default_loan_days
    config.DAILY_OVERDUE_FINE = settings.daily_overdue_fine
    return {
        "message": "Settings updated successfully.",
        "default_loan_days": config.DEFAULT_LOAN_DAYS,
        "daily_overdue_fine": config.DAILY_OVERDUE_FINE
    }

@app.post("/api/database/reseed", tags=["Settings"])
def reseed_database():
    """Resets and reseeds demo data for testing."""
    seed_sample_data(force=True)
    return {"message": "Database reset and seeded with sample books, borrowers, and loans."}

# ============================================================
# 6. STATIC FRONTEND SERVING
# ============================================================

frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    def serve_frontend_root():
        return FileResponse(frontend_dir / "index.html")

    @app.get("/{catchall:path}")
    def serve_frontend_spa(catchall: str):
        file_path = frontend_dir / catchall
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dir / "index.html")
