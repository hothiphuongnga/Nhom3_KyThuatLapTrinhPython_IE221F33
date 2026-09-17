import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta, datetime


class LoansPage:
    def __init__(self, parent, db, refresh_callback=None):
        self.parent = parent
        self.db = db
        self.refresh_callback = refresh_callback
        self.smap, self.bmap = {}, {}
        self.build()

    def build(self):
        form = ttk.LabelFrame(self.parent, text="Lập phiếu mượn")
        form.pack(fill="x", padx=10, pady=8)

        ttk.Label(form, text="Sinh viên").grid(row=0, column=0, padx=5)
        self.student = ttk.Combobox(form, width=28, state="readonly")
        self.student.grid(row=0, column=1, padx=5)

        ttk.Label(form, text="Sách").grid(row=0, column=2, padx=5)
        self.book = ttk.Combobox(form, width=38, state="readonly")
        self.book.grid(row=0, column=3, padx=5)

        ttk.Label(form, text="Số ngày").grid(row=0, column=4, padx=5)
        self.days = tk.StringVar(value="14")
        ttk.Entry(form, textvariable=self.days, width=8).grid(row=0, column=5, padx=5)

        ttk.Button(form, text="Mượn", command=self.borrow).grid(row=0, column=6, padx=4)
        ttk.Button(form, text="Trả", command=self.return_book).grid(row=0, column=7, padx=4)
        ttk.Button(form, text="Gia hạn", command=self.extend_loan).grid(row=0, column=8, padx=4)
        ttk.Button(form, text="Làm mới", command=self.load).grid(row=0, column=9, padx=4)

        search = ttk.Frame(self.parent)
        search.pack(fill="x", padx=10, pady=5)
        ttk.Label(search, text="Tìm kiếm:").pack(side="left")

        self.search = tk.StringVar()
        ttk.Entry(search, textvariable=self.search, width=30).pack(side="left", padx=5)
        ttk.Button(search, text="Tìm", command=self.load).pack(side="left")
        ttk.Button(search, text="Xóa", command=self.clear_search).pack(side="left", padx=5)

        cols = ("id", "student", "book", "borrow", "due", "return", "status")
        self.tree = ttk.Treeview(self.parent, columns=cols, show="headings")

        for c, h, w in zip(
            cols,
            ["ID", "Sinh viên", "Sách", "Ngày mượn", "Hạn trả", "Ngày trả", "Trạng thái"],
            [45, 160, 210, 100, 100, 100, 110]
        ):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=8)
        self.load()

    def load(self):
        conn = self.db()

        students = conn.execute(
            "SELECT id,student_code,name FROM students ORDER BY student_code"
        ).fetchall()
        books = conn.execute(
            "SELECT id,book_code,name,available FROM books ORDER BY book_code"
        ).fetchall()

        self.smap, self.bmap = {}, {}

        for r in students:
            self.smap[r["student_code"] + " - " + r["name"]] = r["id"]

        for r in books:
            if r["available"] > 0:
                text = r["book_code"] + " - " + r["name"] + " (còn " + str(r["available"]) + ")"
                self.bmap[text] = r["id"]

        self.student["values"] = list(self.smap)
        self.book["values"] = list(self.bmap)

        sql = """SELECT l.id,s.student_code||' - '||s.name,
                 b.book_code||' - '||b.name,l.borrow_date,l.due_date,
                 COALESCE(l.return_date,''),l.status
                 FROM loans l JOIN students s ON s.id=l.student_id
                 JOIN books b ON b.id=l.book_id"""

        rows = conn.execute(sql + " ORDER BY l.id DESC").fetchall()

        self.tree.delete(*self.tree.get_children())

        for r in rows:
            v = list(r)
            self.tree.insert("", "end", values=v)

        conn.close()

    def borrow(self):
        if self.student.get() not in self.smap or self.book.get() not in self.bmap:
            return messagebox.showwarning("Thông báo", "Chọn sinh viên và sách.")

        try:
            days = int(self.days.get())
            if days < 1 or days > 365:
                raise ValueError
        except ValueError:
            return messagebox.showerror("Lỗi", "Số ngày phải từ 1 đến 365.")

        sid, bid = self.smap[self.student.get()], self.bmap[self.book.get()]
        conn = self.db()
        book = conn.execute("SELECT available FROM books WHERE id=?", (bid,)).fetchone()

        if not book or book["available"] <= 0:
            conn.close()
            return messagebox.showerror("Lỗi", "Sách đã hết.")

        d, due = date.today(), date.today() + timedelta(days=days)

        conn.execute(
            "INSERT INTO loans(student_id,book_id,borrow_date,due_date,status) VALUES(?,?,?,?,?)",
            (sid, bid, d.isoformat(), due.isoformat(), "Đang mượn")
        )
        conn.execute("UPDATE books SET available=available-1 WHERE id=?", (bid,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Thành công", "Mượn sách thành công.\nHạn trả: " + due.strftime("%d/%m/%Y"))
        self.load()
        if self.refresh_callback:
            self.refresh_callback()

    def return_book(self):
        pass

    def extend_loan(self):
        pass

    def clear_search(self):
        pass