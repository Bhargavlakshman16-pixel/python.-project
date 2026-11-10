import io
import base64
from datetime import date, datetime
from typing import Dict, Any, List

import numpy as np
import pandas as pd
import matplotlib
# Use headless backend for Matplotlib in server environment
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from backend.database import db
from backend.config import config

def _fetch_all_loans_dataframe() -> pd.DataFrame:
    """Loads all loans joined with book and borrower details into a Pandas DataFrame."""
    query = """
        SELECT 
            l.loan_id,
            l.book_id,
            b.title,
            b.author,
            b.category,
            b.isbn,
            b.copies_available,
            b.total_copies,
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
        ORDER BY l.issue_date DESC;
    """
    data = db.fetch_all(query)
    if not data:
        return pd.DataFrame(columns=[
            "loan_id", "book_id", "title", "author", "category", "isbn",
            "copies_available", "total_copies", "borrower_id", "borrower_name",
            "roll_no", "borrower_type", "issue_date", "due_date", "return_date", "status"
        ])
    
    df = pd.DataFrame(data)
    df["issue_date"] = pd.to_datetime(df["issue_date"])
    df["due_date"] = pd.to_datetime(df["due_date"])
    df["return_date"] = pd.to_datetime(df["return_date"])

    # Calculate actual loan duration (days)
    today = pd.to_datetime(date.today())
    # If returned, duration is return_date - issue_date; if active, duration is today - issue_date
    df["duration_days"] = np.where(
        df["return_date"].notnull(),
        (df["return_date"] - df["issue_date"]).dt.days,
        (today - df["issue_date"]).dt.days
    )
    # Clip negative durations just in case
    df["duration_days"] = np.maximum(df["duration_days"], 0)

    # Re-evaluate real-time overdue condition
    # If status is not RETURNED and due_date < today -> Overdue
    is_overdue = (df["return_date"].isnull()) & (df["due_date"] < today)
    df["is_overdue"] = is_overdue
    df["days_overdue"] = np.where(is_overdue, (today - df["due_date"]).dt.days, 0)
    df["fine_amount"] = df["days_overdue"] * config.DAILY_OVERDUE_FINE

    return df

def _fetch_all_books_dataframe() -> pd.DataFrame:
    """Loads all books into a Pandas DataFrame."""
    books = db.fetch_all("SELECT * FROM books ORDER BY book_id ASC;")
    if not books:
        return pd.DataFrame(columns=["book_id", "isbn", "title", "author", "category", "copies_available", "total_copies"])
    return pd.DataFrame(books)

class LibraryAnalytics:

    @staticmethod
    def get_dashboard_summary() -> Dict[str, Any]:
        """Summarizes high-level circulation statistics."""
        df_loans = _fetch_all_loans_dataframe()
        df_books = _fetch_all_books_dataframe()
        borrowers = db.fetch_all("SELECT COUNT(*) as count FROM borrowers;")
        borrower_count = borrowers[0]["count"] if borrowers else 0

        total_books_titles = len(df_books)
        total_physical_copies = int(df_books["total_copies"].sum()) if not df_books.empty else 0
        total_available_copies = int(df_books["copies_available"].sum()) if not df_books.empty else 0
        
        total_loans = len(df_loans)
        active_loans = int((df_loans["return_date"].isnull()).sum()) if not df_loans.empty else 0
        returned_loans = int((df_loans["return_date"].notnull()).sum()) if not df_loans.empty else 0
        overdue_loans = int(df_loans["is_overdue"].sum()) if not df_loans.empty else 0

        return {
            "total_titles": total_books_titles,
            "total_copies": total_physical_copies,
            "available_copies": total_available_copies,
            "borrowed_copies": total_physical_copies - total_available_copies,
            "total_borrowers": borrower_count,
            "total_loans": total_loans,
            "active_loans": active_loans,
            "returned_loans": returned_loans,
            "overdue_loans": overdue_loans,
            "active_engine": db.active_engine,
            "default_loan_days": config.DEFAULT_LOAN_DAYS,
            "daily_fine": config.DAILY_OVERDUE_FINE
        }

    @staticmethod
    def get_most_borrowed_books_report(limit: int = 10) -> List[Dict[str, Any]]:
        """Identifies most-borrowed books with borrow counts and metrics."""
        df_loans = _fetch_all_loans_dataframe()
        if df_loans.empty:
            return []

        # Group by book_id, title, author, category
        grouped = df_loans.groupby(["book_id", "title", "author", "category", "isbn", "total_copies"]).agg(
            times_borrowed=("loan_id", "count"),
            unique_borrowers=("borrower_id", lambda x: len(np.unique(x))),
            avg_duration_days=("duration_days", "mean"),
            active_count=("return_date", lambda x: int(x.isnull().sum()))
        ).reset_index()

        grouped = grouped.sort_values(by=["times_borrowed", "unique_borrowers"], ascending=[False, False])
        top_books = grouped.head(limit)
        
        # Round averages
        top_books["avg_duration_days"] = top_books["avg_duration_days"].round(1)
        return top_books.to_dict(orient="records")

    @staticmethod
    def get_overdue_loans_report() -> List[Dict[str, Any]]:
        """Identifies all currently overdue loans with days overdue and fine calculation."""
        df_loans = _fetch_all_loans_dataframe()
        if df_loans.empty:
            return []

        overdue_df = df_loans[df_loans["is_overdue"]].copy()
        if overdue_df.empty:
            return []

        overdue_df = overdue_df.sort_values(by="days_overdue", ascending=False)
        
        records = []
        for _, row in overdue_df.iterrows():
            records.append({
                "loan_id": int(row["loan_id"]),
                "book_id": int(row["book_id"]),
                "title": str(row["title"]),
                "author": str(row["author"]),
                "category": str(row["category"]),
                "borrower_id": int(row["borrower_id"]),
                "borrower_name": str(row["borrower_name"]),
                "roll_no": str(row["roll_no"]),
                "borrower_type": str(row.get("borrower_type", "Student")),
                "issue_date": row["issue_date"].strftime("%Y-%m-%d"),
                "due_date": row["due_date"].strftime("%Y-%m-%d"),
                "days_overdue": int(row["days_overdue"]),
                "estimated_fine": round(float(row["fine_amount"]), 2)
            })
        return records

    @staticmethod
    def get_category_summary() -> List[Dict[str, Any]]:
        """Pandas category aggregation and summary."""
        df_books = _fetch_all_books_dataframe()
        df_loans = _fetch_all_loans_dataframe()

        if df_books.empty:
            return []

        # Book category aggregation
        cat_books = df_books.groupby("category").agg(
            total_titles=("book_id", "count"),
            total_copies=("total_copies", "sum"),
            available_copies=("copies_available", "sum")
        ).reset_index()

        # Loans per category aggregation
        if not df_loans.empty:
            cat_loans = df_loans.groupby("category").agg(
                total_borrows=("loan_id", "count"),
                active_borrows=("return_date", lambda x: int(x.isnull().sum())),
                overdue_count=("is_overdue", "sum")
            ).reset_index()
            summary = pd.merge(cat_books, cat_loans, on="category", how="left").fillna(0)
        else:
            summary = cat_books.copy()
            summary["total_borrows"] = 0
            summary["active_borrows"] = 0
            summary["overdue_count"] = 0

        # Cast to integers
        summary["total_borrows"] = summary["total_borrows"].astype(int)
        summary["active_borrows"] = summary["active_borrows"].astype(int)
        summary["overdue_count"] = summary["overdue_count"].astype(int)

        # Calculate utilization percentage: (total_copies - available_copies) / total_copies * 100
        summary["utilization_pct"] = np.where(
            summary["total_copies"] > 0,
            np.round(((summary["total_copies"] - summary["available_copies"]) / summary["total_copies"]) * 100, 1),
            0.0
        )

        return summary.sort_values(by="total_borrows", ascending=False).to_dict(orient="records")

    @staticmethod
    def get_monthly_circulation_trends() -> List[Dict[str, Any]]:
        """Pandas monthly aggregation of borrowing circulation."""
        df_loans = _fetch_all_loans_dataframe()
        if df_loans.empty:
            return []

        df_loans["year_month"] = df_loans["issue_date"].dt.strftime("%Y-%m")
        monthly = df_loans.groupby("year_month").agg(
            total_loans=("loan_id", "count"),
            returned_count=("return_date", lambda x: int(x.notnull().sum())),
            overdue_count=("is_overdue", "sum")
        ).reset_index()

        monthly = monthly.sort_values(by="year_month")
        return monthly.to_dict(orient="records")

    @staticmethod
    def get_numpy_descriptive_statistics() -> Dict[str, Any]:
        """NumPy descriptive statistical computation of loan periods and book circulation."""
        df_loans = _fetch_all_loans_dataframe()
        if df_loans.empty:
            return {
                "count": 0,
                "mean_duration": 0.0,
                "median_duration": 0.0,
                "std_duration": 0.0,
                "min_duration": 0.0,
                "max_duration": 0.0,
                "p25_duration": 0.0,
                "p75_duration": 0.0,
                "p90_duration": 0.0,
                "overdue_rate_pct": 0.0,
                "avg_borrows_per_active_book": 0.0
            }

        durations = df_loans["duration_days"].to_numpy(dtype=float)
        
        # NumPy statistics
        mean_dur = float(np.mean(durations))
        median_dur = float(np.median(durations))
        std_dur = float(np.std(durations))
        min_dur = float(np.min(durations))
        max_dur = float(np.max(durations))
        p25 = float(np.percentile(durations, 25))
        p75 = float(np.percentile(durations, 75))
        p90 = float(np.percentile(durations, 90))
        
        # Overdue rate
        overdue_rate = float((np.sum(df_loans["is_overdue"].to_numpy()) / len(df_loans)) * 100)

        # Average borrows per unique book borrowed
        book_counts = df_loans["book_id"].value_counts().to_numpy()
        avg_borrows = float(np.mean(book_counts)) if len(book_counts) > 0 else 0.0

        return {
            "count": int(len(durations)),
            "mean_duration": round(mean_dur, 2),
            "median_duration": round(median_dur, 2),
            "std_duration": round(std_dur, 2),
            "min_duration": round(min_dur, 1),
            "max_duration": round(max_dur, 1),
            "p25_duration": round(p25, 1),
            "p75_duration": round(p75, 1),
            "p90_duration": round(p90, 1),
            "overdue_rate_pct": round(overdue_rate, 2),
            "avg_borrows_per_book": round(avg_borrows, 2)
        }

    # ============================================================
    # Matplotlib Chart Generation (Exported as Base64 Data URI)
    # ============================================================

    @staticmethod
    def _plot_to_base64() -> str:
        """Helper to serialize the current Matplotlib plot to base64 image data string."""
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png", dpi=160, bbox_inches="tight", transparent=False)
        plt.close()
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"

    @classmethod
    def generate_monthly_circulation_chart(cls) -> str:
        """Generates Matplotlib monthly circulation trends chart."""
        df_loans = _fetch_all_loans_dataframe()
        plt.figure(figsize=(9, 4.5), facecolor="#ffffff")
        
        if df_loans.empty:
            plt.text(0.5, 0.5, "No loan data recorded yet", ha="center", va="center", fontsize=14, color="#6b7280")
            plt.axis("off")
            return cls._plot_to_base64()

        df_loans["year_month"] = df_loans["issue_date"].dt.strftime("%b %Y")
        monthly = df_loans.groupby("year_month", sort=False).size().reset_index(name="count")

        ax = plt.gca()
        ax.set_facecolor("#f9fafb")
        
        bars = ax.bar(monthly["year_month"], monthly["count"], color="#3b82f6", width=0.55, edgecolor="#1d4ed8", linewidth=1.2, zorder=3)
        # Line overlay
        ax.plot(monthly["year_month"], monthly["count"], color="#ef4444", marker="o", linewidth=2.5, markersize=7, zorder=4, label="Trend Line")

        # Bar value labels
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"{int(height)}",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 4), textcoords="offset points",
                        ha="center", va="bottom", fontsize=10, fontweight="bold", color="#1e293b")

        ax.grid(axis="y", linestyle="--", alpha=0.5, zorder=0)
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.set_title("Monthly Library Circulation & Borrowing Trends", fontsize=14, fontweight="bold", pad=15, color="#0f172a")
        ax.set_xlabel("Month", fontsize=11, fontweight="bold", labelpad=8, color="#334155")
        ax.set_ylabel("Number of Books Borrowed", fontsize=11, fontweight="bold", labelpad=8, color="#334155")
        ax.legend(loc="upper left", framealpha=0.9)
        plt.xticks(rotation=20, ha="right", fontsize=10)

        return cls._plot_to_base64()

    @classmethod
    def generate_popular_books_chart(cls, limit: int = 6) -> str:
        """Generates Matplotlib popular books ranking chart."""
        books = cls.get_most_borrowed_books_report(limit=limit)
        plt.figure(figsize=(9, 4.5), facecolor="#ffffff")

        if not books:
            plt.text(0.5, 0.5, "No borrowing history available", ha="center", va="center", fontsize=14, color="#6b7280")
            plt.axis("off")
            return cls._plot_to_base64()

        # Reverse order for horizontal bar chart (top book on top)
        titles = [b["title"][:28] + ("..." if len(b["title"]) > 28 else "") for b in reversed(books)]
        counts = [b["times_borrowed"] for b in reversed(books)]

        ax = plt.gca()
        ax.set_facecolor("#f9fafb")
        colors = plt.cm.viridis(np.linspace(0.4, 0.85, len(titles)))

        bars = ax.barh(titles, counts, color=colors, height=0.6, edgecolor="#334155", linewidth=0.8, zorder=3)

        for bar in bars:
            width = bar.get_width()
            ax.annotate(f"{int(width)} borrows",
                        xy=(width, bar.get_y() + bar.get_height() / 2),
                        xytext=(6, 0), textcoords="offset points",
                        ha="left", va="center", fontsize=10, fontweight="bold", color="#1e293b")

        ax.grid(axis="x", linestyle="--", alpha=0.5, zorder=0)
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.set_title(f"Top {len(books)} Most-Borrowed Books", fontsize=14, fontweight="bold", pad=15, color="#0f172a")
        ax.set_xlabel("Total Times Borrowed", fontsize=11, fontweight="bold", labelpad=8, color="#334155")
        plt.yticks(fontsize=10)

        return cls._plot_to_base64()

    @classmethod
    def generate_category_distribution_chart(cls) -> str:
        """Generates Matplotlib category circulation doughnut chart."""
        summary = cls.get_category_summary()
        plt.figure(figsize=(7.5, 4.5), facecolor="#ffffff")

        if not summary or sum(c["total_borrows"] for c in summary) == 0:
            plt.text(0.5, 0.5, "No category borrowing data available", ha="center", va="center", fontsize=14, color="#6b7280")
            plt.axis("off")
            return cls._plot_to_base64()

        categories = [c["category"] for c in summary if c["total_borrows"] > 0]
        borrows = [c["total_borrows"] for c in summary if c["total_borrows"] > 0]

        if not borrows:
            # Fallback to book distribution if no borrows yet
            categories = [c["category"] for c in summary]
            borrows = [c["total_copies"] for c in summary]

        colors = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#06b6d4", "#64748b"]

        wedges, texts, autotexts = plt.pie(
            borrows,
            labels=categories,
            autopct="%1.1f%%",
            pctdistance=0.75,
            startangle=140,
            colors=colors[:len(categories)],
            wedgeprops=dict(width=0.45, edgecolor="#ffffff", linewidth=2)
        )

        for text in texts:
            text.set_color("#1e293b")
            text.set_fontsize(10)
            text.set_fontweight("bold")
        for autotext in autotexts:
            autotext.set_color("#ffffff")
            autotext.set_fontsize(9)
            autotext.set_fontweight("bold")

        plt.title("Circulation by Subject Category", fontsize=14, fontweight="bold", pad=15, color="#0f172a")
        return cls._plot_to_base64()
