"""RateMyProfessors lookup (public GraphQL). Usage: rmp.py "Last name" [schoolID]. Default school = UT Austin."""
import json,sys,urllib.request
name=sys.argv[1];school=sys.argv[2] if len(sys.argv)>2 else "U2Nob29sLTEyNTU="
q={"query":"query($t:TeacherSearchQuery!){newSearch{teachers(query:$t,first:10){edges{node{firstName lastName department avgRating avgDifficulty numRatings wouldTakeAgainPercent}}}}}","variables":{"t":{"text":name,"schoolID":school}}}
r=urllib.request.Request("https://www.ratemyprofessors.com/graphql",json.dumps(q).encode(),{"Authorization":"Basic dGVzdDp0ZXN0","Content-Type":"application/json","User-Agent":"Mozilla/5.0"})
for e in json.load(urllib.request.urlopen(r))["data"]["newSearch"]["teachers"]["edges"]:
    t=e["node"];print(f'{t["firstName"]} {t["lastName"].strip()} ({t["department"]}): quality {t["avgRating"]}, difficulty {t["avgDifficulty"]}, n={t["numRatings"]}, again {round(t["wouldTakeAgainPercent"])}%')
