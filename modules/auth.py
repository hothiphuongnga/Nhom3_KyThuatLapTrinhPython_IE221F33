import tkinter as tk
from tkinter import ttk, messagebox

class LoginWindow:
    def __init__(self, root, on_success):
        self.root=root;self.on_success=on_success
        self.win=tk.Toplevel(root);self.win.title("Đăng nhập - Quản lý thư viện");self.win.geometry("380x380");self.win.resizable(False,False)
        self.win.protocol("WM_DELETE_WINDOW",root.destroy)
        f=ttk.Frame(self.win,padding=25);f.pack(fill="both",expand=True)
        ttk.Label(f,text="QUẢN LÝ THƯ VIỆN",font=("Arial",18,"bold")).pack(pady=(5,20))
        self.user=tk.StringVar();self.pw=tk.StringVar()
        ttk.Label(f,text="Tài khoản").pack(anchor="w");ttk.Entry(f,textvariable=self.user).pack(fill="x",pady=5)
        ttk.Label(f,text="Mật khẩu").pack(anchor="w");ttk.Entry(f,textvariable=self.pw,show="*").pack(fill="x",pady=5)
        ttk.Button(f,text="ĐĂNG NHẬP",command=self.login).pack(pady=12)
        ttk.Label(f,text="Demo: admin / 123456").pack()
        self.win.grab_set()

    def login(self):
        conn=self.on_success.__self__.db()
        row=conn.execute("SELECT username,role FROM users WHERE username=? AND password=?",(self.user.get().strip(),self.pw.get())).fetchone()
        conn.close()
        if not row:return messagebox.showerror("Đăng nhập","Sai tài khoản hoặc mật khẩu.")
        self.win.destroy();self.on_success(row["username"],row["role"])
