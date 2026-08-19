#!/usr/bin/env python3
import datetime as dt, json, os, pathlib, re, urllib.request
from bs4 import BeautifulSoup

ROOT=pathlib.Path(__file__).resolve().parents[1]
PROFILE=ROOT/'profile.json'
OPENAI_KEY=os.getenv('OPENAI_API_KEY','').strip()
MODEL=os.getenv('OPENAI_TRANSLATE_MODEL','gpt-5-mini')
UA='Mozilla/5.0 MayArchiveBot/3.0'
AMUSE='https://www.amuse.co.jp/artist/A9019/'
EVENTERNOTE='https://www.eventernote.com/actors/%E6%A9%98%E3%82%81%E3%81%84/78099/events'

def fetch_text(url):
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept-Language':'ja,en;q=0.8'})
    with urllib.request.urlopen(req,timeout=45) as r:html=r.read().decode('utf-8','ignore')
    soup=BeautifulSoup(html,'html.parser')
    for t in soup(['script','style','noscript','svg']):t.decompose()
    return re.sub(r'\n{3,}','\n\n',soup.get_text('\n',strip=True))[:100000]

def fetch_amuse_rendered():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            page=browser.new_page(viewport={'width':1280,'height':1600},locale='ja-JP')
            page.goto(AMUSE,wait_until='networkidle',timeout=90000)
            for _ in range(30):
                loc=page.get_by_text('もっと見る',exact=True)
                if loc.count()==0:break
                try:
                    if not loc.first.is_visible():break
                    loc.first.click(timeout=5000)
                    page.wait_for_timeout(900)
                except Exception:break
            text=page.locator('body').inner_text()
            browser.close()
            return text[:180000]
    except Exception as e:
        print('Playwright Amuse render failed:',repr(e))
        return fetch_text(AMUSE)

def response_text(instructions,user):
    if not OPENAI_KEY:return ''
    body=json.dumps({'model':MODEL,'store':False,'input':[{'role':'developer','content':instructions},{'role':'user','content':user}]},ensure_ascii=False).encode()
    req=urllib.request.Request('https://api.openai.com/v1/responses',data=body,headers={'Authorization':f'Bearer {OPENAI_KEY}','Content-Type':'application/json','User-Agent':UA},method='POST')
    with urllib.request.urlopen(req,timeout=120) as r:data=json.load(r)
    out=[]
    for item in data.get('output',[]):
        for c in item.get('content',[]):
            if c.get('type') in ('output_text','text') and c.get('text'):out.append(c['text'])
    return '\n'.join(out).strip()

def parse_json(s):
    s=re.sub(r'^```(?:json)?\s*|\s*```$','',s.strip(),flags=re.S)
    m=re.search(r'\{.*\}',s,re.S)
    if not m:raise ValueError('no JSON object in model output')
    return json.loads(m.group(0))

def update_age(profile):
    today=dt.date.today();birth=dt.date(2008,11,19);age=today.year-birth.year-((today.month,today.day)<(birth.month,birth.day))
    for f in profile.get('fields',[]):
        if f.get('label_ja')=='年齢':f['value_ja']=f'{age}歳';f['value_ko']=f'{age}세'

def jp_date_to_iso(s):
    m=re.search(r'(20\d{2})年\s*(\d{1,2})月\s*(\d{1,2})日',s)
    return f'{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}' if m else ''

def deterministic_information(text):
    a=text.find('インフォメーション')
    if a<0:return []
    b=text.find('橘 めいの関連トピックス',a)
    section=text[a:b if b>0 else len(text)]
    lines=[x.strip() for x in section.splitlines() if x.strip()]
    cats={'Media','Live','Other','Release'}
    subtypes={'Event','Live','Stage','TV/WebTV','TV','Web','Radio','CM','Movie','Magazine','Book','Music','TICKET','PRESENT','GAME','Release','DVD/Blu-ray'}
    dates=[i for i,x in enumerate(lines) if re.fullmatch(r'20\d{2}年\s*\d{1,2}月\s*\d{1,2}日',x)]
    out=[]
    for n,i in enumerate(dates):
        prev=lines[max(0,i-3):i]
        typ=next((x for x in reversed(prev) if x in cats),'Other')
        subtype=next((x for x in reversed(prev) if x in subtypes and x!=typ),'')
        end=dates[n+1]-2 if n+1<len(dates) else len(lines)
        chunk=lines[i+1:max(i+2,end)]
        while chunk and chunk[-1] in cats|subtypes|{'もっと見る','ALL'}:chunk.pop()
        title=chunk[0] if chunk else ''
        body='\n'.join(chunk[1:]).strip()
        urls=re.findall(r'https?://[^\s）)]+',title+'\n'+body)
        out.append({'type':typ,'subtype':subtype,'date':jp_date_to_iso(lines[i]),'title_ja':title,'title_ko':title,'body_ja':body,'body_ko':body,'url':urls[0] if urls else AMUSE})
    seen=set();clean=[]
    for x in out:
        k=(x['date'],x['title_ja'])
        if x['title_ja'] and k not in seen:seen.add(k);clean.append(x)
    return clean

def main():
    profile=json.loads(PROFILE.read_text('utf-8'));update_age(profile)
    amuse=fetch_amuse_rendered();events=fetch_text(EVENTERNOTE);today=dt.date.today().isoformat()
    deterministic=deterministic_information(amuse)
    if deterministic:
        profile['information']=deterministic
        print('Amuse information items after expanding もっと見る:',len(deterministic))
    if OPENAI_KEY:
        current=json.dumps({'fields':profile.get('fields',[]),'information':profile.get('information',[]),'related_topics':profile.get('related_topics',[]),'upcoming':profile.get('upcoming',[])},ensure_ascii=False)
        instructions='''Maintain a bilingual Japanese/Korean archive for voice actor 橘めい. The AMUSE text was collected after clicking もっと見る until all information was expanded. Return one JSON object only with keys fields, information, related_topics, upcoming. Preserve EVERY Amuse information item supplied; never truncate older items. information items need type, subtype, date YYYY-MM-DD, title_ja,title_ko,body_ja,body_ko,url. upcoming items need kind (event/broadcast), date, date_label_ja,date_label_ko,title_ja,title_ko,detail_ja,detail_ko,url. For upcoming include only future items on or after TODAY. Use Eventernote for discovery/reference and prefer official URLs when present. Keep verified future broadcasts from CURRENT unless contradicted. Translate naturally into Korean while preserving official names. Never invent dates, venues, URLs, roles, or events.'''
        data=parse_json(response_text(instructions,f'TODAY={today}\nCURRENT={current}\n\nAMUSE FULL EXPANDED:\n{amuse}\n\nEVENTERNOTE:\n{events}'))
        for k in ('fields','information','related_topics','upcoming'):
            if isinstance(data.get(k),list):profile[k]=data[k]
    else:
        print('OPENAI_API_KEY missing; keeping Korean fallback as Japanese for newly discovered Amuse entries.')
    update_age(profile);profile['source_url']=AMUSE;profile['event_source_url']=EVENTERNOTE;profile['auto_updated_at']=dt.datetime.now(dt.timezone.utc).isoformat()
    PROFILE.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n','utf-8')

if __name__=='__main__':main()
