import sqlite3
import mysql.connector
from mysql.connector import errorcode
import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from backend.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LibraryDB")

class DatabaseManager:
    def __init__(self):
        self.active_engine = config.DB_TYPE  # 'mysql' or 'sqlite'
        self._test_and_select_engine()
        self.init_database()

    def _test_and_select_engine(self):
        """Attempts connection to MySQL. Falls back to SQLite if MySQL fails or isn't configured."""
        if self.active_engine == "mysql":
            try:
                # Try connecting to MySQL server directly
                conn = mysql.connector.connect(
                    host=config.DB_HOST,
                    port=config.DB_PORT,
                    user=config.DB_USER,
                    password=config.DB_PASSWORD,
                    connection_timeout=3
                )
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}`;")
                conn.commit()
                cursor.close()
                conn.close()
                logger.info(f"Connected to MySQL database '{config.DB_NAME}' successfully.")
                self.active_engine = "mysql"
                return
            except Exception as e:
                logger.warning(f"MySQL connection attempt failed ({e}). Falling back to SQLite mode for seamless development.")
                self.active_engine = "sqlite"
        else:
            self.active_engine = "sqlite"

    def get_connection(self):
        """Returns an active database connection."""
        if self.active_engine == "mysql":
            return mysql.connector.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                database=config.DB_NAME,
                autocommit=True
            )
        else:
            conn = sqlite3.connect(config.SQLITE_PATH)
            conn.row_factory = sqlite3.Row
            # Enable foreign keys in SQLite
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn

    def _format_query(self, query: str) -> str:
        """Adapts SQL parameter placeholders (%s for MySQL, ? for SQLite)."""
        if self.active_engine == "sqlite":
            return query.replace("%s", "?")
        return query

    def execute(self, query: str, params: tuple = ()) -> int:
        """Executes INSERT/UPDATE/DELETE and returns lastrowid or affected rows."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            formatted_query = self._format_query(query)
            cursor.execute(formatted_query, params)
            if self.active_engine == "sqlite":
                conn.commit()
                last_id = cursor.lastrowid
            else:
                last_id = cursor.lastrowid
            cursor.close()
            return last_id
        finally:
            conn.close()

    def execute_many(self, query: str, params_list: List[tuple]):
        """Executes batch queries."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            formatted_query = self._format_query(query)
            cursor.executemany(formatted_query, params_list)
            if self.active_engine == "sqlite":
                conn.commit()
            cursor.close()
        finally:
            conn.close()

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Executes a SELECT query and returns rows as dictionaries."""
        conn = self.get_connection()
        try:
            formatted_query = self._format_query(query)
            if self.active_engine == "mysql":
                cursor = conn.cursor(dictionary=True)
                cursor.execute(formatted_query, params)
                results = cursor.fetchall()
                cursor.close()
                # Convert date/datetime objects to ISO string for JSON serialization
                for row in results:
                    for k, v in row.items():
                        if isinstance(v, (date, datetime)):
                            row[k] = v.isoformat()
                return results
            else:
                cursor = conn.cursor()
                cursor.execute(formatted_query, params)
                rows = cursor.fetchall()
                results = [dict(row) for row in rows]
                cursor.close()
                return results
        finally:
            conn.close()

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Executes a SELECT query and returns a single row dictionary."""
        rows = self.fetch_all(query, params)
        return rows[0] if rows else None

    def init_database(self):
        """Initializes tables in the active database engine."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if self.active_engine == "mysql":
                cursor.execute("""
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
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS borrowers (
                        borrower_id INT AUTO_INCREMENT PRIMARY KEY,
                        borrower_name VARCHAR(255) NOT NULL,
                        roll_no VARCHAR(50) NOT NULL UNIQUE,
                        borrower_type VARCHAR(50) NOT NULL DEFAULT 'Student',
                        email VARCHAR(255) DEFAULT NULL,
                        contact VARCHAR(50) DEFAULT NULL,
                        password VARCHAR(255) DEFAULT '123456',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB;
                """)
                cursor.execute("""
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
                """)
            else:
                # SQLite Schema
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS books (
                        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        isbn TEXT NOT NULL UNIQUE,
                        title TEXT NOT NULL,
                        author TEXT NOT NULL,
                        category TEXT NOT NULL,
                        copies_available INTEGER NOT NULL DEFAULT 1,
                        total_copies INTEGER NOT NULL DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS borrowers (
                        borrower_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        borrower_name TEXT NOT NULL,
                        roll_no TEXT NOT NULL UNIQUE,
                        borrower_type TEXT NOT NULL DEFAULT 'Student',
                        email TEXT,
                        contact TEXT,
                        password TEXT DEFAULT '123456',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                # Auto-migrate if columns missing in existing SQLite database
                try:
                    cursor.execute("ALTER TABLE borrowers ADD COLUMN borrower_type TEXT DEFAULT 'Student';")
                except Exception:
                    pass
                try:
                    cursor.execute("ALTER TABLE borrowers ADD COLUMN password TEXT DEFAULT '123456';")
                except Exception:
                    pass
                    pass
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS loans (
                        loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        book_id INTEGER NOT NULL,
                        borrower_id INTEGER NOT NULL,
                        issue_date TEXT NOT NULL,
                        due_date TEXT NOT NULL,
                        return_date TEXT,
                        status TEXT NOT NULL DEFAULT 'ACTIVE',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (book_id) REFERENCES books (book_id),
                        FOREIGN KEY (borrower_id) REFERENCES borrowers (borrower_id)
                    );
                """)
                conn.commit()
            cursor.close()
            logger.info(f"Database schema initialized ({self.active_engine}).")
        finally:
            conn.close()

db = DatabaseManager()
