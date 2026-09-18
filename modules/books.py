import tkinter as tk
import sqlite3
from datetime import date
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
        # Nhân viên chỉ xem sách, admin mới được thay đổi dữ liệu.
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
        ttk.Button(search,text="Ai đang mượn?",command=self.show_borrowers).pack(side="right")
        legend=ttk.Frame(self.parent);legend.pack(fill="x",padx=10,pady=(5,0))
        ttk.Label(legend,text="Chú thích màu:").pack(side="left")
        tk.Label(legend,text="  Sắp hết (còn 1-2 bản)  ",background="#fff3cd").pack(side="left",padx=8)
        tk.Label(legend,text="  Hết sách (còn 0 bản)  ",background="#f8d7da").pack(side="left",padx=8)

        # ID vẫn lưu trong dòng để sửa/xóa đúng sách, trên bảng chỉ hiện STT.
        cols=("id","code","name","author","category","publisher","year","quantity","available","stt")
        self.tree=ttk.Treeview(self.parent,columns=cols,show="headings",
                               displaycolumns=("stt",)+cols[1:-1])
        heads=["ID","Mã","Tên sách","Tác giả","Thể loại","NXB","Năm","Tổng","Số lượng còn","STT"]
        widths=[45,70,180,130,100,110,60,55,100,55]
        self.headings=dict(zip(cols,heads))
        self.sort_column=None
        self.sort_descending=True
        for c,h,w in zip(cols,heads,widths):
            self.tree.heading(c,text=h); self.tree.column(c,width=w,anchor="center")
            if c!="id":self.tree.heading(c,command=lambda column=c:self.sort_by(column))
        self.tree.tag_configure("out_of_stock",background="#f8d7da")
        self.tree.tag_configure("low_stock",background="#fff3cd")
        self.tree.pack(fill="both",expand=True,padx=10,pady=10)
        self.tree.bind("<<TreeviewSelect>>",self.select)
        self.load()

    def load(self):
        # Ghép điều kiện tìm kiếm với bộ lọc tồn kho.
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
        sort_columns={"code":"book_code","name":"name","author":"author",
                      "category":"category","publisher":"publisher","year":"year",
                      "quantity":"quantity","available":"available"}
        if self.sort_column in sort_columns:
            direction="DESC" if self.sort_descending else "ASC"
            query+=f" ORDER BY {sort_columns[self.sort_column]} {direction}, id DESC"
        else:query+=" ORDER BY id DESC"
        conn=self.db(); cur=conn.cursor()
        cur.execute(query,params)
        rows=cur.fetchall(); conn.close()
        self.tree.delete(*self.tree.get_children())
        for stt,r in enumerate(rows,1):
            # Đánh lại STT và tô màu theo số sách còn.
            tag="out_of_stock" if r["available"]==0 else "low_stock" if r["available"]<=2 else ""
            self.tree.insert("", "end", values=tuple(r)+(stt,),tags=(tag,) if tag else ())

    def sort_by(self,column):
        # Bấm lại cùng cột thì đảo chiều sắp xếp.
        if column=="stt":
            self.sort_column=None
            self.sort_descending=True
        elif column==self.sort_column:
            self.sort_descending=not self.sort_descending
        else:
            self.sort_column=column
            self.sort_descending=False
        for key,title in self.headings.items():
            if key=="id":continue
            arrow=" ▼" if self.sort_descending else " ▲"
            self.tree.heading(key,text=title+(arrow if key==self.sort_column else ""))
        self.load()

    def select(self,_=None):
        s=self.tree.selection()
        if not s:return
        v=self.tree.item(s[0],"values")
        for var,val in zip(self.vars,v[1:8]): var.set(val)

    def show_borrowers(self):
        selected=self.tree.selection()
        if not selected:return messagebox.showwarning("Thông báo","Chọn một cuốn sách để xem người đang mượn.")
        book=self.tree.item(selected[0],"values")
        conn=self.db()
        try:
            # Chỉ lấy phiếu đang mượn, không hiện các lượt đã trả.
            borrowers=conn.execute("""SELECT s.student_code,s.name,s.class_name,l.borrow_date,l.due_date
                FROM loans l JOIN students s ON s.id=l.student_id
                WHERE l.book_id=? AND l.status='Đang mượn'
                ORDER BY l.due_date,l.id""",(book[0],)).fetchall()
        finally:
            conn.close()

        window=tk.Toplevel(self.parent)
        window.title(f"Người đang mượn - {book[1]}")
        window.geometry("740x360")
        window.transient(self.parent.winfo_toplevel())
        frame=ttk.Frame(window,padding=15);frame.pack(fill="both",expand=True)
        ttk.Label(frame,text=f"{book[1]} - {book[2]}",font=("Arial",13,"bold")).pack(anchor="w",pady=(0,10))
        ttk.Label(frame,text=f"Đang mượn: {len(borrowers)} bản").pack(anchor="w",pady=(0,10))
        columns=("stt","student_code","name","class_name","borrow_date","due_date","status")
        table=ttk.Treeview(frame,columns=columns,show="headings")
        for column,title,width in zip(columns,
            ("STT","Mã SV","Sinh viên","Lớp","Ngày mượn","Hạn trả","Trạng thái"),
            (45,80,155,90,100,100,100)):
            table.heading(column,text=title);table.column(column,width=width,anchor="center")
        table.pack(fill="both",expand=True)
        today=date.today().isoformat()
        for stt,row in enumerate(borrowers,1):
            status="Quá hạn" if row[4]<today else "Đang mượn"
            table.insert("","end",values=(stt,*row,status))
        ttk.Button(frame,text="Đóng",command=window.destroy).pack(anchor="e",pady=(10,0))
        window.grab_set()

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
            # Giữ nguyên số bản đang được mượn khi admin sửa tổng số sách.
            borrowed=old_qty-old_avail
            if qty<borrowed: raise ValueError
            avail=qty-borrowed
            if not messagebox.askyesno("Xác nhận",f"Bạn có chắc chắn muốn sửa sách {v[2]}?"):
                return
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
