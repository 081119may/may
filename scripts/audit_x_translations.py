#!/usr/bin/env python3
import base64,gzip,json,pathlib,re,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
m=json.loads((DATA/'manifest.json').read_text('utf-8'))
b64=''.join((ROOT/p).read_text('utf-8').strip() for p in m['archive_parts'])
posts=json.loads(gzip.decompress(base64.b64decode(b64)).decode('utf-8'))
try: manual=json.loads((DATA/'manual-translations.json').read_text('utf-8'))
except Exception: manual={}
try: terms=(json.loads((DATA/'translation-glossary.json').read_text('utf-8')).get('terms') or [])
except Exception: terms=[]
known=[];left=[];alias_hits=[]
proper=collections.defaultdict(lambda:{'count':0,'examples':[]})
# Conservative candidate patterns: kanji compounds, katakana names/titles, hashtags.
pat=re.compile(r'#[^\s#]+|[一-龯々ヶ]{2,10}|[ァ-ヶー]{2,20}|[A-Za-z][A-Za-z0-9!+&._-]{2,30}')
for p in posts:
    tid=str(p.get('id',''));ja=p.get('ja') or '';ko=manual.get(tid) or p.get('ko') or ''
    for t in terms:
        srcs=t.get('ja') or [];target=t.get('ko') or ''
        if any(s and s in ja for s in srcs) and target and target not in ko:
            known.append({'id':tid,'date':p.get('date'),'ja':ja,'ko':ko,'expected':target,'source':srcs})
        for a in t.get('aliases') or []:
            if a and a!=target and a in ko:
                alias_hits.append({'id':tid,'date':p.get('date'),'alias':a,'expected':target,'ja':ja,'ko':ko})
    # Kana in Korean translation is almost always a title/name/hashtag that needs review.
    if re.search(r'[ぁ-んァ-ヶ]',ko):
        left.append({'id':tid,'date':p.get('date'),'ja':ja,'ko':ko})
    seen=set()
    for tok in pat.findall(ja):
        tok=tok.strip('。、！？!?,.「」『』（）()[]【】')
        if len(tok)<2 or tok in seen:continue
        seen.add(tok);d=proper[tok];d['count']+=1
        if len(d['examples'])<3:d['examples'].append({'id':tid,'ja':ja[:300],'ko':ko[:300]})
out={'total':len(posts),'manual_override_count':len(manual),'known_mismatch':known,'known_alias_hits':alias_hits,'japanese_leftovers':left,'proper_tokens':sorted(({'token':k,**v} for k,v in proper.items()),key=lambda x:(-x['count'],x['token']))}
(DATA/'translation-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
print('posts',len(posts),'known mismatch',len(known),'alias hits',len(alias_hits),'kana leftovers',len(left),'tokens',len(proper))
