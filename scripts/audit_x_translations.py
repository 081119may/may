#!/usr/bin/env python3
import base64,gzip,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
m=json.loads((DATA/'manifest.json').read_text('utf-8'))
b64=''.join((ROOT/p).read_text('utf-8').strip() for p in m['archive_parts'])
posts=json.loads(gzip.decompress(base64.b64decode(b64)).decode('utf-8'))
manual=json.loads((DATA/'manual-translations.json').read_text('utf-8'))
terms=(json.loads((DATA/'translation-glossary.json').read_text('utf-8')).get('terms') or [])
issues=[]
for p in posts:
    tid=str(p.get('id',''));ja=p.get('ja') or '';ko=manual.get(tid,'')
    reasons=[]
    for t in terms:
        srcs=t.get('ja') or [];target=t.get('ko') or ''
        if any(s and s in ja for s in srcs) and target and target not in ko:reasons.append('expected '+target)
        for a in t.get('aliases') or []:
            if a and a!=target and a in ko:reasons.append('legacy '+a+' -> '+target)
    if re.search(r'[ぁ-んァ-ヶ]',ko):reasons.append('Japanese kana remains in Korean')
    if ja.strip() and not ko.strip():reasons.append('missing Korean')
    if reasons:issues.append({'id':tid,'date':p.get('date',''),'reasons':sorted(set(reasons)),'ja':ja,'ko':ko})
out={'total':len(posts),'manual_count':len(manual),'issue_count':len(issues),'issues':issues}
(DATA/'translation-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'total':len(posts),'manual_count':len(manual),'issue_count':len(issues)},ensure_ascii=False))
