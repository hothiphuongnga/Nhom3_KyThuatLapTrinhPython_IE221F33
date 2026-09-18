import tkinter as tk
import sqlite3
from tkinter import ttk, messagebox

class BooksPage:
    def __init__(self, parent, db, refresh_callback=None, role="staff"):
        self.parent, self.db, self.refresh_callback, self.role = parent, db, refresh_callback, role
        self.build()

    def build(self):
        top = ttk.Frame(self.parent); top.pack(fill="x", padx=10, pady=10)
        labels = ["Mã sách","Tên sách","Tác giả","Thể loại","NXB","Năm","Tổng số bản"]
        self.vars = [tk.StringVar() for _ in labels]
        for i,(lab,var) in enumerate(zip(labels,self.vars)):
            ttk.Label(top,text=lab).grid(row=0,column=i,padx=3,sticky="w")
            ttk.Entry(top,textvariable=var,width=16 if i==1 else 12).grid(row=1,column=i,padx=3,pady=3)
        state="normal" if self.role=="admin" else "disabled"
        ttk.Button(top,text="Thêm",command=self.add,state=state).grid(row=1,column=7,padx=4)
        ttk.Button(top,text="Sửa",command=self.edit,state=state).grid(row=1,column=8,padx=4)
        ttk.Button(top,text="Xóa",command=self.delete,state=state).grid(row=1,column=9,padx=4)
        ttk.Button(top,text="Làm mới",command=self.clear).grid(row=1,column=10,padx=4)

        search = ttk.Frame(self.parent); search.pack(fill="x",padx=10)
        self.search_var=tk.StringVar()
        ttk.Label(search,text="Tìm kiếm:").pack(side="left")
        ttk.Entry(search,textvariable=self.search_var,width=30).pack(side="left",padx=5)
        ttk.Button(search,text="Tìm",command=self.load).pack(side="left")
        ttk.Label(search,text="Tồn kho:").pack(side="left",padx=(18,5))
        self.stock_filter=tk.StringVar(value="Tất cả")
        stock=ttk.Combobox(search,textvariable=self.stock_filter,
                           values=("Tất cả","Còn sách","Sắp hết (1-2)","Hết sách"),
                           state="readonly",width=16)
        stock.pack(side="left")
        stock.bind("<<ComboboxSelected>>",lambda _event:self.load())
        legend=ttk.Frame(self.parent);legend.pack(fill="x",padx=10,pady=(5,0))
        ttk.Label(legend,text="Chú thích màu:").pack(side="left")
        tk.Label(legend,text="  Sắp hết (còn 1-2 bản)  ",background="#fff3cd").pack(side="left",padx=8)
        tk.Label(legend,text="  Hết sách (còn 0 bản)  ",background="#f8d7da").pack(side="left",padx=8)

        cols=("id","code","name","author","category","publisher","year","quantity","available")
        self.tree=ttk.Treeview(self.parent,columns=cols,show="headings")
        heads=["ID","Mã","Tên sách","Tác giả","Thể loại","NXB","Năm","Tổng","Số lượng còn"]
        widths=[45,70,180,130,100,110,60,55,100]
        for c,h,w in zip(cols,heads,widths):
            self.tree.heading(c,text=h); self.tree.column(c,width=w,anchor="center")
        self.tree.tag_configure("out_of_stock",background="#f8d7da")
        self.tree.tag_configure("low_stock",background="#fff3cd")
        self.tree.pack(fill="both",expand=True,padx=10,pady=10)
        self.tree.bind("<<TreeviewSelect>>",self.select)
        self.load()

    def load(self):
        q=self.search_var.get().strip()
        conditions=[];params=[]
        if q:
            conditions.append("(book_code LIKE ? OR name LIKE ? OR author LIKE ? OR category LIKE ?)")
            params.extend(f"%{q}%" for _ in range(4))
        stock=self.stock_filter.get()
        if stock=="Còn sách":conditions.append("available > 0")
        elif stock=="Sắp hết (1-2)":conditions.append("available BETWEEN 1 AND 2")
        elif stock=="Hết sách":conditions.append("available = 0")
        query="SELECT * FROM books"
        if conditions:query+=" WHERE "+" AND ".join(conditions)
        query+=" ORDER BY id DESC"
        conn=self.db(); cur=conn.cursor()
        cur.execute(query,params)
        rows=cur.fetchall(); conn.close()
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            tag="out_of_stock" if r["available"]==0 else "low_stock" if r["available"]<=2 else ""
            self.tree.insert("", "end", values=tuple(r),tags=(tag,) if tag else ())

    def select(self,_=None):
        s=self.tree.selection()
        if not s:return
        v=self.tree.item(s[0],"values")
        for var,val in zip(self.vars,v[1:8]): var.set(val)

    def add(self):
        if self.role!="admin":return messagebox.showerror("Không có quyền","Chỉ admin được thêm sách.")
        try:
            code,name,author,cat,pub,year,qty=[v.get().strip() for v in self.vars]
            year=int(year) if year else None; qty=int(qty)
            if not code or not name or qty<0: raise ValueError
            conn=self.db(); conn.execute("""INSERT INTO books
                (book_code,name,author,category,publisher,year,quantity,available)
                VALUES (?,?,?,?,?,?,?,?)""",(code,name,author,cat,pub,year,qty,qty))
            conn.commit(); conn.close(); self.clear(); self.load()
            if self.refresh_callback:self.refresh_callback()
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi","Mã sách đã tồn tại.")
        except Exception: messagebox.showerror("Lỗi","Kiểm tra dữ liệu nhập.")

    def edit(self):
        if self.role!="admin":return messagebox.showerror("Không có quyền","Chỉ admin được sửa sách.")
        s=self.tree.selection()
        if not s:return messagebox.showwarning("Thông báo","Chọn sách cần sửa.")
        v=self.tree.item(s[0],"values"); code,name,author,cat,pub,year,qty=[x.get().strip() for x in self.vars]
        try:
            year=int(year) if year else None; qty=int(qty)
            old_qty=int(v[7]); old_avail=int(v[8])
            borrowed=old_qty-old_avail
            if qty<borrowed: raise ValueError
            avail=qty-borrowed
            conn=self.db(); conn.execute("""UPDATE books SET book_code=?,name=?,author=?,category=?,
                publisher=?,year=?,quantity=?,available=? WHERE id=?""",
                (code,name,author,cat,pub,year,qty,avail,v[0]))
            conn.commit();conn.close();self.clear();self.load()
            if self.refresh_callback:self.refresh_callback()
        except Exception: messagebox.showerror("Lỗi","Dữ liệu không hợp lệ hoặc số lượng mới nhỏ hơn số đang mượn.")

    def delete(self):
        if self.role!="admin":return messagebox.showerror("Không có quyền","Chỉ admin được xóa sách.")
        s=self.tree.selection()
        if not s:return
        v=self.tree.item(s[0],"values")
        if int(v[8])!=int(v[7]): return messagebox.showerror("Lỗi","Không thể xóa sách đang được mượn.")
        if messagebox.askyesno("Xác nhận","Xóa sách này?"):
            conn=self.db()
            try:
                conn.execute("DELETE FROM books WHERE id=?",(v[0],));conn.commit()
            except Exception: messagebox.showerror("Lỗi","Sách đã có lịch sử mượn, không thể xóa.")
            conn.close();self.load();self.clear()

    def clear(self):
        for v in self.vars:v.set("")
