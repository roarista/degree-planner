"""Export plan.json to other formats. Usage: export.py plan.json md|docx|pptx|csv [out]
md   : no deps. Paste into Google Docs / Notion.
docx : pip install python-docx  -> upload to Google Drive, "Open with Google Docs".
pptx : pip install python-pptx  -> one slide per semester; upload to Drive for Google Slides.
csv  : no deps. Import into Google Sheets / Excel."""
import json,sys,csv
src,fmt=sys.argv[1],sys.argv[2];out=sys.argv[3] if len(sys.argv)>3 else src.rsplit(".",1)[0]+"."+fmt
P=json.load(open(src));C=P["classes"];T=[t for t in P["terms"] if not t.get("pool")]
def rows(t):return [(C[i]["code"],C[i]["name"],C[i]["hours"],C[i].get("diff","?"),C[i].get("note","")) for i in t["classes"]]
hrs=lambda t:sum(r[2] for r in rows(t))
if fmt=="md":
    L=[f"# {P.get('title','Plan')}",P.get("student",""),""]
    for t in T:L+=[f"## {t['term']} ({hrs(t)} hrs)","| Class | Name | Hrs | Difficulty | Note |","|---|---|---|---|---|"]+[f"| {a} | {b} | {c} | {d} | {e} |" for a,b,c,d,e in rows(t)]+[""]
    open(out,"w").write("\n".join(L))
elif fmt=="csv":
    w=csv.writer(open(out,"w",newline=""));w.writerow(["Term","Class","Name","Hours","Difficulty","Note"])
    for t in T:[w.writerow([t["term"],*r]) for r in rows(t)]
elif fmt=="docx":
    import docx;d=docx.Document();d.add_heading(P.get("title","Plan"),0);d.add_paragraph(P.get("student",""))
    for t in T:
        d.add_heading(f"{t['term']} ({hrs(t)} hrs)",1);tb=d.add_table(rows=1,cols=5);tb.style="Light Grid Accent 2"
        for c,h in zip(tb.rows[0].cells,["Class","Name","Hrs","Difficulty","Note"]):c.text=h
        for r in rows(t):[setattr(c,"text",str(v)) for c,v in zip(tb.add_row().cells,r)]
    d.save(out)
elif fmt=="pptx":
    from pptx import Presentation;from pptx.util import Inches,Pt
    pr=Presentation();s=pr.slides.add_slide(pr.slide_layouts[0]);s.shapes.title.text=P.get("title","Plan");s.placeholders[1].text=P.get("student","")
    for t in T:
        s=pr.slides.add_slide(pr.slide_layouts[5]);s.shapes.title.text=f"{t['term']} · {hrs(t)} hrs";R=rows(t)
        tb=s.shapes.add_table(len(R)+1,4,Inches(.5),Inches(1.6),Inches(9),Inches(.4*(len(R)+1))).table
        for j,h in enumerate(["Class","Name","Hrs","Difficulty"]):tb.cell(0,j).text=h
        for i,r in enumerate(R,1):
            for j,v in enumerate(r[:4]):tb.cell(i,j).text=str(v);tb.cell(i,j).text_frame.paragraphs[0].font.size=Pt(14)
    pr.save(out)
else:sys.exit("format: md|docx|pptx|csv")
print(out)
