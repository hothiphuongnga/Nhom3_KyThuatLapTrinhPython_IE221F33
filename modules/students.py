import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class StudentsPage:
    def __init__(self,parent,db,refresh_callback=None):
        self.parent,self.db,self.refresh_callback=parent,db,refresh_callback
        self.build()

    def build(self):
        form=ttk.Frame(self.parent);form.pack(fill="x",padx=10,pady=10)
        labels=["Mã SV","Họ tên","Lớp","SĐT","Email"]
        self.vars=[tk.StringVar() for _ in labels]
        for i,(lab,var) in enumerate(zip(labels,self.vars)):
            ttk.Label(form,text=lab).grid(row=0,column=i,padx=4,sticky="w")
            ttk.Entry(form,textvariable=var,width=24 if i in (1,4) else 14).grid(row=1,column=i,padx=4)
        for i,(t,cmd) in enumerate([("Thêm",self.add),("Sửa",self.edit),("Xóa",self.delete),("Làm mới",self.clear)]):
            ttk.Button(form,text=t,command=cmd).grid(row=1,column=5+i,padx=4)

        s=ttk.Frame(self.parent);s.pack(fill="x",padx=10)
        self.search=tk.StringVar();ttk.Label(s,text="Tìm kiếm:").pack(side="left")
        ttk.Entry(s,textvariable=self.search,width=30).pack(side="left",padx=5)
        ttk.Button(s,text="Tìm",command=self.load).pack(side="left")

        cols=("id","code","name","class","phone","email")
        self.tree=ttk.Treeview(self.parent,columns=cols,show="headings")
        for c,h,w in zip(cols,["ID","Mã SV","Họ tên","Lớp","SĐT","Email"],[45,80,180,100,120,220]):
            self.tree.heading(c,text=h);self.tree.column(c,width=w,anchor="center")
        self.tree.pack(fill="both",expand=True,padx=10,pady=10);self.tree.bind("<<TreeviewSelect>>",self.select)
        self.load()

    def load(self):
        q=self.search.get().strip();conn=self.db()
        if q: rows=conn.execute("""SELECT * FROM students WHERE student_code LIKE ? OR name LIKE ? OR class_name LIKE ?""",(f"%{q}%",)*3).fetchall()
        else: rows=conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
        self.tree.delete(*self.tree.get_children())
        for r in rows:self.tree.insert("", "end",values=tuple(r))
        conn.close()

    def select(self,_=None):
        s=self.tree.selection()
        if s:
            v=self.tree.item(s[0],"values")
            for var,val in zip(self.vars,v[1:]):var.set(val)

    def add(self):
        vals=[v.get().strip() for v in self.vars]
        if not vals[0] or not vals[1]:return messagebox.showwarning("Thiếu dữ liệu","Nhập Mã SV và Họ tên.")
        conn=self.db()
        try:conn.execute("INSERT INTO students(student_code,name,class_name,phone,email) VALUES(?,?,?,?,?)",vals);conn.commit()
        except sqlite3.IntegrityError:return messagebox.showerror("Lỗi","Mã sinh viên đã tồn tại.")
        finally:conn.close()
        self.clear();self.load()
        if self.refresh_callback:self.refresh_callback()

    def edit(self):
        s=self.tree.selection()
        if not s:return messagebox.showwarning("Thông báo","Chọn sinh viên.")
        v=self.tree.item(s[0],"values");vals=[x.get().strip() for x in self.vars]
        conn=self.db();conn.execute("""UPDATE students SET student_code=?,name=?,class_name=?,phone=?,email=? WHERE id=?""",(*vals,v[0]));conn.commit();conn.close()
        self.clear();self.load();self.refresh_callback and self.refresh_callback()

    def delete(self):
        s=self.tree.selection()
        if not s:return
        v=self.tree.item(s[0],"values")
        if messagebox.askyesno("Xác nhận","Xóa sinh viên này?"):
            conn=self.db()
            try:conn.execute("DELETE FROM students WHERE id=?",(v[0],));conn.commit()
            except sqlite3.IntegrityError:messagebox.showerror("Lỗi","Sinh viên đã có lịch sử mượn, không thể xóa.")
            conn.close();self.load();self.clear()

    def clear(self):
        for v in self.vars:v.set("")
