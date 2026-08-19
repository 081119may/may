#!/usr/bin/env python3
import base64,gzip,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
manifest=json.loads((DATA/'manifest.json').read_text('utf-8'))
b64=''.join((ROOT/p).read_text('utf-8').strip() for p in manifest['archive_parts'])
posts=json.loads(gzip.decompress(base64.b64decode(b64)).decode('utf-8'))
try: manual=json.loads((DATA/'manual-translations.json').read_text('utf-8'))
except Exception: manual={}
final={}
missing=[]
for p in posts:
    tid=str(p.get('id',''))
    value=(manual.get(tid) or p.get('ko') or '').strip()
    if value: final[tid]=value
    else: missing.append({'id':tid,'date':p.get('date',''),'ja':p.get('ja','')})
(DATA/'manual-translations.json').write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n','utf-8')
(DATA/'manual-missing.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2)+'\n','utf-8')
print('manual',len(final),'missing',len(missing),'total',len(posts))
