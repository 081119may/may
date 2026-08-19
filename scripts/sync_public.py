#!/usr/bin/env python3
import datetime as dt, json, os, pathlib, re, urllib.request
from bs4 import BeautifulSoup

ROOT=pathlib.Path(__file__).resolve().parents[1]
PROFILE=ROOT/'profile.json'
OPENAI_KEY=os.getenv('OPENAI_API_KEY','').strip()
MODEL=os.getenv('OPENAI_TRANSLATE_MODEL','gpt-5-mini')
UA='Mozilla/5.0 MayArchiveBot/2.0'
AMUSE='https://www.amuse.co.jp/artist/A9019/'
EVENTERNOTE='https://www.eventernote.com/actors/%E6%A9%98%E3%82%81%E3%81%84/78099/events'

def fetch_text(url):
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept-Language':'ja,en;q=0.8'})
    with urllib.request.urlopen(req,timeout=45) as r:html=r.read().decode('utf-8','ignore')
    soup=BeautifulSoup(html,'html.parser')
    for t in soup(['script','style','noscript','svg']):t.decompose()
    for a in soup.find_all('a',href=True):
        label=' '.join(a.stripped_strings)
        if label:a.string=f'{label} ({a.get("href")})'
    return re.sub(r'\n{3,}','\n\n',soup.get_text('\n',strip=True))[:85000]

def response_text(instructions,user):
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

def main():
    profile=json.loads(PROFILE.read_text('utf-8'));update_age(profile)
    if not OPENAI_KEY:
        PROFILE.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n','utf-8')
        print('OPENAI_API_KEY missing; refreshed computed profile fields only.')
        return
    amuse=fetch_text(AMUSE);events=fetch_text(EVENTERNOTE);today=dt.date.today().isoformat()
    current=json.dumps({'fields':profile.get('fields',[]),'information':profile.get('information',[]),'related_topics':profile.get('related_topics',[]),'upcoming':profile.get('upcoming',[])},ensure_ascii=False)
    instructions='''Maintain a bilingual Japanese/Korean archive for voice actor 橘めい. Extract only facts supported by the supplied Amuse official profile and Eventernote text. Return one JSON object only with keys fields, information, related_topics, upcoming. information items need type (Media/Live/Other), subtype, date YYYY-MM-DD, title_ja,title_ko,body_ja,body_ko,url. upcoming items need kind (event/broadcast), date, date_label_ja,date_label_ko,title_ja,title_ko,detail_ja,detail_ko,url. Include only future items on or after TODAY. Use Eventernote as a discovery/reference source and prefer official event URLs when present. Keep verified future broadcasts from CURRENT unless contradicted. Translate naturally into Korean while preserving official names. Never invent dates, venues, URLs, roles, or events.'''
    data=parse_json(response_text(instructions,f'TODAY={today}\nCURRENT={current}\n\nAMUSE:\n{amuse}\n\nEVENTERNOTE:\n{events}'))
    for k in ('fields','information','related_topics','upcoming'):
        if isinstance(data.get(k),list):profile[k]=data[k]
    update_age(profile);profile['source_url']=AMUSE;profile['event_source_url']=EVENTERNOTE;profile['auto_updated_at']=dt.datetime.now(dt.timezone.utc).isoformat()
    PROFILE.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n','utf-8')

if __name__=='__main__':main()
