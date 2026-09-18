import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection


class LoginWindow:
    def __init__(self, parent, on_success):
        self.parent = parent
        self.on_success = on_success
        self.top = tk.Toplevel(parent)
        self.top.title("Đăng nhập - Quản lý thư viện")
        self.top.resizable(False, False)
        self.top.protocol("WM_DELETE_WINDOW", self.on_close)

        width, height = 400, 440
        self.center_window(width, height)

        self.setup_ui()

    def center_window(self, width, height):
        self.top.update_idletasks()
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.top.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        BG_COLOR = "#f8fafc"
        CARD_BG = "#ffffff"
        PRIMARY = "#2563eb"
        PRIMARY_HOVER = "#1d4ed8"
        TEXT_MAIN = "#0f172a"
        TEXT_MUTED = "#64748b"

        self.top.configure(bg=BG_COLOR)

        card = tk.Frame(self.top, bg=CARD_BG, padx=30, pady=30, highlightthickness=1, highlightbackground="#e2e8f0")
        card.pack(fill="both", expand=True, padx=20, pady=20)

        lbl_icon = tk.Label(card, text="📚", font=("Segoe UI Emoji", 32), bg=CARD_BG)
        lbl_icon.pack(pady=(0, 2))

        lbl_title = tk.Label(card, text="HỆ THỐNG THƯ VIỆN", font=("Segoe UI", 15, "bold"), bg=CARD_BG, fg=TEXT_MAIN)
        lbl_title.pack()

        lbl_sub = tk.Label(card, text="Vui lòng đăng nhập để tiếp tục", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_MUTED)
        lbl_sub.pack(pady=(2, 20))

        lbl_user = tk.Label(card, text="Tài khoản", font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg="#334155")
        lbl_user.pack(anchor="w")

        self.ent_user = ttk.Entry(card, font=("Segoe UI", 10))
        self.ent_user.pack(fill="x", pady=(4, 14), ipady=4)
        self.ent_user.focus()

        lbl_pass = tk.Label(card, text="Mật khẩu", font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg="#334155")
        lbl_pass.pack(anchor="w")

        self.ent_pass = ttk.Entry(card, show="•", font=("Segoe UI", 10))
        self.ent_pass.pack(fill="x", pady=(4, 20), ipady=4)

        self.btn_login = tk.Button(
            card,
            text="ĐĂNG NHẬP",
            font=("Segoe UI", 10, "bold"),
            bg=PRIMARY,
            fg="#ffffff",
            activebackground=PRIMARY_HOVER,
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            command=self.handle_login
        )
        self.btn_login.pack(fill="x", ipady=6)
        self.top.bind("<Return>", lambda event: self.handle_login())

    def handle_login(self):
        username = self.ent_user.get().strip()
        password = self.ent_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ tài khoản và mật khẩu!", parent=self.top)
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT username, role FROM users WHERE username = ? AND password = ?", (username, password))
            user = cur.fetchone()
            conn.close()

            if user:
                self.top.destroy()
                self.on_success(user["username"], user["role"])
            else:
                messagebox.showerror("Đăng nhập thất bại", "Tài khoản hoặc mật khẩu không chính xác!", parent=self.top)
                self.ent_pass.delete(0, tk.END)
                self.ent_pass.focus()
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Không thể kết nối cơ sở dữ liệu:\n{e}", parent=self.top)

    def on_close(self):
        self.parent.destroy()
