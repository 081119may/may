#!/usr/bin/env python3
import base64, datetime as dt, gzip, json, os, pathlib, time, urllib.error, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
USERNAME=os.getenv('X_USERNAME','May_o_o_T')
UA='Mozilla/5.0 MayArchiveBot/5.0'
TOKYO=ZoneInfo('Asia/Tokyo')

def read_json(path,default=None):
    try:return json.loads(path.read_text('utf-8'))
    except Exception:return default

MANUAL=read_json(DATA/'manual-translations.json',{}) or {}

def get_json(url,timeout=45):
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            if r.status==204:return {'code':204,'results':[]}
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code==204:return {'code':204,'results':[]}
        raise

def load_archive():
    m=read_json(DATA/'manifest.json',{}) or {};parts=m.get('archive_parts') or []
    if not parts:return m,[]
    b64=''.join((ROOT/p).read_text('utf-8').strip() for p in parts)
    return m,json.loads(gzip.decompress(base64.b64decode(b64)).decode('utf-8'))

def save_archive(m,posts):
    posts.sort(key=lambda x:x.get('date',''),reverse=True)
    raw=json.dumps(posts,ensure_ascii=False,separators=(',',':')).encode()
    (DATA/'archive-auto.b64').write_text(base64.b64encode(gzip.compress(raw,9)).decode(),'utf-8')
    m.update({'format':'gzip-base64-parts','archive_parts':['data/archive-auto.b64'],'tweet_count':len(posts),'translation_count':sum(bool(MANUAL.get(str(p.get('id'))) or p.get('ko')) for p in posts),'full_archive_count':len(posts),'media_count':sum(len(p.get('media') or []) for p in posts),'media_base':'media_remote/','status':'auto','updated_at':dt.datetime.now(dt.timezone.utc).isoformat()})
    (DATA/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf-8')
    (DATA/'tweet_ids.txt').write_text('\n'.join(str(p['id']) for p in posts if p.get('id'))+'\n','utf-8')
    # Human/manual translation review source. One tweet per line so it is easy to inspect in chunks.
    with (DATA/'archive-review.jsonl').open('w',encoding='utf-8') as f:
        for p in posts:
            f.write(json.dumps({'id':str(p.get('id','')),'date':p.get('date',''),'ja':p.get('ja',''),'current_ko':MANUAL.get(str(p.get('id'))) or p.get('ko','')},ensure_ascii=False)+'\n')

def parse_time(v):
    if isinstance(v,(int,float)):return dt.datetime.fromtimestamp(v,dt.timezone.utc).astimezone(TOKYO)
    s=str(v or '')
    try:return dt.datetime.fromisoformat(s.replace('Z','+00:00')).astimezone(TOKYO)
    except Exception:
        try:return dt.datetime.strptime(s,'%a %b %d %H:%M:%S %z %Y').astimezone(TOKYO)
        except Exception:return dt.datetime.now(TOKYO)

def latest_epoch(posts):
    vals=[]
    for p in posts:
        try:vals.append(dt.datetime.strptime(p['date'],'%Y-%m-%d %H:%M:%S').replace(tzinfo=TOKYO).timestamp())
        except Exception:pass
    return max(vals)-120 if vals else 0

def media_source(m):
    typ=(m.get('type') or '').lower()
    if typ=='photo' and m.get('url'):return m['url'],'jpg'
    fs=[x for x in (m.get('formats') or []) if x.get('url') and (x.get('container')=='mp4' or '.mp4' in x.get('url','').split('?')[0].lower())]
    if fs:
        fs.sort(key=lambda x:x.get('bitrate') or x.get('size') or 0,reverse=True);return fs[0]['url'],'mp4'
    u=m.get('transcode_url') or m.get('url') or m.get('thumbnail_url')
    return (u,'mp4' if typ in ('video','gif') and u and '.mp4' in u.lower() else 'jpg') if u else (None,None)

def download(url,path):
    if path.exists() and path.stat().st_size>1000:return True
    req=urllib.request.Request(url,headers={'User-Agent':UA})
    with urllib.request.urlopen(req,timeout=90) as r:data=r.read(90*1024*1024+1)
    if len(data)>90*1024*1024:return False
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);return True

def fetch_page(params):
    url=f'https://api.fxtwitter.com/2/profile/{urllib.parse.quote(USERNAME)}/statuses?'+urllib.parse.urlencode(params)
    return get_json(url)

def fetch_new(posts):
    since=int(latest_epoch(posts));known={str(p.get('id')) for p in posts};found=[];cursor=None
    for _ in range(5):
        q={'count':'100','with_replies':'1'}
        if cursor:q['cursor']=cursor
        elif since:q['since']=str(since)
        data=fetch_page(q);results=[x for x in (data.get('results') or []) if isinstance(x,dict) and x.get('type')=='status']
        if not results:break
        stop=False
        for x in results:
            tid=str(x.get('id') or '')
            if tid in known:stop=True;continue
            if tid and tid not in {str(y.get('id')) for y in found}:found.append(x)
        if stop:break
        cursor=(data.get('cursor') or {}).get('bottom')
        if not cursor:break
        time.sleep(.2)
    return found

def convert(x):
    tid=str(x['id']);d=parse_time(x.get('created_at') or x.get('created_timestamp'));paths=[]
    mo=x.get('media') or {};media=(mo.get('all') or ((mo.get('photos') or [])+(mo.get('videos') or []))) if isinstance(mo,dict) else (mo if isinstance(mo,list) else [])
    for i,m in enumerate(media,1):
        u,ext=media_source(m or {})
        if not u:continue
        rel=f'media_remote/{tid}_{i}.{ext}'
        try:
            if download(u,ROOT/rel):paths.append(rel)
        except Exception as e:print('media WARN',tid,repr(e))
    author=x.get('author') or {};text=(x.get('text') or '').strip()
    # No automatic translation. New tweets enter with an empty Korean field until manually translated.
    return {'id':tid,'date':d.strftime('%Y-%m-%d %H:%M:%S'),'name':author.get('name') or '橘めい','handle':author.get('screen_name') or USERNAME,'ja':text,'ko':'','reply':x.get('replies',0) or 0,'retweet':x.get('reposts',0) or 0,'favorite':x.get('likes',0) or 0,'views':x.get('views',0) or 0,'has_media':bool(paths),'media':paths}

def main():
    m,posts=load_archive();new=fetch_new(posts)
    print('archive',len(posts),'new X posts',len(new),'since',int(latest_epoch(posts)))
    if new:posts.extend(convert(x) for x in reversed(new))
    # Always regenerate review file so manual translation work sees the current archive.
    save_archive(m,posts)

if __name__=='__main__':main()
