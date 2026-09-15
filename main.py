import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection, init_db
from modules.auth import LoginWindow
from modules.books import BooksPage
from modules.students import StudentsPage
from modules.loans import LoansPage
from modules.statistics import StatisticsPage

class App:
    def __init__(self, root):
        self.root=root
        self.root.withdraw()
        init_db()
        LoginWindow(root,self.login_success)

    def db(self):
        return get_connection()

    def login_success(self,username,role):
        self.root.deiconify()
        self.root.title("HỆ THỐNG QUẢN LÝ THƯ VIỆN")
        self.root.geometry("1180x720")
        self.root.minsize(1000,620)

        header=ttk.Frame(self.root);header.pack(fill="x",padx=10,pady=8)
        ttk.Label(header,text="📚 QUẢN LÝ THƯ VIỆN",font=("Arial",20,"bold")).pack(side="left")
        ttk.Label(header,text=f"Đăng nhập: {username} ({role})").pack(side="right")

        self.nb=ttk.Notebook(self.root);self.nb.pack(fill="both",expand=True,padx=8,pady=5)
        self.dash=ttk.Frame(self.nb);self.books=ttk.Frame(self.nb);self.students=ttk.Frame(self.nb)
        self.loans=ttk.Frame(self.nb);self.stats=ttk.Frame(self.nb)
        for tab,title in [(self.dash,"Tổng quan"),(self.books,"Quản lý sách"),(self.students,"Sinh viên"),
                          (self.loans,"Mượn / Trả"),(self.stats,"Thống kê")]:
            self.nb.add(tab,text=title)

        BooksPage(self.books,self.db,self.refresh)
        StudentsPage(self.students,self.db,self.refresh)
        LoansPage(self.loans,self.db,self.refresh)
        self.stats_page=StatisticsPage(self.stats,self.db)
        self.build_dashboard()
        self.refresh()

    def build_dashboard(self):
        f=ttk.Frame(self.dash,padding=30);f.pack(fill="both",expand=True)
        ttk.Label(f,text="HỆ THỐNG QUẢN LÝ THƯ VIỆN",font=("Arial",24,"bold")).pack(pady=20)
        ttk.Label(f,text="Ứng dụng desktop Python + Tkinter + SQLite",font=("Arial",13)).pack(pady=5)
        self.info=ttk.Label(f,text="",font=("Arial",15));self.info.pack(pady=30)
        ttk.Label(f,text="Chọn các tab phía trên để quản lý sách, sinh viên, mượn/trả và xem thống kê.",
                  font=("Arial",11)).pack()

    def refresh(self):
        if not hasattr(self,"info"):return
        conn=self.db()
        books=conn.execute("SELECT COALESCE(SUM(quantity),0) FROM books").fetchone()[0]
        available=conn.execute("SELECT COALESCE(SUM(available),0) FROM books").fetchone()[0]
        students=conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        active=conn.execute("SELECT COUNT(*) FROM loans WHERE status='Đang mượn'").fetchone()[0]
        overdue=conn.execute("SELECT COUNT(*) FROM loans WHERE status='Đang mượn' AND due_date < date('now')").fetchone()[0]
        conn.close()
        self.info.config(text=f"Tổng đầu sách: {books}    |    Sách còn: {available}\n"
                              f"Sinh viên: {students}    |    Đang mượn: {active}    |    Quá hạn: {overdue}")
        if hasattr(self,"stats_page"):self.stats_page.load()

if __name__=="__main__":
    root=tk.Tk()
    App(root)
    root.mainloop()
