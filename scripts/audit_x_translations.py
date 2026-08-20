#!/usr/bin/env python3
import base64,gzip,json,pathlib,re,collections
ROOT=pathlib.Path(__file__).resolve().parents[1];DATA=ROOT/'data'
m=json.loads((DATA/'manifest.json').read_text('utf-8'));b64=''.join((ROOT/p).read_text('utf-8').strip() for p in m['archive_parts'])
posts=json.loads(gzip.decompress(base64.b64decode(b64)).decode('utf-8'));manual=json.loads((DATA/'manual-translations.json').read_text('utf-8'))
terms=(json.loads((DATA/'translation-glossary.json').read_text('utf-8')).get('terms') or [])
counts=collections.defaultdict(lambda:{'count':0,'ids':[]});known=[];missing=[]
for p in posts:
    tid=str(p.get('id',''));ja=p.get('ja') or '';ko=manual.get(tid,'')
    if ja.strip() and not ko.strip():missing.append({'id':tid,'ja':ja})
    clean=re.sub(r'https?://\S+','',ko)
    for tok in re.findall(r'#[^\s#]*[ぁ-んァ-ヶ一-龯々][^\s#]*|[ぁ-んァ-ヶー]{2,}|[一-龯々]{2,}',clean):
        d=counts[tok];d['count']+=1
        if tid not in d['ids'] and len(d['ids'])<8:d['ids'].append(tid)
    for t in terms:
        srcs=t.get('ja') or [];target=t.get('ko') or ''
        if any(s and s in ja for s in srcs) and target and target not in ko:
            known.append({'id':tid,'expected':target,'ja':ja,'ko':ko})
out={'total':len(posts),'manual_count':len(manual),'missing':missing,'known_mismatch':known,'leftover_tokens':sorted(({'token':k,**v} for k,v in counts.items()),key=lambda x:(-x['count'],x['token']))}
(DATA/'translation-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
print('manual',len(manual),'missing',len(missing),'known',len(known),'tokens',len(counts))
