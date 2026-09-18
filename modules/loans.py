import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta, datetime

class LoansPage:
    def __init__(self,parent,db,refresh_callback=None):
        self.parent,self.db,self.refresh_callback=parent,db,refresh_callback
        self.build()

    def build(self):
        form=ttk.LabelFrame(self.parent,text="Lập phiếu mượn");form.pack(fill="x",padx=10,pady=8)
        self.student=ttk.Combobox(form,width=28,state="readonly")
        self.book=ttk.Combobox(form,width=38,state="readonly")
        self.days=tk.StringVar(value="14")
        ttk.Label(form,text="Sinh viên").grid(row=0,column=0,padx=5,pady=5)
        self.student.grid(row=0,column=1,padx=5)
        ttk.Label(form,text="Sách").grid(row=0,column=2,padx=5)
        self.book.grid(row=0,column=3,padx=5)
        ttk.Label(form,text="Số ngày").grid(row=0,column=4,padx=5)
        ttk.Entry(form,textvariable=self.days,width=8).grid(row=0,column=5,padx=5)
        ttk.Button(form,text="Mượn sách",command=self.borrow).grid(row=0,column=6,padx=8)
        ttk.Button(form,text="Làm mới",command=self.load).grid(row=0,column=7,padx=8)

        cols=("id","student","book","borrow","due","return","status")
        self.tree=ttk.Treeview(self.parent,columns=cols,show="headings")
        for c,h,w in zip(cols,["ID","Sinh viên","Sách","Ngày mượn","Hạn trả","Ngày trả","Trạng thái"],[45,160,210,100,100,100,110]):
            self.tree.heading(c,text=h);self.tree.column(c,width=w,anchor="center")
        self.tree.pack(fill="both",expand=True,padx=10,pady=8)
        self.tree.bind("<Double-1>",lambda e:self.return_book())
        self.load()

    def load(self):
        conn=self.db()
        ss=conn.execute("SELECT id,student_code,name FROM students ORDER BY student_code").fetchall()
        bs=conn.execute("SELECT id,book_code,name,available FROM books ORDER BY book_code").fetchall()
        self.smap={f"{r['student_code']} - {r['name']}":r['id'] for r in ss}
        self.bmap={f"{r['book_code']} - {r['name']} (còn {r['available']})":r['id'] for r in bs if r['available']>0}
        self.student["values"]=list(self.smap);self.book["values"]=list(self.bmap)
        rows=conn.execute("""SELECT l.id,s.student_code||' - '||s.name student,b.book_code||' - '||b.name book,
          l.borrow_date,l.due_date,COALESCE(l.return_date,''),l.status
          FROM loans l JOIN students s ON s.id=l.student_id JOIN books b ON b.id=l.book_id ORDER BY l.id DESC""").fetchall()
        self.tree.delete(*self.tree.get_children())
        today=date.today()
        for r in rows:
            vals=list(r)
            if vals[6]=="Đang mượn" and datetime.strptime(vals[4],"%Y-%m-%d").date()<today: vals[6]="QUÁ HẠN"
            self.tree.insert("", "end",values=vals)
        conn.close()

    def borrow(self):
        if self.student.get() not in self.smap or self.book.get() not in self.bmap:return messagebox.showwarning("Thiếu dữ liệu","Chọn sinh viên và sách.")
        try:days=int(self.days.get()); assert 1<=days<=365
        except: return messagebox.showerror("Lỗi","Số ngày phải từ 1 đến 365.")
        sid=self.smap[self.student.get()];bid=self.bmap[self.book.get()]
        conn=self.db()
        row=conn.execute("SELECT available FROM books WHERE id=?",(bid,)).fetchone()
        if not row or row["available"]<=0:return messagebox.showerror("Lỗi","Sách đã hết.")
        d=date.today();due=d+timedelta(days=days)
        conn.execute("INSERT INTO loans(student_id,book_id,borrow_date,due_date,status) VALUES(?,?,?,?,?)",
                     (sid,bid,d.isoformat(),due.isoformat(),"Đang mượn"))
        conn.execute("UPDATE books SET available=available-1 WHERE id=?",(bid,))
        conn.commit();conn.close();messagebox.showinfo("Thành công",f"Mượn sách thành công.\nHạn trả: {due.strftime('%d/%m/%Y')}")
        self.load();self.refresh_callback and self.refresh_callback()

    def return_book(self):
        s=self.tree.selection()
        if not s:return messagebox.showwarning("Thông báo","Chọn phiếu mượn cần trả.")
        v=self.tree.item(s[0],"values")
        if v[6]!="Đang mượn" and v[6]!="QUÁ HẠN":return messagebox.showinfo("Thông báo","Sách này đã được trả.")
        if not messagebox.askyesno("Xác nhận",f"Xác nhận trả sách của {v[1]}?"):return
        conn=self.db();today=date.today().isoformat()
        row=conn.execute("SELECT book_id FROM loans WHERE id=?",(v[0],)).fetchone()
        conn.execute("UPDATE loans SET return_date=?,status='Đã trả' WHERE id=?",(today,v[0]))
        conn.execute("UPDATE books SET available=available+1 WHERE id=?",(row["book_id"],))
        conn.commit();conn.close();self.load();self.refresh_callback and self.refresh_callback()
