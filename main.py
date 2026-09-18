import tkinter as tk
from tkinter import ttk, messagebox, font
from database import get_connection, init_db
from modules.auth import LoginWindow
from modules.books import BooksPage
from modules.students import StudentsPage
from modules.loans import LoansPage
from modules.statistics import StatisticsPage

class App:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()
        init_db()
        self.apply_theme()
        LoginWindow(root, self.login_success)

    def db(self):
        return get_connection()

    def apply_theme(self):
        style = ttk.Style()
        style.theme_use("clam")

        system_fonts = font.families()
        if "Aptos" in system_fonts:
            self.font_family = "Aptos"
        elif "Segoe UI" in system_fonts:
            self.font_family = "Segoe UI"
        else:
            self.font_family = "Arial"

        # Bảng màu mềm (Soft Modern Palette)
        BG_COLOR = "#f1f5f9"  # Xám phấn dịu mắt
        HEADER_BG = "#0f172a"  # Xanh Slate tối
        PRIMARY = "#2563eb"  # Xanh thương hiệu
        DANGER = "#e11d48"  # Đỏ Rose mềm

        self.root.configure(bg=BG_COLOR)

        # Cấu hình chung
        style.configure(".", background=BG_COLOR, font=(self.font_family, 10))
        style.configure("TFrame", background=BG_COLOR)
        style.configure("Header.TFrame", background=HEADER_BG)

        style.configure("HeaderTitle.TLabel",
                        background=HEADER_BG,
                        foreground="#ffffff",
                        font=(self.font_family, 15, "bold"))
        style.configure("HeaderUser.TLabel",
                        background=HEADER_BG,
                        foreground="#94a3b8",
                        font=(self.font_family, 10))

        # Nút bấm dạng phẳng (Flat buttons)
        style.configure("TButton",
                        font=(self.font_family, 10),
                        padding=(10, 6),
                        relief="flat",
                        borderwidth=0)
        style.configure("Logout.TButton",
                        font=(self.font_family, 9, "bold"),
                        foreground=DANGER,
                        background="#ffe4e6",
                        padding=(10, 4),
                        relief="flat",
                        borderwidth=0)
        style.map("Logout.TButton",
                  background=[("active", "#fecdd3"), ("pressed", "#fda4af")],
                  foreground=[("active", "#be123c")])

        # Triệt tiêu viền cứng của Tabs (Flat Pill style)
        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab",
                        padding=[20, 8],
                        font=(self.font_family, 10, "bold"),
                        background="#e2e8f0",
                        foreground="#475569",
                        borderwidth=0,
                        relief="flat")
        style.map("TNotebook.Tab",
                  background=[("selected", PRIMARY), ("active", "#cbd5e1")],
                  foreground=[("selected", "#ffffff"), ("active", "#0f172a")])

        # Treeview phẳng, bỏ viền thô
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#0f172a",
                        fieldbackground="#ffffff",
                        rowheight=32,
                        font=(self.font_family, 10),
                        borderwidth=0,
                        relief="flat")
        style.configure("Treeview.Heading",
                        background="#e2e8f0",
                        foreground="#1e293b",
                        font=(self.font_family, 10, "bold"),
                        padding=6,
                        relief="flat")
        style.map("Treeview", background=[("selected", PRIMARY)], foreground=[("selected", "#ffffff")])
    def login_success(self, username, role):
        self.root.deiconify()
        self.root.title("HỆ THỐNG QUẢN LÝ THƯ VIỆN")
        self.root.geometry("1180x720")
        self.root.minsize(1000, 620)

        # Thanh Header
        self.header = ttk.Frame(self.root, style="Header.TFrame", padding=(15, 10))
        self.header.pack(fill="x")

        ttk.Label(self.header, text="HỆ THỐNG QUẢN LÝ THƯ VIỆN", style="HeaderTitle.TLabel").pack(side="left")

        user_frame = ttk.Frame(self.header, style="Header.TFrame")
        user_frame.pack(side="right")
        role_tag = f"Vai trò: {role.upper()}" if role else ""
        ttk.Label(user_frame, text=f"👤 {username}  |  {role_tag}    ", style="HeaderUser.TLabel").pack(side="left")
        ttk.Button(user_frame, text="Đăng xuất", style="Logout.TButton", command=self.logout).pack(side="left")

        # Cụm Tab chức năng
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=12, pady=10)

        self.dash = ttk.Frame(self.nb)
        self.books = ttk.Frame(self.nb)
        self.students = ttk.Frame(self.nb)
        self.loans = ttk.Frame(self.nb)
        self.stats = ttk.Frame(self.nb)

        tabs = [
            (self.dash, "  Tổng quan  "),
            (self.books, "  Quản lý sách  "),
            (self.students, "  Sinh viên  "),
            (self.loans, "  Mượn / Trả  "),
            (self.stats, "  Thống kê  ")
        ]
        for tab, title in tabs:
            self.nb.add(tab, text=title)

        # Khởi tạo các trang nghiệp vụ
        BooksPage(self.books, self.db, self.refresh)
        StudentsPage(self.students, self.db, self.refresh)
        LoansPage(self.loans, self.db, self.refresh)
        self.stats_page = StatisticsPage(self.stats, self.db)

        self.build_dashboard()
        self.refresh()

    def build_dashboard(self):
        f = ttk.Frame(self.dash, padding=30)
        f.pack(fill="both", expand=True)

        ttk.Label(f, text="TRUNG TÂM ĐIỀU HÀNH THƯ VIỆN",
                  font=(self.font_family, 18, "bold"), foreground="#0f172a").pack(anchor="w", pady=(0, 5))
        ttk.Label(f, text="Theo dõi các chỉ số và dữ liệu lưu thông thời gian thực",
                  font=(self.font_family, 10), foreground="#64748b").pack(anchor="w", pady=(0, 25))

        # Thẻ Thống kê phẳng (Loại bỏ highlight viền đen)
        self.cards_frame = ttk.Frame(f)
        self.cards_frame.pack(fill="x", pady=10)

        self.card_labels = {}
        cards_config = [
            ("books", "Tổng đầu sách", "#ffffff", "#1d4ed8"),
            ("available", "Sách sẵn có", "#ffffff", "#15803d"),
            ("active", "Đang mượn", "#ffffff", "#b45309"),
            ("overdue", "Quá hạn", "#ffffff", "#be123c"),
            ("students", "Tổng sinh viên", "#ffffff", "#334155"),
        ]

        for i, (key, title, bg, fg) in enumerate(cards_config):
            # Dùng borderwidth=0 để thẻ hòa vào nền, không bị viền hộp cứng
            card = tk.Frame(self.cards_frame, bg=bg, padx=18, pady=18, relief="flat", borderwidth=0)
            card.grid(row=0, column=i, padx=8, sticky="nsew")
            self.cards_frame.columnconfigure(i, weight=1)

            lbl_title = tk.Label(card, text=title.upper(), font=(self.font_family, 8, "bold"), bg=bg, fg="#94a3b8")
            lbl_title.pack(anchor="w")

            lbl_val = tk.Label(card, text="0", font=(self.font_family, 22, "bold"), bg=bg, fg=fg)
            lbl_val.pack(anchor="w", pady=(6, 0))
            self.card_labels[key] = lbl_val

        # Hộp thông tin mềm
        tip_box = tk.Frame(f, bg="#ffffff", padx=16, pady=12, relief="flat", borderwidth=0)
        tip_box.pack(fill="x", pady=30)
        tk.Label(tip_box,
                 text="💡 Hướng dẫn: Điều hướng qua các tab phía trên để tra cứu danh mục, quản lý thông tin sinh viên hoặc lập phiếu mượn/trả.",
                 bg="#ffffff", fg="#475569", font=(self.font_family, 10)).pack(anchor="w")

    def refresh(self):
        if not hasattr(self, "card_labels"):
            return
        conn = self.db()
        books = conn.execute("SELECT COALESCE(SUM(quantity),0) FROM books").fetchone()[0]
        available = conn.execute("SELECT COALESCE(SUM(available),0) FROM books").fetchone()[0]
        students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        active = conn.execute("SELECT COUNT(*) FROM loans WHERE status='Đang mượn'").fetchone()[0]
        overdue = conn.execute("SELECT COUNT(*) FROM loans WHERE status='Đang mượn' AND due_date < date('now')").fetchone()[0]
        conn.close()

        self.card_labels["books"].config(text=f"{books:,}")
        self.card_labels["available"].config(text=f"{available:,}")
        self.card_labels["students"].config(text=f"{students:,}")
        self.card_labels["active"].config(text=f"{active:,}")
        self.card_labels["overdue"].config(text=f"{overdue:,}")

        if hasattr(self, "stats_page"):
            self.stats_page.load()

    def logout(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn đăng xuất tài khoản?"):
            for widget in self.root.winfo_children():
                widget.destroy()
            self.root.withdraw()
            LoginWindow(self.root, self.login_success)

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()