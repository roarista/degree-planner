"""How hard is THIS class with THIS professor, for THIS student? (1 = easy, 10 = hard)
Usage: difficulty.py DB DEPT NUM "Prof Last" [--profile me.json] [--info class.json] [--json]

Signals (each missing one is skipped and the weights renormalize):
  G  grades   A, A-, full distribution -> GPA, for this prof in this course (shrunk toward the course-wide
              numbers when the sample is small), plus the prof across all their courses.
  R  RMP      difficulty from reviews of THIS course (e.g. "ECO330T") vs. all the prof's reviews,
              weighted by how many class-specific reviews exist.
  F  format   what reviews say: test-heavy, Honorlock/lockdown, in-person vs Canvas exams, async,
              assignment-heavy, group projects, attendance, reading, papers, curve, extra credit.
              --info adds facts from the course schedule/syllabus: {"mode":"online|in person|hybrid",
              "days":"MWF","time":"8:00","exams":3,"exam_weight":0.6,"exam_where":"in person|canvas|honorlock"}
  P  personal --profile: {"tests":"strong|average|weak","likes":["papers","group"],"dislikes":["8am","attendance"]}
Formula: base = 0.55*G + 0.45*R (0-10 scale each), then + format/personal adjustments, clipped to 1-10."""
import sqlite3,sys,json,re,urllib.request
a=sys.argv[1:];db,dept,num,prof=a[:4]
opt=lambda k:a[a.index(k)+1] if k in a else None
profile=json.load(open(opt("--profile"))) if opt("--profile") else {}
info=json.load(open(opt("--info"))) if opt("--info") else {}
W={"A":4,"A_Minus":3.67,"B_Plus":3.33,"B":3,"B_Minus":2.67,"C_Plus":2.33,"C":2,"C_Minus":1.67,"D_Plus":1.33,"D":1,"D_Minus":.67,"F":0}
con=sqlite3.connect(db)
def dist(where,p):
    r=con.execute(f"select {','.join(f'sum({k})' for k in W)} from grade_distributions where {where}",p).fetchone()
    n=sum(x or 0 for x in r)
    if not n:return None
    d=dict(zip(W,[x or 0 for x in r]));return {"n":n,"A%":round(100*d["A"]/n,1),"A-%":round(100*d["A_Minus"]/n,1),
        "A-range%":round(100*(d["A"]+d["A_Minus"])/n,1),"GPA":round(sum(W[k]*d[k] for k in W)/n,2),"F/D%":round(100*(d["F"]+d["D"]+d["D_Minus"]+d["D_Plus"])/n,1)}
pl=prof.strip().upper()
this=dist("trim(Department_Code)=? and Course_Number=? and upper(trim(Instructor_Last))=?",(dept,num,pl))
course=dist("trim(Department_Code)=? and Course_Number=?",(dept,num))
profall=dist("upper(trim(Instructor_Last))=? and trim(Department_Code)=?",(pl,dept))
def gscore(d):  # 0 easy .. 10 hard, from A-range% and GPA
    return None if not d else max(0,min(10,.5*10*(1-d["A-range%"]/100)+.5*10*(1-(d["GPA"]-1.5)/2.5)))
G=None
if this or course:
    gs,gc=gscore(this),gscore(course)
    if gs is None:G=gc
    else:w=this["n"]/(this["n"]+50);G=w*gs+(1-w)*(gc if gc is not None else gs)
def gql(q,v):
    r=urllib.request.Request("https://www.ratemyprofessors.com/graphql",json.dumps({"query":q,"variables":v}).encode(),
        {"Authorization":"Basic dGVzdDp0ZXN0","Content-Type":"application/json","User-Agent":"Mozilla/5.0"})
    return json.load(urllib.request.urlopen(r,timeout=25))["data"]
rmp=None;revs=[]
try:
    q="""query($t:TeacherSearchQuery!){newSearch{teachers(query:$t,first:10){edges{node{firstName lastName department avgRating avgDifficulty numRatings wouldTakeAgainPercent
    ratings(first:200){edges{node{class grade date difficultyRating helpfulRating wouldTakeAgain attendanceMandatory isForOnlineClass textbookUse comment ratingTags}}}}}}}}"""
    E=[e["node"] for e in gql(q,{"t":{"text":prof,"schoolID":opt("--school") or "U2Nob29sLTEyNTU="}})["newSearch"]["teachers"]["edges"] if e["node"]["lastName"].strip().upper()==pl]
    if E:rmp=max(E,key=lambda t:t["numRatings"]);revs=[r["node"] for r in rmp["ratings"]["edges"]]
except Exception as ex:print("RMP lookup failed:",ex,file=sys.stderr)
code=re.sub(r"\s","",dept+num).upper()
mine=[r for r in revs if re.sub(r"[\s-]","",r["class"] or "").upper()==code]
R=None;rc=ra=None
if rmp:
    ra=rmp["avgDifficulty"];rc=round(sum(r["difficultyRating"] for r in mine)/len(mine),2) if mine else None
    k=len(mine)/(len(mine)+5);d=(k*rc+(1-k)*ra) if rc is not None else ra
    R=(d-1)*2.5 if d else None
FEAT={"test-heavy":r"\b(exams?|tests?|midterms?|finals?)\b.*\b(hard|heavy|most of (the|your) grade|all that matters|brutal)|test.heavy|exam.heavy",
 "honorlock/lockdown":r"honorlock|lockdown|proctor",
 "exams on canvas/online":r"(exams?|tests?|quizz?es) (are|were)? ?(on|through) canvas|online (exams?|tests?)|open.note|open.book",
 "exams in person":r"in.person (exams?|tests?)|paper (exams?|tests?)",
 "async/online":r"asynch|self.paced|online class|recorded lectures?",
 "assignment-heavy":r"(lots of|so much|tons of|heavy) (home)?work|busy ?work|assignment.heavy|weekly (assignments|homework|quizzes)",
 "group projects":r"group (projects?|work)",
 "attendance matters":r"attendance|pop quiz|in.class (quizzes|participation)|iclicker|instapoll",
 "reading-heavy":r"(lots of|heavy|a lot of) reading|readings? (are|is) (long|heavy)",
 "papers/writing":r"\b(papers?|essays?|writing assignments?)\b",
 "curve":r"\bcurve[sd]?\b",
 "extra credit":r"extra credit",
 "tough grader":r"tough grader|harsh(ly)? grad|picky"}
txt=[(r["comment"] or "")+" "+(r.get("ratingTags") or "") for r in (mine or revs)]
feat={k:round(sum(bool(re.search(p,t,re.I)) for t in txt)/len(txt),2) for k,p in FEAT.items()} if txt else {}
adj=[];add=lambda v,why:adj.append((round(v,2),why))
if feat:
    if feat["tough grader"]>.15:add(.75,"reviews: tough grader")
    if feat["curve"]>.15:add(-.4,"reviews: curves")
    if feat["extra credit"]>.15:add(-.4,"reviews: extra credit")
    if feat["assignment-heavy"]>.2:add(.5,"reviews: assignment-heavy")
    if feat["honorlock/lockdown"]>.1:add(.4,"reviews: proctored exams")
tests={"weak":1.5,"average":0,"strong":-1}.get(profile.get("tests","average"),0)
th=max(feat.get("test-heavy",0)*2,info.get("exam_weight",0))
if tests and th:add(tests*min(1,th),f"you are {profile['tests']} at tests; class is test-weighted ({th:.0%})")
FMAP={"group":"group projects","papers":"papers/writing","reading":"reading-heavy","attendance":"attendance matters","tests":"test-heavy","online":"async/online","busywork":"assignment-heavy"}
for k in profile.get("dislikes",[]):
    if FMAP.get(k) and feat.get(FMAP[k],0)>.15:add(.75,f"you dislike {k}; reviews mention it")
    if k=="8am" and str(info.get("time","")).startswith(("8:","8 ")):add(.75,"you dislike 8 AM classes")
    if k=="friday" and "F" in info.get("days",""):add(.4,"meets Fridays")
for k in profile.get("likes",[]):
    if FMAP.get(k) and feat.get(FMAP[k],0)>.15:add(-.5,f"you like {k}; reviews mention it")
parts=[(G,.55),(R,.45)];have=[(v,w) for v,w in parts if v is not None]
base=sum(v*w for v,w in have)/sum(w for _,w in have) if have else None
score=None if base is None else round(max(1,min(10,base+sum(v for v,_ in adj))),1)
out={"class":f"{dept} {num}","prof":prof,"score_1_10":score,"grades_this_prof_course":this,"grades_course_all_profs":course,"grades_prof_all_dept":profall,
 "rmp":None if not rmp else {"name":f"{rmp['firstName']} {rmp['lastName'].strip()}","quality":rmp["avgRating"],"difficulty_all_classes":ra,
   "difficulty_this_class":rc,"reviews_this_class":len(mine),"reviews_total":rmp["numRatings"],"would_take_again%":rmp["wouldTakeAgainPercent"]},
 "review_signals":feat,"info":info,"adjustments":adj,"G_0_10":None if G is None else round(G,2),"R_0_10":None if R is None else round(R,2),
 "sample_reviews_this_class":[(r["date"][:10],r["grade"],r["comment"][:240]) for r in mine[:5]]}
if "--json" in a:print(json.dumps(out,indent=1));sys.exit()
print(f"{dept} {num} with {prof}: difficulty {score if score is not None else '?'}/10")
for k,v in [("this prof, this course",this),("course, all profs",course),(f"{prof}, all {dept} courses",profall)]:
    print(f"  grades {k}: "+(f"A {v['A%']}% · A- {v['A-%']}% · GPA {v['GPA']} · D/F {v['F/D%']}% · n={v['n']}" if v else "?"))
if rmp:print(f"  RMP difficulty: this class {rc if rc is not None else '?'} ({len(mine)} reviews) · all classes {ra} ({rmp['numRatings']}) · quality {rmp['avgRating']}")
else:print("  RMP: ?")
if feat:print("  reviews mention: "+", ".join(f"{k} {v:.0%}" for k,v in feat.items() if v>=.1) or "nothing notable")
for v,w in adj:print(f"  {v:+} {w}")
