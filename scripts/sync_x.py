#!/usr/bin/env python3
import base64, datetime as dt, gzip, json, os, pathlib, time, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
USERNAME=os.getenv('X_USERNAME','May_o_o_T')
TOKEN=os.getenv('X_BEARER_TOKEN','').strip()
OPENAI_KEY=os.getenv('OPENAI_API_KEY','').strip()
TRANSLATE_MODEL=os.getenv('OPENAI_TRANSLATE_MODEL','gpt-5-mini')
UA='Mozilla/5.0 MayArchiveBot/2.0'

def read_json(path,default=None):
    try:return json.loads(path.read_text('utf-8'))
    except Exception:return default

def api_json(url,headers=None,timeout=40):
    h={'User-Agent':UA,'Accept':'application/json'}
    if headers:h.update(headers)
    req=urllib.request.Request(url,headers=h)
    with urllib.request.urlopen(req,timeout=timeout) as r:return json.load(r)

def openai_text(instructions,text):
    if not OPENAI_KEY:return ''
    body=json.dumps({'model':TRANSLATE_MODEL,'store':False,'input':[{'role':'developer','content':instructions},{'role':'user','content':text}]},ensure_ascii=False).encode()
    req=urllib.request.Request('https://api.openai.com/v1/responses',data=body,headers={'Authorization':f'Bearer {OPENAI_KEY}','Content-Type':'application/json','User-Agent':UA},method='POST')
    with urllib.request.urlopen(req,timeout=90) as r:data=json.load(r)
    chunks=[]
    for item in data.get('output',[]):
        for c in item.get('content',[]):
            if c.get('type') in ('output_text','text') and c.get('text'):chunks.append(c['text'])
    return '\n'.join(chunks).strip()

def translate_ko(text):
    if not text:return ''
    return openai_text('일본어 X 게시물을 자연스러운 한국어로 번역하세요. 해시태그, 고유명사, 이모지, 줄바꿈을 최대한 보존하고 설명 없이 번역문만 출력하세요.',text)

def load_archive():
    manifest=read_json(DATA/'manifest.json',{}) or {}
    parts=manifest.get('archive_parts') or []
    if not parts:return manifest,[]
    b64=''.join((ROOT/p).read_text('utf-8').strip() for p in parts)
    raw=gzip.decompress(base64.b64decode(b64))
    return manifest,json.loads(raw.decode('utf-8'))

def save_archive(manifest,posts):
    posts.sort(key=lambda x:x.get('date',''),reverse=True)
    raw=json.dumps(posts,ensure_ascii=False,separators=(',',':')).encode('utf-8')
    blob=base64.b64encode(gzip.compress(raw,compresslevel=9)).decode('ascii')
    (DATA/'archive-auto.b64').write_text(blob,'utf-8')
    manifest.update({'format':'gzip-base64-parts','archive_parts':['data/archive-auto.b64'],'tweet_count':len(posts),'translation_count':sum(1 for p in posts if p.get('ko')),'full_archive_count':len(posts),'media_count':sum(len(p.get('media') or []) for p in posts),'media_base':'media_remote/','status':'auto','updated_at':dt.datetime.now(dt.timezone.utc).isoformat()})
    (DATA/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf-8')
    (DATA/'tweet_ids.txt').write_text('\n'.join(str(p['id']) for p in posts if p.get('id'))+'\n','utf-8')

def best_media(m):
    typ=m.get('type','')
    if typ=='photo' and m.get('url'):return m['url'],'jpg'
    variants=[v for v in m.get('variants',[]) if str(v.get('content_type','')).startswith('video/mp4') and v.get('url')]
    if variants:
        variants.sort(key=lambda v:v.get('bit_rate') or 0,reverse=True)
        return variants[0]['url'],'mp4'
    if m.get('preview_image_url'):return m['preview_image_url'],'jpg'
    return None,None

def download(url,path):
    if path.exists() and path.stat().st_size>1000:return True
    req=urllib.request.Request(url,headers={'User-Agent':UA})
    with urllib.request.urlopen(req,timeout=90) as r:
        length=int(r.headers.get('Content-Length') or 0)
        if length>90*1024*1024:return False
        data=r.read(90*1024*1024+1)
    if len(data)>90*1024*1024:return False
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);return True

def main():
    manifest,posts=load_archive();known={str(p.get('id')) for p in posts}
    if not TOKEN:
        print('X_BEARER_TOKEN is not configured; keeping existing archive unchanged.')
        return
    auth={'Authorization':f'Bearer {TOKEN}'}
    user=api_json(f'https://api.x.com/2/users/by/username/{urllib.parse.quote(USERNAME)}',auth).get('data') or {}
    uid=user.get('id')
    if not uid:raise SystemExit('Could not resolve X user id')
    found=[];token=None;media_by_key={}
    for _ in range(10):
        q={'max_results':'100','exclude':'retweets','tweet.fields':'created_at,public_metrics,attachments,note_tweet','expansions':'attachments.media_keys','media.fields':'type,url,preview_image_url,variants,width,height'}
        if token:q['pagination_token']=token
        payload=api_json(f'https://api.x.com/2/users/{uid}/tweets?'+urllib.parse.urlencode(q),auth)
        for m in (payload.get('includes') or {}).get('media',[]):media_by_key[m.get('media_key')]=m
        page_posts=payload.get('data') or [];found.extend(page_posts)
        if any(str(x.get('id')) in known for x in page_posts):break
        token=(payload.get('meta') or {}).get('next_token')
        if not token:break
        time.sleep(.3)
    new=[x for x in found if str(x.get('id')) not in known]
    print('new X posts',len(new))
    for x in reversed(new):
        tid=str(x['id']);text=((x.get('note_tweet') or {}).get('text') or x.get('text') or '').strip()
        created=x.get('created_at') or dt.datetime.now(dt.timezone.utc).isoformat()
        d=dt.datetime.fromisoformat(created.replace('Z','+00:00')).astimezone(ZoneInfo('Asia/Tokyo'))
        metrics=x.get('public_metrics') or {};paths=[]
        for i,key in enumerate((x.get('attachments') or {}).get('media_keys') or [],1):
            u,ext=best_media(media_by_key.get(key) or {})
            if not u:continue
            rel=f'media_remote/{tid}_{i}.{ext}'
            if download(u,ROOT/rel):paths.append(rel)
        posts.append({'id':tid,'date':d.strftime('%Y-%m-%d %H:%M:%S'),'name':'橘めい','handle':USERNAME,'ja':text,'ko':translate_ko(text) if OPENAI_KEY else '','reply':metrics.get('reply_count',0),'retweet':metrics.get('retweet_count',0),'favorite':metrics.get('like_count',0),'views':metrics.get('impression_count',0),'has_media':bool(paths),'media':paths})
    if new:save_archive(manifest,posts)

if __name__=='__main__':main()
