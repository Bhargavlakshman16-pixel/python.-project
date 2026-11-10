# Library Book Usage Analysis System 📚📊

> **A circulation management and usage analytics platform focused on library circulation, popular book identification, overdue tracking, and data visualization.**

---

## 🎯 Project Overview & Scope

The **Library Book Usage Analysis System** is designed to manage book borrowing transactions while deriving usage insights using statistical data analysis and graphical visualizations.

### 🌟 Key Features
- **Book & Borrower Records Management**: Full catalog tracking (ISBN, title, author, category, available copies) and patron records (names, roll numbers).
- **Circulation Transactions**: Issue and return books with automated date calculations and strict acceptance criteria enforcement.
- **Configurable Due Dates & Overdue Status**: Real-time calculation of overdue books, days overdue, and customizable daily penalty/fine estimates.
- **Pandas Data Summaries**: Grouping and aggregations by book category and monthly borrowing frequency.
- **NumPy Descriptive Statistics**: Mean, median, standard deviation, and percentiles for borrowing duration and circulation metrics.
- **Matplotlib Visualizations**: High-resolution charts dynamically generated on the backend:
  - *Monthly Circulation Trend* (Line + Bar overlay)
  - *Top Most-Borrowed Books* (Ranked horizontal bar chart)
  - *Category Circulation Distribution* (Donut/Pie chart)
- **Zero-Friction Dual-Engine Database Architecture**: Built with native **MySQL** schema and automated fallback to SQLite mode if MySQL credentials are not yet entered.

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | HTML5, CSS3 (Modern Glassmorphic UI), JavaScript (ES6+), React 18, Babel Standalone, FontAwesome |
| **Backend** | Python 3.13, FastAPI, Uvicorn, Pydantic |
| **Data Analysis** | **Pandas** (summaries & aggregations), **NumPy** (descriptive statistics) |
| **Visualization**| **Matplotlib** (dynamic server-side chart rendering to Base64) |
| **Database** | **MySQL** (`mysql-connector-python`) + Automatic SQLite fallback |

---

## 🗄️ Database Architecture & Entities

### 1. `books` Table
```sql
CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    copies_available INT NOT NULL DEFAULT 1,
    total_copies INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. `borrowers` Table
```sql
CREATE TABLE borrowers (
    borrower_id INT AUTO_INCREMENT PRIMARY KEY,
    borrower_name VARCHAR(255) NOT NULL,
    roll_no VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) DEFAULT NULL,
    contact VARCHAR(50) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. `loans` Table
```sql
CREATE TABLE loans (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    borrower_id INT NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE DEFAULT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books (book_id),
    FOREIGN KEY (borrower_id) REFERENCES borrowers (borrower_id)
);
```

---

## 🚀 Quick Start Guide

### 1. Clone or Open Project
Ensure you are in the project root directory:
```bash
cd "c:\Users\Bhargav Lakshman\Desktop\project"
```

### 2. Configure Database (Optional for MySQL)
Edit `.env` if you wish to connect to your local MySQL Server:
```env
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=library_db
```
*(If left empty or if MySQL is unreachable, the system automatically uses SQLite so you can evaluate the entire app immediately with zero configuration!)*

### 3. Run the Application
Launch the server and interactive UI with a single command:
```bash
python run.py
```
- **Web Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## ✅ Acceptance Criteria & Business Logic Verification

1. **Returned Book Updates Loan Status & Timestamp**:
   - Marking a book as returned sets `status = 'RETURNED'` and records the `return_date`.
2. **Consistent Available-Copy Counts**:
   - When a book is issued, `copies_available` decrements by 1 atomically.
   - When returned, `copies_available` increments by 1 (capped at `total_copies`).
3. **Rejection of Invalid Sequences**:
   - **Zero Copies Left**: Attempting to issue a book with `copies_available <= 0` is rejected with `HTTP 400 Bad Request`.
   - **Double Return**: Attempting to return a loan that has already been returned is rejected with `HTTP 400 Bad Request`.
   - **Chronology Check**: Return date cannot precede the issue date.
   - **Duplicate Active Loan**: A borrower cannot issue multiple active copies of the exact same book concurrently.

---

## 📈 Expected Outputs Demonstrated in the UI

1. **Most-Borrowed Books Report**: Ranked table of top titles by borrowing volume with borrower count and average duration, accompanied by a Matplotlib horizontal bar chart.
2. **Overdue-Loan List**: Filtered report showing all borrowers with overdue books, days overdue, and calculated fine estimates.
3. **Monthly Circulation Chart**: Matplotlib line & bar chart displaying month-over-month book borrowing trends.
4. **Category Summary**: Pandas grouping summarizing total titles, inventory, circulation counts, and category utilization rates.
