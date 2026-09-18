import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from collections import Counter
try:
    import tkinter.font
except: pass

class StatisticsPage:
    def __init__(self,parent,db):
        self.parent,self.db=parent,db
        self.build()

    def build(self):
        self.cards=ttk.Frame(self.parent);self.cards.pack(fill="x",padx=10,pady=10)
        self.vars=[tk.StringVar(value="0") for _ in range(4)]
        for i,(title,var) in enumerate(zip(["Tổng sách","Tổng sinh viên","Đang mượn","Quá hạn"],self.vars)):
            f=ttk.LabelFrame(self.cards,text=title);f.grid(row=0,column=i,padx=6,sticky="nsew");self.cards.columnconfigure(i,weight=1)
            ttk.Label(f,textvariable=var,font=("Arial",18,"bold")).pack(padx=30,pady=18)
        btn=ttk.Frame(self.parent);btn.pack(fill="x",padx=10)
        ttk.Button(btn,text="Cập nhật thống kê",command=self.load).pack(side="left")
        ttk.Button(btn,text="Xuất CSV",command=self.export_csv).pack(side="left",padx=6)
        self.tree=ttk.Treeview(self.parent,columns=("book","count"),show="headings")
        self.tree.heading("book",text="Sách");self.tree.heading("count",text="Số lượt mượn")
        self.tree.column("book",width=420);self.tree.column("count",width=150,anchor="center")
        self.tree.pack(fill="both",expand=True,padx=10,pady=10)
        self.load()

    def load(self):
        conn=self.db()
        total=conn.execute("SELECT COALESCE(SUM(quantity),0) FROM books").fetchone()[0]
        students=conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        active=conn.execute("SELECT COUNT(*) FROM loans WHERE status='Đang mượn'").fetchone()[0]
        overdue=conn.execute("SELECT COUNT(*) FROM loans WHERE status='Đang mượn' AND due_date < ?",(date.today().isoformat(),)).fetchone()[0]
        self.vars[0].set(str(total));self.vars[1].set(str(students));self.vars[2].set(str(active));self.vars[3].set(str(overdue))
        rows=conn.execute("""SELECT b.name,COUNT(l.id) n FROM loans l JOIN books b ON b.id=l.book_id
                             GROUP BY b.id ORDER BY n DESC,b.name""").fetchall()
        self.tree.delete(*self.tree.get_children())
        for r in rows:self.tree.insert("", "end",values=(r["name"],r["n"]))
        conn.close()

    def export_csv(self):
        import csv
        from tkinter import filedialog
        path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")],initialfile="bao_cao_muon_sach.csv")
        if not path:return
        conn=self.db()
        rows=conn.execute("""SELECT s.student_code,s.name,b.book_code,b.name,l.borrow_date,l.due_date,l.return_date,l.status
                             FROM loans l JOIN students s ON s.id=l.student_id JOIN books b ON b.id=l.book_id
                             ORDER BY l.id DESC""").fetchall()
        conn.close()
        with open(path,"w",newline="",encoding="utf-8-sig") as f:
            w=csv.writer(f);w.writerow(["Mã SV","Sinh viên","Mã sách","Sách","Ngày mượn","Hạn trả","Ngày trả","Trạng thái"])
            w.writerows([tuple(r) for r in rows])
        messagebox.showinfo("Thành công","Đã xuất báo cáo CSV.")
