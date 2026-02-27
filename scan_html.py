lines = open('templates/index.html','r',encoding='utf-8').readlines()
hits = []
for i,l in enumerate(lines,1):
    low = l.lower()
    if any(x in low for x in ['api/games','loadgames','fetchgames','domcontentloaded','onclick','btn-date','date-btn','selecteddate','today']):
        hits.append(f'{i}: {l.rstrip()}')

for h in hits[:60]:
    print(h)
