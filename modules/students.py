import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk


class StudentsPage:
    """Lớp quản lý trang sinh viên sử dụng Tkinter và SQLite3."""

    def __init__(self, parent, db, refresh_callback=None):
        self._parent = parent
        self._db = db
        self._refresh_callback = refresh_callback

        self._vars = []
        self._search_var = None
        self._tree = None

        self._build_ui()

    def _build_ui(self):
        self._build_form_section()
        self._build_search_section()
        self._build_treeview_section()

    def _build_form_section(self):
        form_frame = ttk.Frame(self._parent)
        form_frame.pack(fill="x", padx=10, pady=10)

        labels = ["Mã SV", "Họ tên", "Lớp", "SĐT", "Email"]
        self._vars = [tk.StringVar() for _ in labels]

        for i, (label_text, var) in enumerate(zip(labels, self._vars)):
            ttk.Label(form_frame, text=label_text).grid(
                row=0, column=i, padx=4, sticky="w"
            )
            entry_width = 24 if i in (1, 4) else 14
            ttk.Entry(form_frame, textvariable=var, width=entry_width).grid(
                row=1, column=i, padx=4
            )

        actions = [
            ("Thêm", None),
            ("Sửa", None),
            ("Xóa", None),
            ("Làm mới", None),
        ]
        for i, (text, command) in enumerate(actions):
            ttk.Button(form_frame, text=text, command=command).grid(
                row=1, column=5 + i, padx=4
            )

    def _build_search_section(self):
        search_frame = ttk.Frame(self._parent)
        search_frame.pack(fill="x", padx=10)

        self._search_var = tk.StringVar()
        ttk.Label(search_frame, text="Tìm kiếm:").pack(side="left")
        ttk.Entry(search_frame, textvariable=self._search_var, width=30).pack(
            side="left", padx=5
        )
        ttk.Button(search_frame, text="Tìm").pack(side="left")

    def _build_treeview_section(self):
        columns = ("id", "code", "name", "class", "phone", "email")
        headers = ["ID", "Mã SV", "Họ tên", "Lớp", "SĐT", "Email"]
        widths = [45, 80, 180, 100, 120, 220]

        self._tree = ttk.Treeview(
            self._parent, columns=columns, show="headings"
        )
        for col, head, width in zip(columns, headers, widths):
            self._tree.heading(col, text=head)
            self._tree.column(col, width=width, anchor="center")

        self._tree.pack(fill="both", expand=True, padx=10, pady=10)