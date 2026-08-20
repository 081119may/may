#!/usr/bin/env python3
import base64,gzip,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1];DATA=ROOT/'data'
m=json.loads((DATA/'manifest.json').read_text('utf-8'))
b64=''.join((ROOT/p).read_text('utf-8').strip() for p in m['archive_parts'])
posts=json.loads(gzip.decompress(base64.b64decode(b64)).decode('utf-8'))
manual=json.loads((DATA/'manual-translations.json').read_text('utf-8'))
changed=0
for p in posts:
    tid=str(p.get('id',''));ja=p.get('ja') or '';ko=manual.get(tid,'')
    if not ko or '#デートウォーズ' not in ja:continue
    both='#DATEWARS' in ja
    old=ko
    if both:
        # Preserve one English official tag and render the Japanese tag in Korean.
        ko=re.sub(r'#DATEWARS(\s+)#DATEWARS',r'#데이트워즈\1#DATEWARS',ko,count=1)
        if ko==old:
            # Handle reversed order or separated lines without touching all English occurrences.
            pos=ko.find('#DATEWARS')
            if pos>=0:ko=ko[:pos]+'#데이트워즈'+ko[pos+len('#DATEWARS'):]
    else:
        ko=ko.replace('#DATEWARS','#데이트워즈')
        ko=ko.replace('DATEWARS','데이트 워즈') if 'DATEWARS' not in ja else ko
    if ko!=old:manual[tid]=ko;changed+=1
(DATA/'manual-translations.json').write_text(json.dumps(manual,ensure_ascii=False,indent=2)+'\n','utf-8')
print('DATEWARS manual fixes',changed)
