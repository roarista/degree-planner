"""RateMyProfessors lookup (public GraphQL). Usage: rmp.py "Last name" [--reviews N] [--school ID]
Prints rating, difficulty, would-take-again, top tags, and the N newest reviews (class, grade, comment). Default school = UT Austin."""
import json,sys,urllib.request
a=sys.argv[1:];name=a[0];n=int(a[a.index("--reviews")+1]) if "--reviews" in a else 5
school=a[a.index("--school")+1] if "--school" in a else "U2Nob29sLTEyNTU="
def gql(q,v):
    r=urllib.request.Request("https://www.ratemyprofessors.com/graphql",json.dumps({"query":q,"variables":v}).encode(),
        {"Authorization":"Basic dGVzdDp0ZXN0","Content-Type":"application/json","User-Agent":"Mozilla/5.0"})
    return json.load(urllib.request.urlopen(r,timeout=20))["data"]
q="""query($t:TeacherSearchQuery!,$n:Int){newSearch{teachers(query:$t,first:10){edges{node{firstName lastName department
avgRating avgDifficulty numRatings wouldTakeAgainPercent teacherRatingTags{tagName tagCount}
ratings(first:$n){edges{node{class grade date difficultyRating helpfulRating wouldTakeAgain comment}}}}}}}}"""
for e in gql(q,{"t":{"text":name,"schoolID":school},"n":n})["newSearch"]["teachers"]["edges"]:
    t=e["node"];wta=t["wouldTakeAgainPercent"]
    print(f"\n{t['firstName']} {t['lastName'].strip()} · {t['department']} · quality {t['avgRating']} · difficulty {t['avgDifficulty']} · {t['numRatings']} ratings · would take again {round(wta) if wta and wta>=0 else '?'}%")
    tags=sorted(t["teacherRatingTags"] or [],key=lambda x:-x["tagCount"])[:5]
    if tags:print("  tags: "+", ".join(f"{x['tagName']} ({x['tagCount']})" for x in tags))
    for r in t["ratings"]["edges"]:
        r=r["node"];print(f"  - {r['date'][:10]} {r['class']} grade={r['grade'] or '?'} diff={r['difficultyRating']} quality={r['helpfulRating']}: {(r['comment'] or '').strip()[:300]}")
