from datetime import date, datetime

def vn_date(iso_date):
    try:return datetime.strptime(iso_date,"%Y-%m-%d").strftime("%d/%m/%Y")
    except:return iso_date
