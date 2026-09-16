import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "library.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'staff'
    );

    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        author TEXT,
        category TEXT,
        publisher TEXT,
        year INTEGER,
        quantity INTEGER NOT NULL DEFAULT 0,
        available INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        class_name TEXT,
        phone TEXT,
        email TEXT
    );

    CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        borrow_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        return_date TEXT,
        status TEXT NOT NULL DEFAULT 'Đang mượn',
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(book_id) REFERENCES books(id)
    );
    """)
    if cur.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        cur.execute("INSERT INTO users(username,password,role) VALUES (?,?,?)",
                    ("admin","123456","admin"))
        cur.execute("INSERT INTO users(username,password,role) VALUES (?,?,?)",
                    ("nhanvien","123456","staff"))
    if cur.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 0:
        sample_books = [
            ("S001","Lập trình Python","Nguyễn Văn A","CNTT","NXB Giáo dục",2024,10),
            ("S002","Cơ sở dữ liệu","Trần Văn B","CNTT","NXB Thống kê",2023,8),
            ("S003","Lập trình C++","Lê Văn C","CNTT","NXB Khoa học",2022,6),
            ("S004","Mạng máy tính","Phạm Văn D","Mạng","NXB Bách khoa",2024,7),
            ("S005","Kỹ năng giao tiếp","Nguyễn Thị E","Kỹ năng","NXB Lao động",2021,5),
        ]
        cur.executemany("""INSERT INTO books
            (book_code,name,author,category,publisher,year,quantity,available)
            VALUES (?,?,?,?,?,?,?,?)""",
            [x + (x[-1],) for x in sample_books])
    if cur.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
        cur.executemany("""INSERT INTO students
            (student_code,name,class_name,phone,email) VALUES (?,?,?,?,?)""", [
            ("SV001","Nguyễn Văn An","CNTT01","0901000001","an@example.com"),
            ("SV002","Trần Thị Lan","CNTT02","0901000002","lan@example.com"),
            ("SV003","Lê Hoàng Nam","CNTT03","0901000003","nam@example.com"),
        ])
    conn.commit()
    conn.close()
