"""Find classes that match interests, easiest first. Usage: find.py DB "ai,sports,film" [--dept ADV,MKT] [--upper] [--min-n 40]
Searches course titles for each keyword, ranks by A-range %. Check the course schedule after: titles in this DB are past offerings."""
import sqlite3,sys
a=sys.argv[1:];db,kw=a[0],[k.strip().lower() for k in a[1].split(",") if k.strip()]
dept=a[a.index("--dept")+1].split(",") if "--dept" in a else None
minn=int(a[a.index("--min-n")+1]) if "--min-n" in a else 40
n="A+A_Minus+B_Plus+B+B_Minus+C_Plus+C+C_Minus+D_Plus+D+D_Minus+F"
w=" or ".join("lower(Course_Full_Title) like ?" for _ in kw);p=[f"%{k}%" for k in kw]
if dept:w=f"({w}) and trim(Department_Code) in ({','.join('?'*len(dept))})";p+=dept
w=f"({w}) and cast(substr(Course_Number,2,2) as int)<80"  # UT: 2nd-3rd digits 80+ = graduate
if "--upper" in a:w+=" and cast(substr(Course_Number,2,2) as int)>=20"
q=f"""select trim(Department_Code)||' '||Course_Number,max(Course_Title),sum({n}),round(100.0*sum(A+A_Minus)/sum({n}),1),max(Semester)
from grade_distributions where {w} group by 1 having sum({n})>=? order by 4 desc limit 40"""
for r in sqlite3.connect(db).execute(q,p+[minn]):print(f"{r[0]:<10} A-range={r[3]:>5}%  n={r[2]:<6} last={r[4]}  {r[1]}")
