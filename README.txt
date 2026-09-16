QUAN LY THU VIEN - PHIEN BAN NHOM 5 NGUOI

1. YEU CAU
- Python 3.10+ (khuyen nghi Python 3.12/3.13; Python 3.14 cung co the chay)
- Khong can cai thu vien pip bo sung.
- Khong can server, MySQL hay Internet.

2. CAU TRUC
main.py                 TV5 - file chay chinh
database.py             TV5 - SQLite va khoi tao database
modules/books.py        TV1 - quan ly sach
modules/students.py     TV2 - quan ly sinh vien
modules/loans.py        TV3 - muon/tra sach
modules/statistics.py   TV4 - thong ke + xuat CSV
modules/auth.py         TV5 - dang nhap
utils/helpers.py        Ham dung chung
library.db              Tu dong tao khi chay

3. CHAY CHUONG TRINH
Cach 1: double-click run.bat
Cach 2:
  Mo CMD
  cd /d "duong_dan_den_thu_muc"
  python main.py

4. TAI KHOAN DEMO
admin / 123456
nhanvien / 123456

5. LUU DU LIEU
Du lieu luu trong library.db. Tat chuong trinh khong mat du lieu.
Khong xoa library.db neu muon giu du lieu.

6. NEU MUON RESET DU LIEU DEMO
Dong chuong trinh -> xoa library.db -> chay lai main.py.
