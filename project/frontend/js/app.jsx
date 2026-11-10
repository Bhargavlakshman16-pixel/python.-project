const { useState, useEffect, useMemo } = React;

// API Helper
const API_BASE = "";

async function apiRequest(endpoint, options = {}) {
    try {
        const res = await fetch(`${API_BASE}${endpoint}`, {
            headers: { "Content-Type": "application/json", ...(options.headers || {}) },
            ...options
        });
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || data.message || "An error occurred with the request.");
        }
        return data;
    } catch (err) {
        throw err;
    }
}

// ============================================================
// MAIN APP COMPONENT
// ============================================================
function App() {
    const [currentTab, setCurrentTab] = useState("dashboard"); // dashboard, books, borrowers, loans, analytics
    const [stats, setStats] = useState(null);
    const [toast, setToast] = useState(null);
    const [showSettings, setShowSettings] = useState(false);
    const [showIssueModal, setShowIssueModal] = useState(false);
    const [selectedBookForIssue, setSelectedBookForIssue] = useState(null);
    const [refreshTrigger, setRefreshTrigger] = useState(0);

    const showNotification = (message, type = "success") => {
        setToast({ message, type });
        setTimeout(() => setToast(null), 4000);
    };

    const triggerRefresh = () => setRefreshTrigger(prev => prev + 1);

    useEffect(() => {
        apiRequest("/api/analytics/dashboard")
            .then(data => setStats(data))
            .catch(err => console.error("Failed to load dashboard summary:", err));
    }, [refreshTrigger]);

    return (
        <div className="app-layout">
            {/* Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-brand">
                    <i className="fa-solid fa-book-bookmark brand-icon"></i>
                    <div className="brand-text">
                        <h1>LibAnalytics</h1>
                        <span>Circulation System</span>
                    </div>
                </div>

                <ul className="nav-links">
                    <li>
                        <button 
                            className={`nav-btn ${currentTab === "dashboard" ? "active" : ""}`}
                            onClick={() => setCurrentTab("dashboard")}
                        >
                            <i className="fa-solid fa-chart-pie"></i>
                            Dashboard
                        </button>
                    </li>
                    <li>
                        <button 
                            className={`nav-btn ${currentTab === "books" ? "active" : ""}`}
                            onClick={() => setCurrentTab("books")}
                        >
                            <i className="fa-solid fa-book"></i>
                            Book Records
                        </button>
                    </li>
                    <li>
                        <button 
                            className={`nav-btn ${currentTab === "borrowers" ? "active" : ""}`}
                            onClick={() => setCurrentTab("borrowers")}
                        >
                            <i className="fa-solid fa-users"></i>
                            Borrower Records
                        </button>
                    </li>
                    <li>
                        <button 
                            className={`nav-btn ${currentTab === "loans" ? "active" : ""}`}
                            onClick={() => setCurrentTab("loans")}
                        >
                            <i className="fa-solid fa-arrow-right-arrow-left"></i>
                            Circulation & Loans
                        </button>
                    </li>
                    <li>
                        <button 
                            className={`nav-btn ${currentTab === "analytics" ? "active" : ""}`}
                            onClick={() => setCurrentTab("analytics")}
                        >
                            <i className="fa-solid fa-chart-line"></i>
                            Usage Analytics
                        </button>
                    </li>
                </ul>

                <div className="sidebar-footer">
                    {stats && (
                        <div>
                            <span className={`engine-badge ${stats.active_engine}`}>
                                <i className="fa-solid fa-database"></i> Engine: {stats.active_engine.toUpperCase()}
                            </span>
                            <p style={{fontSize: "0.74rem"}}>Loan Period: {stats.default_loan_days} Days</p>
                        </div>
                    )}
                    <button 
                        className="btn btn-outline btn-sm" 
                        style={{marginTop: "10px", width: "100%", justifyContent: "center", color: "#cbd5e1", borderColor: "#334155"}}
                        onClick={() => setShowSettings(true)}
                    >
                        <i className="fa-solid fa-gear"></i> System Settings
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="main-wrapper">
                <header className="top-header">
                    <div className="page-title">
                        <h2>
                            {currentTab === "dashboard" && "Circulation Dashboard"}
                            {currentTab === "books" && "Books Inventory"}
                            {currentTab === "borrowers" && "Borrowers Management"}
                            {currentTab === "loans" && "Book Circulation & Loans"}
                            {currentTab === "analytics" && "Library Usage Analytics"}
                        </h2>
                        <p>
                            {currentTab === "dashboard" && "Overview of active loans, overdue counts, and monthly circulation."}
                            {currentTab === "books" && "Manage book titles, categories, and real-time available copies."}
                            {currentTab === "borrowers" && "Manage student/faculty borrower profiles and roll numbers."}
                            {currentTab === "loans" && "Record book issues and returns with due date validation."}
                            {currentTab === "analytics" && "Pandas & NumPy data summaries and Matplotlib trend visualizations."}
                        </p>
                    </div>
                    <div className="header-actions">
                        <button 
                            className="btn btn-primary"
                            onClick={() => {
                                setSelectedBookForIssue(null);
                                setShowIssueModal(true);
                            }}
                        >
                            <i className="fa-solid fa-plus"></i> Issue Book
                        </button>
                    </div>
                </header>

                <div className="content-body">
                    {/* View Switcher */}
                    {currentTab === "dashboard" && (
                        <DashboardView 
                            stats={stats} 
                            onNavigate={setCurrentTab} 
                            onIssueClick={(book) => {
                                setSelectedBookForIssue(book);
                                setShowIssueModal(true);
                            }}
                            refreshTrigger={refreshTrigger}
                            showNotification={showNotification}
                        />
                    )}
                    {currentTab === "books" && (
                        <BooksView 
                            showNotification={showNotification}
                            onIssueClick={(book) => {
                                setSelectedBookForIssue(book);
                                setShowIssueModal(true);
                            }}
                            refreshTrigger={refreshTrigger}
                            triggerRefresh={triggerRefresh}
                        />
                    )}
                    {currentTab === "borrowers" && (
                        <BorrowersView 
                            showNotification={showNotification}
                            refreshTrigger={refreshTrigger}
                            triggerRefresh={triggerRefresh}
                        />
                    )}
                    {currentTab === "loans" && (
                        <LoansView 
                            showNotification={showNotification}
                            refreshTrigger={refreshTrigger}
                            triggerRefresh={triggerRefresh}
                            onOpenIssueModal={() => {
                                setSelectedBookForIssue(null);
                                setShowIssueModal(true);
                            }}
                        />
                    )}
                    {currentTab === "analytics" && (
                        <AnalyticsView 
                            refreshTrigger={refreshTrigger}
                        />
                    )}
                </div>
            </main>

            {/* Issue Book Modal */}
            {showIssueModal && (
                <IssueBookModal 
                    preselectedBook={selectedBookForIssue}
                    onClose={() => setShowIssueModal(false)}
                    onSuccess={() => {
                        setShowIssueModal(false);
                        triggerRefresh();
                        showNotification("Book issued successfully!");
                    }}
                    showNotification={showNotification}
                />
            )}

            {/* Settings Modal */}
            {showSettings && (
                <SettingsModal 
                    onClose={() => setShowSettings(false)}
                    showNotification={showNotification}
                    triggerRefresh={triggerRefresh}
                />
            )}

            {/* Toast Notifications */}
            {toast && (
                <div className="toast-container">
                    <div className={`toast ${toast.type === "error" ? "toast-error" : "toast-success"}`}>
                        <i className={`fa-solid ${toast.type === "error" ? "fa-circle-exclamation" : "fa-circle-check"}`}></i>
                        <span>{toast.message}</span>
                    </div>
                </div>
            )}
        </div>
    );
}

// ============================================================
// 1. DASHBOARD VIEW
// ============================================================
function DashboardView({ stats, onNavigate, onIssueClick, refreshTrigger, showNotification }) {
    const [charts, setCharts] = useState(null);
    const [loadingCharts, setLoadingCharts] = useState(true);

    useEffect(() => {
        setLoadingCharts(true);
        apiRequest("/api/analytics/charts")
            .then(data => {
                setCharts(data);
                setLoadingCharts(false);
            })
            .catch(err => {
                console.error("Failed to load charts:", err);
                setLoadingCharts(false);
            });
    }, [refreshTrigger]);

    return (
        <div>
            {/* KPI Cards */}
            <div className="kpi-grid">
                <div className="kpi-card">
                    <div className="kpi-icon blue"><i className="fa-solid fa-book"></i></div>
                    <div className="kpi-info">
                        <h4>Book Titles</h4>
                        <div className="kpi-value">{stats ? stats.total_titles : "-"}</div>
                        <span className="kpi-subtitle">{stats ? `${stats.total_copies} Total Copies` : ""}</span>
                    </div>
                </div>

                <div className="kpi-card">
                    <div className="kpi-icon green"><i className="fa-solid fa-check-circle"></i></div>
                    <div className="kpi-info">
                        <h4>Available Copies</h4>
                        <div className="kpi-value">{stats ? stats.available_copies : "-"}</div>
                        <span className="kpi-subtitle">Ready for borrowing</span>
                    </div>
                </div>

                <div className="kpi-card">
                    <div className="kpi-icon amber"><i className="fa-solid fa-hand-holding"></i></div>
                    <div className="kpi-info">
                        <h4>Active Loans</h4>
                        <div className="kpi-value">{stats ? stats.active_loans : "-"}</div>
                        <span className="kpi-subtitle">Currently issued out</span>
                    </div>
                </div>

                <div className="kpi-card">
                    <div className="kpi-icon red"><i className="fa-solid fa-clock"></i></div>
                    <div className="kpi-info">
                        <h4>Overdue Loans</h4>
                        <div className="kpi-value">{stats ? stats.overdue_loans : "-"}</div>
                        <span className="kpi-subtitle">Past due date</span>
                    </div>
                </div>

                <div className="kpi-card">
                    <div className="kpi-icon purple"><i className="fa-solid fa-users"></i></div>
                    <div className="kpi-info">
                        <h4>Borrowers</h4>
                        <div className="kpi-value">{stats ? stats.total_borrowers : "-"}</div>
                        <span className="kpi-subtitle">Registered patrons</span>
                    </div>
                </div>
            </div>

            {/* Overdue alert if any */}
            {stats && stats.overdue_loans > 0 && (
                <div className="alert-banner alert-danger">
                    <i className="fa-solid fa-triangle-exclamation" style={{fontSize: "1.2rem"}}></i>
                    <div style={{flex: 1}}>
                        <strong>Attention Needed:</strong> There are currently <strong>{stats.overdue_loans}</strong> overdue book loans requiring returns or notices.
                    </div>
                    <button 
                        className="btn btn-sm btn-danger"
                        onClick={() => onNavigate("loans")}
                    >
                        View Overdue Loans
                    </button>
                </div>
            )}

            {/* Matplotlib Charts Overview */}
            <div style={{display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(480px, 1fr))", gap: "24px", marginBottom: "24px"}}>
                <div className="card">
                    <div className="card-header">
                        <h3><i className="fa-solid fa-chart-line" style={{color: "var(--primary)"}}></i> Monthly Circulation Trend</h3>
                        <span className="badge badge-info">Matplotlib + Pandas</span>
                    </div>
                    <div className="card-body" style={{textAlign: "center"}}>
                        {loadingCharts ? (
                            <div style={{padding: "60px 0"}}><div className="spinner"></div></div>
                        ) : charts && charts.monthly_circulation_chart ? (
                            <img src={charts.monthly_circulation_chart} alt="Monthly Circulation" style={{maxWidth: "100%", borderRadius: "8px"}} />
                        ) : (
                            <p style={{color: "var(--text-muted)", padding: "40px"}}>No chart data available.</p>
                        )}
                    </div>
                </div>

                <div className="card">
                    <div className="card-header">
                        <h3><i className="fa-solid fa-chart-pie" style={{color: "var(--success)"}}></i> Category Circulation Breakdown</h3>
                        <span className="badge badge-info">Matplotlib + Pandas</span>
                    </div>
                    <div className="card-body" style={{textAlign: "center"}}>
                        {loadingCharts ? (
                            <div style={{padding: "60px 0"}}><div className="spinner"></div></div>
                        ) : charts && charts.category_distribution_chart ? (
                            <img src={charts.category_distribution_chart} alt="Category Breakdown" style={{maxWidth: "100%", borderRadius: "8px"}} />
                        ) : (
                            <p style={{color: "var(--text-muted)", padding: "40px"}}>No chart data available.</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Quick Actions & Navigation Bar */}
            <div className="card">
                <div className="card-header">
                    <h3><i className="fa-solid fa-bolt" style={{color: "var(--warning)"}}></i> Quick Operations</h3>
                </div>
                <div className="card-body" style={{display: "flex", gap: "12px", flexWrap: "wrap"}}>
                    <button className="btn btn-primary" onClick={() => onNavigate("books")}>
                        <i className="fa-solid fa-book"></i> View All Books
                    </button>
                    <button className="btn btn-outline" onClick={() => onNavigate("loans")}>
                        <i className="fa-solid fa-arrow-right-arrow-left"></i> Manage Active Loans
                    </button>
                    <button className="btn btn-outline" onClick={() => onNavigate("analytics")}>
                        <i className="fa-solid fa-magnifying-glass-chart"></i> View Full Usage Analytics Report
                    </button>
                </div>
            </div>
        </div>
    );
}

// ============================================================
// 2. BOOKS VIEW
// ============================================================
function BooksView({ showNotification, onIssueClick, refreshTrigger, triggerRefresh }) {
    const [books, setBooks] = useState([]);
    const [categories, setCategories] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState("All");
    const [searchTerm, setSearchTerm] = useState("");
    const [loading, setLoading] = useState(true);
    const [showAddModal, setShowAddModal] = useState(false);
    const [editingBook, setEditingBook] = useState(null);

    const loadBooks = () => {
        setLoading(true);
        let url = `/api/books?category=${encodeURIComponent(selectedCategory)}`;
        if (searchTerm.trim()) {
            url += `&search=${encodeURIComponent(searchTerm.trim())}`;
        }
        apiRequest(url)
            .then(data => {
                setBooks(data);
                setLoading(false);
            })
            .catch(err => {
                showNotification(err.message, "error");
                setLoading(false);
            });
    };

    useEffect(() => {
        apiRequest("/api/books/categories")
            .then(data => setCategories(data))
            .catch(err => console.error(err));
    }, [refreshTrigger]);

    useEffect(() => {
        loadBooks();
    }, [selectedCategory, searchTerm, refreshTrigger]);

    const handleDelete = async (bookId, title) => {
        if (!confirm(`Are you sure you want to delete book "${title}"?`)) return;
        try {
            await apiRequest(`/api/books/${bookId}`, { method: "DELETE" });
            showNotification(`"${title}" deleted successfully.`);
            triggerRefresh();
        } catch (err) {
            showNotification(err.message, "error");
        }
    };

    return (
        <div className="card">
            <div className="card-header">
                <h3><i className="fa-solid fa-book" style={{color: "var(--primary)"}}></i> Library Catalog & Inventory</h3>
                <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
                    <i className="fa-solid fa-plus"></i> Add New Book
                </button>
            </div>
            <div className="card-body">
                {/* Search & Filters */}
                <div className="filter-bar">
                    <div className="search-box">
                        <i className="fa-solid fa-magnifying-glass"></i>
                        <input 
                            type="text" 
                            className="search-input" 
                            placeholder="Search by title, author, or ISBN..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <select 
                        className="select-input" 
                        value={selectedCategory} 
                        onChange={(e) => setSelectedCategory(e.target.value)}
                    >
                        <option value="All">All Categories</option>
                        {categories.map(c => (
                            <option key={c} value={c}>{c}</option>
                        ))}
                    </select>
                </div>

                {/* Table */}
                <div className="table-container">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>ISBN</th>
                                <th>Title</th>
                                <th>Author</th>
                                <th>Category</th>
                                <th>Copies Available</th>
                                <th>Total Inventory</th>
                                <th>Status</th>
                                <th style={{textAlign: "right"}}>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr><td colSpan="8" style={{textAlign: "center", padding: "40px"}}><div className="spinner"></div></td></tr>
                            ) : books.length === 0 ? (
                                <tr><td colSpan="8" style={{textAlign: "center", padding: "40px", color: "var(--text-muted)"}}>No books match your criteria.</td></tr>
                            ) : (
                                books.map(book => {
                                    const isAvailable = book.copies_available > 0;
                                    return (
                                        <tr key={book.book_id}>
                                            <td style={{fontFamily: "monospace", fontSize: "0.82rem"}}>{book.isbn}</td>
                                            <td style={{fontWeight: 600, color: "var(--text-primary)"}}>{book.title}</td>
                                            <td>{book.author}</td>
                                            <td><span className="badge badge-secondary">{book.category}</span></td>
                                            <td style={{fontWeight: 700, color: isAvailable ? "var(--success)" : "var(--danger)"}}>
                                                {book.copies_available}
                                            </td>
                                            <td>{book.total_copies}</td>
                                            <td>
                                                {isAvailable ? (
                                                    <span className="badge badge-success"><i className="fa-solid fa-check"></i> Available</span>
                                                ) : (
                                                    <span className="badge badge-danger"><i className="fa-solid fa-ban"></i> Out of Stock</span>
                                                )}
                                            </td>
                                            <td style={{textAlign: "right", whiteSpace: "nowrap"}}>
                                                <button 
                                                    className="btn btn-outline btn-sm" 
                                                    disabled={!isAvailable}
                                                    title={isAvailable ? "Issue this book" : "No copies available to issue"}
                                                    style={{marginRight: "6px"}}
                                                    onClick={() => onIssueClick(book)}
                                                >
                                                    <i className="fa-solid fa-share"></i> Issue
                                                </button>
                                                <button 
                                                    className="btn btn-outline btn-sm" 
                                                    style={{marginRight: "6px"}}
                                                    onClick={() => setEditingBook(book)}
                                                    title="Edit book"
                                                >
                                                    <i className="fa-solid fa-pen"></i>
                                                </button>
                                                <button 
                                                    className="btn btn-outline btn-sm" 
                                                    style={{color: "var(--danger)", borderColor: "#fecaca"}}
                                                    onClick={() => handleDelete(book.book_id, book.title)}
                                                    title="Delete book"
                                                >
                                                    <i className="fa-solid fa-trash"></i>
                                                </button>
                                            </td>
                                        </tr>
                                    );
                                })
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Add Book Modal */}
            {showAddModal && (
                <BookFormModal 
                    title="Add New Book"
                    onClose={() => setShowAddModal(false)}
                    onSubmit={async (formData) => {
                        try {
                            await apiRequest("/api/books", {
                                method: "POST",
                                body: JSON.stringify(formData)
                            });
                            showNotification("Book added successfully!");
                            setShowAddModal(false);
                            triggerRefresh();
                        } catch (err) {
                            showNotification(err.message, "error");
                        }
                    }}
                />
            )}

            {/* Edit Book Modal */}
            {editingBook && (
                <BookFormModal 
                    title="Edit Book Details"
                    initialData={editingBook}
                    onClose={() => setEditingBook(null)}
                    onSubmit={async (formData) => {
                        try {
                            await apiRequest(`/api/books/${editingBook.book_id}`, {
                                method: "PUT",
                                body: JSON.stringify(formData)
                            });
                            showNotification("Book updated successfully!");
                            setEditingBook(null);
                            triggerRefresh();
                        } catch (err) {
                            showNotification(err.message, "error");
                        }
                    }}
                />
            )}
        </div>
    );
}

// ============================================================
// 3. BORROWERS VIEW
// ============================================================
function BorrowersView({ showNotification, refreshTrigger, triggerRefresh }) {
    const [borrowers, setBorrowers] = useState([]);
    const [searchTerm, setSearchTerm] = useState("");
    const [loading, setLoading] = useState(true);
    const [showAddModal, setShowAddModal] = useState(false);
    const [selectedBorrowerHistory, setSelectedBorrowerHistory] = useState(null);

    const loadBorrowers = () => {
        setLoading(true);
        let url = "/api/borrowers";
        if (searchTerm.trim()) {
            url += `?search=${encodeURIComponent(searchTerm.trim())}`;
        }
        apiRequest(url)
            .then(data => {
                setBorrowers(data);
                setLoading(false);
            })
            .catch(err => {
                showNotification(err.message, "error");
                setLoading(false);
            });
    };

    useEffect(() => {
        loadBorrowers();
    }, [searchTerm, refreshTrigger]);

    const viewHistory = async (borrowerId) => {
        try {
            const data = await apiRequest(`/api/borrowers/${borrowerId}`);
            setSelectedBorrowerHistory(data);
        } catch (err) {
            showNotification(err.message, "error");
        }
    };

    const handleDelete = async (borrowerId, name) => {
        if (!confirm(`Delete borrower "${name}"?`)) return;
        try {
            await apiRequest(`/api/borrowers/${borrowerId}`, { method: "DELETE" });
            showNotification(`Borrower ${name} deleted.`);
            triggerRefresh();
        } catch (err) {
            showNotification(err.message, "error");
        }
    };

    return (
        <div className="card">
            <div className="card-header">
                <h3><i className="fa-solid fa-users" style={{color: "var(--primary)"}}></i> Registered Borrowers</h3>
                <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
                    <i className="fa-solid fa-user-plus"></i> Add New Borrower
                </button>
            </div>
            <div className="card-body">
                <div className="filter-bar">
                    <div className="search-box">
                        <i className="fa-solid fa-magnifying-glass"></i>
                        <input 
                            type="text" 
                            className="search-input" 
                            placeholder="Search borrower by name or roll number..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </div>

                <div className="table-container">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Roll Number</th>
                                <th>Borrower Name</th>
                                <th>Email</th>
                                <th>Contact</th>
                                <th>Joined</th>
                                <th style={{textAlign: "right"}}>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr><td colSpan="6" style={{textAlign: "center", padding: "40px"}}><div className="spinner"></div></td></tr>
                            ) : borrowers.length === 0 ? (
                                <tr><td colSpan="6" style={{textAlign: "center", padding: "40px", color: "var(--text-muted)"}}>No borrowers found.</td></tr>
                            ) : (
                                borrowers.map(b => (
                                    <tr key={b.borrower_id}>
                                        <td style={{fontFamily: "monospace", fontWeight: 700, color: "var(--primary)"}}>{b.roll_no}</td>
                                        <td style={{fontWeight: 600}}>{b.borrower_name}</td>
                                        <td>{b.email || <span style={{color: "var(--text-muted)"}}>—</span>}</td>
                                        <td>{b.contact || <span style={{color: "var(--text-muted)"}}>—</span>}</td>
                                        <td style={{fontSize: "0.82rem", color: "var(--text-muted)"}}>{b.created_at ? b.created_at.slice(0, 10) : "—"}</td>
                                        <td style={{textAlign: "right", whiteSpace: "nowrap"}}>
                                            <button 
                                                className="btn btn-outline btn-sm" 
                                                style={{marginRight: "6px"}}
                                                onClick={() => viewHistory(b.borrower_id)}
                                            >
                                                <i className="fa-solid fa-clock-rotate-left"></i> Loan History
                                            </button>
                                            <button 
                                                className="btn btn-outline btn-sm" 
                                                style={{color: "var(--danger)", borderColor: "#fecaca"}}
                                                onClick={() => handleDelete(b.borrower_id, b.borrower_name)}
                                            >
                                                <i className="fa-solid fa-trash"></i>
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Add Borrower Modal */}
            {showAddModal && (
                <BorrowerFormModal 
                    onClose={() => setShowAddModal(false)}
                    onSubmit={async (formData) => {
                        try {
                            await apiRequest("/api/borrowers", {
                                method: "POST",
                                body: JSON.stringify(formData)
                            });
                            showNotification("Borrower registered successfully!");
                            setShowAddModal(false);
                            triggerRefresh();
                        } catch (err) {
                            showNotification(err.message, "error");
                        }
                    }}
                />
            )}

            {/* Borrower Loan History Modal */}
            {selectedBorrowerHistory && (
                <div className="modal-overlay">
                    <div className="modal-content" style={{maxWidth: "750px"}}>
                        <div className="modal-header">
                            <h3>Borrowing Record: {selectedBorrowerHistory.borrower_name} ({selectedBorrowerHistory.roll_no})</h3>
                            <button className="modal-close" onClick={() => setSelectedBorrowerHistory(null)}>&times;</button>
                        </div>
                        <div className="modal-body">
                            {selectedBorrowerHistory.loans && selectedBorrowerHistory.loans.length > 0 ? (
                                <table className="data-table">
                                    <thead>
                                        <tr>
                                            <th>Book Title</th>
                                            <th>Category</th>
                                            <th>Issue Date</th>
                                            <th>Due Date</th>
                                            <th>Return Date</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {selectedBorrowerHistory.loans.map(loan => (
                                            <tr key={loan.loan_id}>
                                                <td style={{fontWeight: 600}}>{loan.title}</td>
                                                <td><span className="badge badge-secondary">{loan.category}</span></td>
                                                <td>{loan.issue_date.slice(0, 10)}</td>
                                                <td>{loan.due_date.slice(0, 10)}</td>
                                                <td>{loan.return_date ? loan.return_date.slice(0, 10) : <span style={{color: "var(--warning)", fontWeight: 600}}>Not Returned</span>}</td>
                                                <td>
                                                    <span className={`badge status-badge ${loan.return_date ? 'badge-success' : 'badge-warning'}`}>
                                                        {loan.return_date ? 'Returned' : 'Active'}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            ) : (
                                <p style={{color: "var(--text-muted)", textAlign: "center", padding: "20px"}}>No loan history found for this borrower.</p>
                            )}
                        </div>
                        <div className="modal-footer">
                            <button className="btn btn-outline" onClick={() => setSelectedBorrowerHistory(null)}>Close</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

// ============================================================
// 4. CIRCULATION & LOANS VIEW
// ============================================================
function LoansView({ showNotification, refreshTrigger, triggerRefresh, onOpenIssueModal }) {
    const [loans, setLoans] = useState([]);
    const [statusFilter, setStatusFilter] = useState("ALL"); // ALL, ACTIVE, OVERDUE, RETURNED
    const [loading, setLoading] = useState(true);
    const [returnModalLoan, setReturnModalLoan] = useState(null);
    const [returnDateInput, setReturnDateInput] = useState(new Date().toISOString().slice(0, 10));

    const loadLoans = () => {
        setLoading(true);
        let url = `/api/loans?status_filter=${statusFilter}`;
        apiRequest(url)
            .then(data => {
                setLoans(data);
                setLoading(false);
            })
            .catch(err => {
                showNotification(err.message, "error");
                setLoading(false);
            });
    };

    useEffect(() => {
        loadLoans();
    }, [statusFilter, refreshTrigger]);

    const handleReturnSubmit = async () => {
        if (!returnModalLoan) return;
        try {
            const res = await apiRequest(`/api/loans/${returnModalLoan.loan_id}/return`, {
                method: "POST",
                body: JSON.stringify({ return_date: returnDateInput })
            });
            showNotification(`"${res.title}" returned successfully! Available copies updated.`);
            setReturnModalLoan(null);
            triggerRefresh();
        } catch (err) {
            showNotification(err.message, "error");
        }
    };

    return (
        <div className="card">
            <div className="card-header">
                <h3><i className="fa-solid fa-arrow-right-arrow-left" style={{color: "var(--primary)"}}></i> Circulation & Borrowing Transactions</h3>
                <button className="btn btn-primary" onClick={onOpenIssueModal}>
                    <i className="fa-solid fa-plus"></i> Issue Book
                </button>
            </div>
            <div className="card-body">
                {/* Filter buttons */}
                <div style={{display: "flex", gap: "8px", marginBottom: "20px", flexWrap: "wrap"}}>
                    {["ALL", "ACTIVE", "OVERDUE", "RETURNED"].map(status => (
                        <button
                            key={status}
                            className={`btn btn-sm ${statusFilter === status ? "btn-primary" : "btn-outline"}`}
                            onClick={() => setStatusFilter(status)}
                        >
                            {status === "ALL" && "All Transactions"}
                            {status === "ACTIVE" && "Active Loans"}
                            {status === "OVERDUE" && "Overdue Loans"}
                            {status === "RETURNED" && "Returned Books"}
                        </button>
                    ))}
                </div>

                <div className="table-container">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Loan ID</th>
                                <th>Book Title</th>
                                <th>Borrower</th>
                                <th>Issue Date</th>
                                <th>Due Date</th>
                                <th>Return Date</th>
                                <th>Overdue Days</th>
                                <th>Status</th>
                                <th style={{textAlign: "right"}}>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr><td colSpan="9" style={{textAlign: "center", padding: "40px"}}><div className="spinner"></div></td></tr>
                            ) : loans.length === 0 ? (
                                <tr><td colSpan="9" style={{textAlign: "center", padding: "40px", color: "var(--text-muted)"}}>No transactions found for this view.</td></tr>
                            ) : (
                                loans.map(loan => {
                                    const isReturned = loan.status === "RETURNED";
                                    const isOverdue = loan.status === "OVERDUE";
                                    return (
                                        <tr key={loan.loan_id} style={{backgroundColor: isOverdue ? "#fff5f5" : "inherit"}}>
                                            <td style={{fontFamily: "monospace", fontWeight: 700}}>#{loan.loan_id}</td>
                                            <td>
                                                <div style={{fontWeight: 600, color: "var(--text-primary)"}}>{loan.title}</div>
                                                <div style={{fontSize: "0.78rem", color: "var(--text-muted)"}}>ISBN: {loan.isbn}</div>
                                            </td>
                                            <td>
                                                <div style={{fontWeight: 600}}>{loan.borrower_name}</div>
                                                <div style={{fontSize: "0.78rem", color: "var(--text-muted)"}}>Roll: {loan.roll_no}</div>
                                            </td>
                                            <td>{loan.issue_date.slice(0, 10)}</td>
                                            <td style={{fontWeight: isOverdue ? 700 : 400, color: isOverdue ? "var(--danger)" : "inherit"}}>
                                                {loan.due_date.slice(0, 10)}
                                            </td>
                                            <td>
                                                {loan.return_date ? (
                                                    loan.return_date.slice(0, 10)
                                                ) : (
                                                    <span style={{color: "var(--text-muted)", fontStyle: "italic"}}>Pending</span>
                                                )}
                                            </td>
                                            <td>
                                                {isOverdue ? (
                                                    <span style={{color: "var(--danger)", fontWeight: 700}}>
                                                        {loan.days_overdue} days (${loan.fine_amount} fine)
                                                    </span>
                                                ) : (
                                                    <span style={{color: "var(--text-muted)"}}>0</span>
                                                )}
                                            </td>
                                            <td>
                                                {isReturned && <span className="badge badge-success status-badge"><i className="fa-solid fa-check"></i> Returned</span>}
                                                {isOverdue && <span className="badge badge-danger status-badge"><i className="fa-solid fa-clock"></i> Overdue</span>}
                                                {!isReturned && !isOverdue && <span className="badge badge-info status-badge"><i className="fa-solid fa-book-open"></i> Active</span>}
                                            </td>
                                            <td style={{textAlign: "right"}}>
                                                {!isReturned ? (
                                                    <button 
                                                        className="btn btn-outline btn-sm"
                                                        style={{color: "var(--success)", borderColor: "#a7f3d0"}}
                                                        onClick={() => {
                                                            setReturnModalLoan(loan);
                                                            setReturnDateInput(new Date().toISOString().slice(0, 10));
                                                        }}
                                                    >
                                                        <i className="fa-solid fa-arrow-turn-down"></i> Return Book
                                                    </button>
                                                ) : (
                                                    <span style={{fontSize: "0.8rem", color: "var(--text-muted)"}}>Completed</span>
                                                )}
                                            </td>
                                        </tr>
                                    );
                                })
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Return Book Confirmation Modal */}
            {returnModalLoan && (
                <div className="modal-overlay">
                    <div className="modal-content">
                        <div className="modal-header">
                            <h3>Record Book Return</h3>
                            <button className="modal-close" onClick={() => setReturnModalLoan(null)}>&times;</button>
                        </div>
                        <div className="modal-body">
                            <p style={{marginBottom: "16px"}}>
                                Returning <strong>{returnModalLoan.title}</strong> borrowed by <strong>{returnModalLoan.borrower_name}</strong> (Roll: {returnModalLoan.roll_no}).
                            </p>
                            <div className="form-group">
                                <label>Date of Return</label>
                                <input 
                                    type="date" 
                                    value={returnDateInput}
                                    onChange={(e) => setReturnDateInput(e.target.value)}
                                    min={returnModalLoan.issue_date.slice(0, 10)}
                                />
                                <div className="help-text">Issue Date was: {returnModalLoan.issue_date.slice(0, 10)}. Return date cannot precede issue date.</div>
                            </div>

                            {returnModalLoan.days_overdue > 0 && (
                                <div className="alert-banner alert-warning" style={{marginTop: "12px"}}>
                                    <i className="fa-solid fa-triangle-exclamation"></i>
                                    <div>
                                        <strong>Book is Overdue by {returnModalLoan.days_overdue} days.</strong><br/>
                                        Accrued fine estimate: <strong>${returnModalLoan.fine_amount}</strong>.
                                    </div>
                                </div>
                            )}
                        </div>
                        <div className="modal-footer">
                            <button className="btn btn-outline" onClick={() => setReturnModalLoan(null)}>Cancel</button>
                            <button className="btn btn-primary" onClick={handleReturnSubmit}>Confirm Return & Update Copies</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

// ============================================================
// 5. USAGE ANALYTICS & REPORTS VIEW (Pandas, NumPy, Matplotlib)
// ============================================================
function AnalyticsView({ refreshTrigger }) {
    const [popularBooks, setPopularBooks] = useState([]);
    const [overdueLoans, setOverdueLoans] = useState([]);
    const [categorySummary, setCategorySummary] = useState([]);
    const [monthlyTrends, setMonthlyTrends] = useState([]);
    const [statsNumpy, setStatsNumpy] = useState(null);
    const [charts, setCharts] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        Promise.all([
            apiRequest("/api/analytics/most-borrowed?limit=8"),
            apiRequest("/api/analytics/overdue-loans"),
            apiRequest("/api/analytics/category-summary"),
            apiRequest("/api/analytics/monthly-trends"),
            apiRequest("/api/analytics/descriptive-statistics"),
            apiRequest("/api/analytics/charts")
        ]).then(([pop, overdue, cat, monthly, npy, chs]) => {
            setPopularBooks(pop);
            setOverdueLoans(overdue);
            setCategorySummary(cat);
            setMonthlyTrends(monthly);
            setStatsNumpy(npy);
            setCharts(chs);
            setLoading(false);
        }).catch(err => {
            console.error("Analytics fetch error:", err);
            setLoading(false);
        });
    }, [refreshTrigger]);

    if (loading) {
        return <div style={{padding: "60px 0", textAlign: "center"}}><div className="spinner"></div><p style={{marginTop: "12px", color: "var(--text-muted)"}}>Running Pandas & NumPy Analytics calculations...</p></div>;
    }

    return (
        <div>
            {/* Descriptive Statistics Card (NumPy) */}
            <div className="card">
                <div className="card-header">
                    <h3><i className="fa-solid fa-square-root-variable" style={{color: "var(--primary)"}}></i> NumPy Descriptive Circulation Statistics</h3>
                    <span className="badge badge-info">NumPy Engine</span>
                </div>
                <div className="card-body">
                    {statsNumpy && (
                        <div className="stat-box-grid">
                            <div className="stat-box">
                                <div className="stat-label">Total Evaluated Loans</div>
                                <div className="stat-val">{statsNumpy.count}</div>
                            </div>
                            <div className="stat-box">
                                <div className="stat-label">Mean Loan Duration</div>
                                <div className="stat-val">{statsNumpy.mean_duration} <span style={{fontSize: "0.8rem", fontWeight: 500}}>days</span></div>
                            </div>
                            <div className="stat-box">
                                <div className="stat-label">Median Duration</div>
                                <div className="stat-val">{statsNumpy.median_duration} <span style={{fontSize: "0.8rem", fontWeight: 500}}>days</span></div>
                            </div>
                            <div className="stat-box">
                                <div className="stat-label">Std Deviation (σ)</div>
                                <div className="stat-val">±{statsNumpy.std_duration} <span style={{fontSize: "0.8rem", fontWeight: 500}}>days</span></div>
                            </div>
                            <div className="stat-box">
                                <div className="stat-label">90th Percentile Duration</div>
                                <div className="stat-val">{statsNumpy.p90_duration} <span style={{fontSize: "0.8rem", fontWeight: 500}}>days</span></div>
                            </div>
                            <div className="stat-box">
                                <div className="stat-label">Overdue Rate</div>
                                <div className="stat-val" style={{color: statsNumpy.overdue_rate_pct > 15 ? "var(--danger)" : "var(--success)"}}>
                                    {statsNumpy.overdue_rate_pct}%
                                </div>
                            </div>
                            <div className="stat-box">
                                <div className="stat-label">Avg Borrows / Book</div>
                                <div className="stat-val">{statsNumpy.avg_borrows_per_book}</div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Expected Output 1: Most-Borrowed Books Report */}
            <div className="card">
                <div className="card-header">
                    <h3><i className="fa-solid fa-trophy" style={{color: "var(--warning)"}}></i> Expected Output 1: Most-Borrowed Books Report</h3>
                    <span className="badge badge-info">Pandas Aggregation</span>
                </div>
                <div className="card-body">
                    <div style={{display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(450px, 1fr))", gap: "20px", alignItems: "center"}}>
                        <div>
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Rank</th>
                                        <th>Book Title</th>
                                        <th>Category</th>
                                        <th>Times Borrowed</th>
                                        <th>Unique Borrowers</th>
                                        <th>Avg Duration</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {popularBooks.map((b, idx) => (
                                        <tr key={b.book_id}>
                                            <td style={{fontWeight: 800, color: idx === 0 ? "var(--warning)" : "var(--text-muted)"}}>
                                                #{idx + 1}
                                            </td>
                                            <td style={{fontWeight: 600}}>{b.title}</td>
                                            <td><span className="badge badge-secondary">{b.category}</span></td>
                                            <td style={{fontWeight: 700, color: "var(--primary)"}}>{b.times_borrowed}</td>
                                            <td>{b.unique_borrowers}</td>
                                            <td>{b.avg_duration_days} days</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        <div style={{textAlign: "center"}}>
                            {charts && charts.popular_books_chart && (
                                <img src={charts.popular_books_chart} alt="Popular Books Chart" style={{maxWidth: "100%", borderRadius: "8px"}} />
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Expected Output 2: Overdue-Loan List */}
            <div className="card">
                <div className="card-header">
                    <h3><i className="fa-solid fa-circle-exclamation" style={{color: "var(--danger)"}}></i> Expected Output 2: Overdue-Loan List</h3>
                    <span className="badge badge-danger">{overdueLoans.length} Loans Overdue</span>
                </div>
                <div className="card-body">
                    {overdueLoans.length === 0 ? (
                        <div className="alert-banner alert-info">
                            <i className="fa-solid fa-circle-check"></i>
                            <div>All active book loans are currently within their permitted due dates. No overdue records.</div>
                        </div>
                    ) : (
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Loan ID</th>
                                    <th>Book Title</th>
                                    <th>Category</th>
                                    <th>Borrower Name</th>
                                    <th>Roll Number</th>
                                    <th>Issue Date</th>
                                    <th>Due Date</th>
                                    <th>Days Overdue</th>
                                    <th>Estimated Fine</th>
                                </tr>
                            </thead>
                            <tbody>
                                {overdueLoans.map(loan => (
                                    <tr key={loan.loan_id} style={{backgroundColor: "#fff5f5"}}>
                                        <td style={{fontFamily: "monospace", fontWeight: 700}}>#{loan.loan_id}</td>
                                        <td style={{fontWeight: 600}}>{loan.title}</td>
                                        <td><span className="badge badge-secondary">{loan.category}</span></td>
                                        <td style={{fontWeight: 600}}>{loan.borrower_name}</td>
                                        <td style={{fontFamily: "monospace"}}>{loan.roll_no}</td>
                                        <td>{loan.issue_date}</td>
                                        <td style={{color: "var(--danger)", fontWeight: 700}}>{loan.due_date}</td>
                                        <td><span className="badge badge-danger">{loan.days_overdue} days</span></td>
                                        <td style={{fontWeight: 800, color: "var(--danger)"}}>${loan.estimated_fine}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>

            {/* Expected Output 3 & 4: Monthly Circulation Chart & Category Summary */}
            <div style={{display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(480px, 1fr))", gap: "24px"}}>
                {/* Expected Output 3 */}
                <div className="card">
                    <div className="card-header">
                        <h3><i className="fa-solid fa-chart-line" style={{color: "var(--primary)"}}></i> Expected Output 3: Monthly Circulation Chart</h3>
                    </div>
                    <div className="card-body" style={{textAlign: "center"}}>
                        {charts && charts.monthly_circulation_chart && (
                            <img src={charts.monthly_circulation_chart} alt="Monthly Circulation" style={{maxWidth: "100%", borderRadius: "8px"}} />
                        )}
                        <table className="data-table" style={{marginTop: "16px"}}>
                            <thead>
                                <tr>
                                    <th>Year-Month</th>
                                    <th>Total Loans</th>
                                    <th>Returned</th>
                                    <th>Overdue</th>
                                </tr>
                            </thead>
                            <tbody>
                                {monthlyTrends.map(m => (
                                    <tr key={m.year_month}>
                                        <td style={{fontWeight: 600}}>{m.year_month}</td>
                                        <td style={{fontWeight: 700, color: "var(--primary)"}}>{m.total_loans}</td>
                                        <td>{m.returned_count}</td>
                                        <td style={{color: m.overdue_count > 0 ? "var(--danger)" : "inherit"}}>{m.overdue_count}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Expected Output 4 */}
                <div className="card">
                    <div className="card-header">
                        <h3><i className="fa-solid fa-chart-pie" style={{color: "var(--success)"}}></i> Expected Output 4: Category Summary</h3>
                    </div>
                    <div className="card-body">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Category</th>
                                    <th>Titles</th>
                                    <th>Total Copies</th>
                                    <th>Available</th>
                                    <th>Total Borrows</th>
                                    <th>Utilization</th>
                                </tr>
                            </thead>
                            <tbody>
                                {categorySummary.map(c => (
                                    <tr key={c.category}>
                                        <td style={{fontWeight: 600}}>{c.category}</td>
                                        <td>{c.total_titles}</td>
                                        <td>{c.total_copies}</td>
                                        <td style={{color: c.available_copies > 0 ? "var(--success)" : "var(--danger)", fontWeight: 600}}>
                                            {c.available_copies}
                                        </td>
                                        <td style={{fontWeight: 700, color: "var(--primary)"}}>{c.total_borrows}</td>
                                        <td>
                                            <div style={{display: "flex", alignItems: "center", gap: "8px"}}>
                                                <div style={{flex: 1, height: "6px", background: "#e2e8f0", borderRadius: "3px", overflow: "hidden"}}>
                                                    <div style={{width: `${Math.min(c.utilization_pct, 100)}%`, height: "100%", background: "var(--primary)"}}></div>
                                                </div>
                                                <span style={{fontSize: "0.76rem", fontWeight: 700}}>{c.utilization_pct}%</span>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}

// ============================================================
// MODAL FORMS: ISSUE BOOK, BOOK CREATE/EDIT, BORROWER CREATE, SETTINGS
// ============================================================

function IssueBookModal({ preselectedBook, onClose, onSuccess, showNotification }) {
    const [books, setBooks] = useState([]);
    const [borrowers, setBorrowers] = useState([]);
    const [selectedBookId, setSelectedBookId] = useState(preselectedBook ? preselectedBook.book_id : "");
    const [selectedBorrowerId, setSelectedBorrowerId] = useState("");
    const [loanDays, setLoanDays] = useState(14);
    const [issueDate, setIssueDate] = useState(new Date().toISOString().slice(0, 10));
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        apiRequest("/api/books").then(data => setBooks(data));
        apiRequest("/api/borrowers").then(data => setBorrowers(data));
        apiRequest("/api/settings").then(s => setLoanDays(s.default_loan_days));
    }, []);

    const selectedBookObj = books.find(b => b.book_id === Number(selectedBookId));

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!selectedBookId || !selectedBorrowerId) {
            showNotification("Please select both a book and a borrower.", "error");
            return;
        }

        if (selectedBookObj && selectedBookObj.copies_available <= 0) {
            showNotification("Cannot issue: Selected book has 0 copies available.", "error");
            return;
        }

        setSubmitting(true);
        try {
            await apiRequest("/api/loans/issue", {
                method: "POST",
                body: JSON.stringify({
                    book_id: Number(selectedBookId),
                    borrower_id: Number(selectedBorrowerId),
                    issue_date: issueDate,
                    loan_period_days: Number(loanDays)
                })
            });
            onSuccess();
        } catch (err) {
            showNotification(err.message, "error");
            setSubmitting(false);
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <div className="modal-header">
                    <h3>Issue Book to Patron</h3>
                    <button className="modal-close" onClick={onClose}>&times;</button>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className="modal-body">
                        <div className="form-group">
                            <label>Select Book *</label>
                            <select 
                                value={selectedBookId} 
                                onChange={(e) => setSelectedBookId(e.target.value)}
                                required
                            >
                                <option value="">-- Choose a Book --</option>
                                {books.map(b => (
                                    <option key={b.book_id} value={b.book_id} disabled={b.copies_available <= 0}>
                                        {b.title} (Available: {b.copies_available}/{b.total_copies}) {b.copies_available <= 0 ? "- [OUT OF STOCK]" : ""}
                                    </option>
                                ))}
                            </select>
                            {selectedBookObj && (
                                <div className="help-text">
                                    Author: {selectedBookObj.author} | Category: {selectedBookObj.category} | ISBN: {selectedBookObj.isbn}
                                </div>
                            )}
                        </div>

                        <div className="form-group">
                            <label>Select Borrower *</label>
                            <select 
                                value={selectedBorrowerId} 
                                onChange={(e) => setSelectedBorrowerId(e.target.value)}
                                required
                            >
                                <option value="">-- Choose a Registered Patron --</option>
                                {borrowers.map(b => (
                                    <option key={b.borrower_id} value={b.borrower_id}>
                                        {b.borrower_name} ({b.roll_no})
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div style={{display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px"}}>
                            <div className="form-group">
                                <label>Issue Date</label>
                                <input 
                                    type="date" 
                                    value={issueDate} 
                                    onChange={(e) => setIssueDate(e.target.value)}
                                    required 
                                />
                            </div>
                            <div className="form-group">
                                <label>Loan Period (Days)</label>
                                <input 
                                    type="number" 
                                    min="1" 
                                    max="180" 
                                    value={loanDays} 
                                    onChange={(e) => setLoanDays(e.target.value)}
                                    required 
                                />
                            </div>
                        </div>
                    </div>
                    <div className="modal-footer">
                        <button type="button" className="btn btn-outline" onClick={onClose}>Cancel</button>
                        <button type="submit" className="btn btn-primary" disabled={submitting}>
                            {submitting ? "Processing..." : "Confirm & Issue Book"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

function BookFormModal({ title, initialData, onClose, onSubmit }) {
    const [formData, setFormData] = useState({
        isbn: initialData ? initialData.isbn : "",
        title: initialData ? initialData.title : "",
        author: initialData ? initialData.author : "",
        category: initialData ? initialData.category : "Computer Science",
        total_copies: initialData ? initialData.total_copies : 3,
        copies_available: initialData ? initialData.copies_available : 3
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(formData);
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <div className="modal-header">
                    <h3>{title}</h3>
                    <button className="modal-close" onClick={onClose}>&times;</button>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className="modal-body">
                        <div className="form-group">
                            <label>ISBN *</label>
                            <input 
                                type="text" 
                                value={formData.isbn} 
                                onChange={(e) => setFormData({...formData, isbn: e.target.value})}
                                placeholder="e.g. 978-0131103627"
                                required
                                disabled={!!initialData}
                            />
                        </div>
                        <div className="form-group">
                            <label>Book Title *</label>
                            <input 
                                type="text" 
                                value={formData.title} 
                                onChange={(e) => setFormData({...formData, title: e.target.value})}
                                placeholder="Enter book title"
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>Author(s) *</label>
                            <input 
                                type="text" 
                                value={formData.author} 
                                onChange={(e) => setFormData({...formData, author: e.target.value})}
                                placeholder="e.g. Brian W. Kernighan"
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>Category *</label>
                            <input 
                                type="text" 
                                value={formData.category} 
                                onChange={(e) => setFormData({...formData, category: e.target.value})}
                                placeholder="e.g. Computer Science, Mathematics, Physics"
                                required
                            />
                        </div>
                        <div style={{display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px"}}>
                            <div className="form-group">
                                <label>Total Physical Copies</label>
                                <input 
                                    type="number" 
                                    min="1" 
                                    value={formData.total_copies} 
                                    onChange={(e) => {
                                        const tot = parseInt(e.target.value) || 1;
                                        setFormData({
                                            ...formData, 
                                            total_copies: tot,
                                            copies_available: Math.min(formData.copies_available, tot)
                                        });
                                    }}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>Available Copies</label>
                                <input 
                                    type="number" 
                                    min="0" 
                                    max={formData.total_copies}
                                    value={formData.copies_available} 
                                    onChange={(e) => setFormData({...formData, copies_available: parseInt(e.target.value) || 0})}
                                    required
                                />
                            </div>
                        </div>
                    </div>
                    <div className="modal-footer">
                        <button type="button" className="btn btn-outline" onClick={onClose}>Cancel</button>
                        <button type="submit" className="btn btn-primary">Save Book</button>
                    </div>
                </form>
            </div>
        </div>
    );
}

function BorrowerFormModal({ onClose, onSubmit }) {
    const [formData, setFormData] = useState({
        borrower_name: "",
        roll_no: "",
        email: "",
        contact: ""
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(formData);
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <div className="modal-header">
                    <h3>Register New Borrower</h3>
                    <button className="modal-close" onClick={onClose}>&times;</button>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className="modal-body">
                        <div className="form-group">
                            <label>Full Name *</label>
                            <input 
                                type="text" 
                                value={formData.borrower_name} 
                                onChange={(e) => setFormData({...formData, borrower_name: e.target.value})}
                                placeholder="e.g. Aarav Sharma"
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>Roll Number / Patron ID *</label>
                            <input 
                                type="text" 
                                value={formData.roll_no} 
                                onChange={(e) => setFormData({...formData, roll_no: e.target.value})}
                                placeholder="e.g. CS2023001"
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>Email Address</label>
                            <input 
                                type="email" 
                                value={formData.email} 
                                onChange={(e) => setFormData({...formData, email: e.target.value})}
                                placeholder="patron@college.edu"
                            />
                        </div>
                        <div className="form-group">
                            <label>Contact Number</label>
                            <input 
                                type="text" 
                                value={formData.contact} 
                                onChange={(e) => setFormData({...formData, contact: e.target.value})}
                                placeholder="e.g. 9876543210"
                            />
                        </div>
                    </div>
                    <div className="modal-footer">
                        <button type="button" className="btn btn-outline" onClick={onClose}>Cancel</button>
                        <button type="submit" className="btn btn-primary">Register Borrower</button>
                    </div>
                </form>
            </div>
        </div>
    );
}

function SettingsModal({ onClose, showNotification, triggerRefresh }) {
    const [settings, setSettings] = useState({
        default_loan_days: 14,
        daily_overdue_fine: 1.50,
        active_engine: "mysql",
        db_name: "library_db"
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        apiRequest("/api/settings").then(data => {
            setSettings(data);
            setLoading(false);
        });
    }, []);

    const handleSave = async (e) => {
        e.preventDefault();
        try {
            await apiRequest("/api/settings", {
                method: "PUT",
                body: JSON.stringify({
                    default_loan_days: Number(settings.default_loan_days),
                    daily_overdue_fine: Number(settings.daily_overdue_fine)
                })
            });
            showNotification("System settings updated successfully!");
            triggerRefresh();
            onClose();
        } catch (err) {
            showNotification(err.message, "error");
        }
    };

    const handleReseed = async () => {
        if (!confirm("Are you sure? This will reset all books, borrowers, and loans to the fresh initial demo dataset.")) return;
        try {
            await apiRequest("/api/database/reseed", { method: "POST" });
            showNotification("Database successfully reset and reseeded!");
            triggerRefresh();
            onClose();
        } catch (err) {
            showNotification(err.message, "error");
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <div className="modal-header">
                    <h3>System Settings & Database</h3>
                    <button className="modal-close" onClick={onClose}>&times;</button>
                </div>
                <form onSubmit={handleSave}>
                    <div className="modal-body">
                        <div style={{background: "#f8fafc", padding: "12px 16px", borderRadius: "8px", marginBottom: "16px", border: "1px solid #e2e8f0"}}>
                            <div style={{fontSize: "0.85rem", color: "var(--text-secondary)"}}>
                                <strong>Active Database Engine:</strong> <span className={`engine-badge ${settings.active_engine}`}>{settings.active_engine.toUpperCase()}</span>
                            </div>
                            <div style={{fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "4px"}}>
                                Target Database: <code>{settings.db_name}</code>
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Default Loan Duration (Days)</label>
                            <input 
                                type="number" 
                                min="1" 
                                max="180"
                                value={settings.default_loan_days}
                                onChange={(e) => setSettings({...settings, default_loan_days: e.target.value})}
                                required
                            />
                            <div className="help-text">Used to compute due date when a new book loan is issued.</div>
                        </div>

                        <div className="form-group">
                            <label>Daily Overdue Fine ($ / currency unit)</label>
                            <input 
                                type="number" 
                                step="0.25"
                                min="0" 
                                value={settings.daily_overdue_fine}
                                onChange={(e) => setSettings({...settings, daily_overdue_fine: e.target.value})}
                                required
                            />
                            <div className="help-text">Rate charged per day overdue past the due date.</div>
                        </div>

                        <hr style={{border: "none", borderTop: "1px solid #e2e8f0", margin: "20px 0"}} />

                        <div style={{display: "flex", justifyContent: "space-between", alignItems: "center"}}>
                            <div>
                                <strong style={{fontSize: "0.88rem"}}>Reset & Reseed Demo Data</strong>
                                <div style={{fontSize: "0.78rem", color: "var(--text-muted)"}}>Restores original sample records for demonstration.</div>
                            </div>
                            <button type="button" className="btn btn-outline btn-sm" onClick={handleReseed} style={{color: "var(--warning)", borderColor: "#fde68a"}}>
                                <i className="fa-solid fa-arrows-rotate"></i> Reset Data
                            </button>
                        </div>
                    </div>
                    <div className="modal-footer">
                        <button type="button" className="btn btn-outline" onClick={onClose}>Cancel</button>
                        <button type="submit" className="btn btn-primary">Save Settings</button>
                    </div>
                </form>
            </div>
        </div>
    );
}

// Render root React component
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
