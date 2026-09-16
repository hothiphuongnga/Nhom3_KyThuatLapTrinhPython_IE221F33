import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
import csv

class StatisticsPage:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.build()

    def build(self):
        self.cards = ttk.Frame(self.parent)
        self.cards.pack(fill="x", padx=10, pady=10)
        
        self.vars = [tk.StringVar(value="0") for _ in range(4)]
        titles = ["Tổng sách", "Tổng sinh viên", "Đang mượn", "Quá hạn"]
        
        for i, (title, var) in enumerate(zip(titles, self.vars)):
            f = ttk.LabelFrame(self.cards, text=title)
            f.grid(row=0, column=i, padx=6, sticky="nsew")
            self.cards.columnconfigure(i, weight=1)
            ttk.Label(f, textvariable=var, font=("Arial", 18, "bold")).pack(padx=30, pady=18)

        btn_frame = ttk.Frame(self.parent)
        btn_frame.pack(fill="x", padx=10)
        ttk.Button(btn_frame, text="Cập nhật thống kê", command=self.load).pack(side="left")
        ttk.Button(btn_frame, text="Xuất CSV", command=self.export_csv).pack(side="left", padx=6)

        columns = ("student", "book", "borrow_date", "due_date", "remaining", "status")
        self.tree = ttk.Treeview(self.parent, columns=columns, show="headings")
        
        self.tree.heading("student", text="Sinh viên mượn")
        self.tree.heading("book", text="Tên sách")
        self.tree.heading("borrow_date", text="Ngày mượn")
        self.tree.heading("due_date", text="Hạn trả")
        self.tree.heading("remaining", text="Còn lại / Trạng thái")
        self.tree.heading("status", text="Tình trạng")
        
        self.tree.column("student", width=160, anchor="center")
        self.tree.column("book", width=220, anchor="center")
        self.tree.column("borrow_date", width=110, anchor="center")
        self.tree.column("due_date", width=110, anchor="center")
        self.tree.column("remaining", width=140, anchor="center")
        self.tree.column("status", width=110, anchor="center")
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.load()

    def load(self):
        conn = self.db()
        
        total = conn.execute("SELECT COALESCE(SUM(quantity),0) FROM books").fetchone()[0]
        students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        active = conn.execute("SELECT COUNT(*) FROM loans WHERE status='Đang mượn'").fetchone()[0]
        overdue = conn.execute("SELECT COUNT(*) FROM loans WHERE status='Đang mượn' AND due_date < ?", (date.today().isoformat(),)).fetchone()[0]
        
        self.vars[0].set(str(total))
        self.vars[1].set(str(students))
        self.vars[2].set(str(active))
        self.vars[3].set(str(overdue))

        rows = conn.execute("""
            SELECT s.name AS student_name, b.name AS book_name, l.borrow_date, l.due_date, l.status 
            FROM loans l 
            JOIN students s ON s.id = l.student_id 
            JOIN books b ON b.id = l.book_id
            ORDER BY l.id DESC
        """).fetchall()
        
        self.tree.delete(*self.tree.get_children())
        
        today = date.today()
        for r in rows:
            due = date.fromisoformat(r["due_date"])
            delta = (due - today).days
            
            if r["status"] == "Đã trả":
                rem_text = "Đã hoàn tất"
            elif delta < 0:
                rem_text = f"Quá hạn {-delta} ngày"
            elif delta == 0:
                rem_text = "Hạn trả hôm nay"
            else:
                rem_text = f"Còn {delta} ngày"
                
            self.tree.insert("", "end", values=(
                r["student_name"], 
                r["book_name"], 
                r["borrow_date"], 
                r["due_date"], 
                rem_text, 
                r["status"]
            ))
            
        conn.close()

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="bao_cao_muon_sach.csv"
        )
        if not path:
            return

        conn = self.db()
        rows = conn.execute("""
            SELECT s.student_code, s.name, b.book_code, b.name, l.borrow_date, l.due_date, l.return_date, l.status
            FROM loans l 
            JOIN students s ON s.id = l.student_id 
            JOIN books b ON b.id = l.book_id
            ORDER BY l.id DESC
        """).fetchall()
        conn.close()

        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Mã SV", "Sinh viên", "Mã sách", "Sách", "Ngày mượn", "Hạn trả", "Ngày trả", "Trạng thái"])
                writer.writerows([tuple(r) for r in rows])
            messagebox.showinfo("Thành công", "Đã xuất báo cáo CSV thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất file: {e}")