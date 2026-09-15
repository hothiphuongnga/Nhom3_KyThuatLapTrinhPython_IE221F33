import tkinter as tk
import sqlite3
from tkinter import ttk, messagebox

class BooksPage:
    def __init__(self, parent, db, refresh_callback=None):
       
        self.build()

    def build(self):
        top = ttk.Frame(self.parent); top.pack(fill="x", padx=10, pady=10)
        labels = ["Mã sách","Tên sách","Tác giả","Thể loại","NXB","Năm","Số lượng"]
        self.vars = [tk.StringVar() for _ in labels]
        