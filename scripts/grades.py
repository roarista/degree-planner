"""A-range % per instructor from a UT Registration Plus grade_distributions.db. Usage: grades.py DB DEPT NUMBER"""
import sqlite3,sys
db,dept,num=sys.argv[1:4]
n="A+A_Minus+B_Plus+B+B_Minus+C_Plus+C+C_Minus+D_Plus+D+D_Minus+F"
q=f"select upper(trim(Instructor_Last)),sum({n}),round(100.0*sum(A+A_Minus)/sum({n}),1) from grade_distributions where trim(Department_Code)=? and Course_Number=? group by 1 having sum({n})>0 order by 3 desc"
for r in sqlite3.connect(db).execute(q,(dept,num)):print(f"{r[0]:<24} n={r[1]:<6} A-range={r[2]}%")
