#!/usr/bin/env python3
import base64,gzip,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
manifest=json.loads((DATA/'manifest.json').read_text('utf-8'))
b64=''.join((ROOT/p).read_text('utf-8').strip() for p in manifest['archive_parts'])
posts=json.loads(gzip.decompress(base64.b64decode(b64)).decode('utf-8'))
try: manual=json.loads((DATA/'manual-translations.json').read_text('utf-8'))
except Exception: manual={}
terms=(json.loads((DATA/'translation-glossary.json').read_text('utf-8')).get('terms') or [])
terms=sorted(terms,key=lambda x:max([len(s) for s in x.get('ja',[])]+[0]),reverse=True)

def normalize(ja,ko):
    for term in terms:
        srcs=term.get('ja') or [];target=term.get('ko') or ''
        if not target or not any(s and s in ja for s in srcs):continue
        for alias in sorted(set(term.get('aliases') or []),key=len,reverse=True):
            if alias and alias!=target:ko=ko.replace(alias,target)
        for src in sorted(srcs,key=len,reverse=True):
            if src and src!=target:ko=ko.replace(src,target)
    return ko

final={};missing=[];changed=0
for p in posts:
    tid=str(p.get('id',''));ja=p.get('ja') or ''
    value=(manual.get(tid) or p.get('ko') or '').strip()
    if value:
        fixed=normalize(ja,value).strip();changed+=fixed!=value;final[tid]=fixed
    elif ja.strip():missing.append({'id':tid,'date':p.get('date',''),'ja':ja})
(DATA/'manual-translations.json').write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n','utf-8')
(DATA/'manual-missing.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2)+'\n','utf-8')
print('manual',len(final),'missing text posts',len(missing),'canonical fixes',changed,'total',len(posts))
