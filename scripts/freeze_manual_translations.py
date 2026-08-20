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

# One-time editorial mappings. These are applied once to the static manual translation file;
# production/runtime code never machine-translates or rewrites Korean text.
EDITORIAL=[
('魔法の姉妹ルルットリリィ','마법의 자매 루루토 릴리'),('ルルットリリィ','루루토 릴리'),
('てつりょー！meet with 鉄道むすめ','테츠료! meet with 철도무스메'),('てつりょー! meet with 鉄道むすめ','테츠료! meet with 철도무스메'),
('夢限大みゅーたいぷ','무겐다이 뮤타입'),('光が死んだ夏','히카루가 죽은 여름'),
('ふつつかな悪女ではございますが','못난이 악녀입니다만'),('きみが死ぬまで恋をしたい','네가 죽을 때까지 사랑하고 싶어'),
('エリスの聖杯','에리스의 성배'),('薫る花は凛と咲く','향기로운 꽃은 늠름하게 핀다'),
('死亡遊戯で飯を食う。','사망유희로 밥을 먹는다.'),('終末ツーリング','종말 투어링'),
('炎炎ノ消防隊 参ノ章','불꽃 소방대 3장'),('多聞くん今どっち','타몬 군 지금 어느 쪽?'),
('スキップとローファー','스킵과 로퍼'),('ささやくように恋を唄う','속삭이듯 사랑을 노래하다'),
('魔法の天使クリーミィマミ','마법의 천사 크리미 마미'),('ぴえろ魔法少女シリーズ','피에로 마법소녀 시리즈'),
('ホーミー・タイッ！！','호미 타잇!!'),('ホーミー・タイッ‼︎','호미 타잇!!'),('マジカルランデブー','매지컬 랑데부'),
('わたし未来線','나의 미래선'),('デリケートに好きして','델리케이트하게 좋아해 줘'),
('トレセンラーメン列伝','트레센 라멘 열전'),('フラッシュバックメモリー〜時代を駆ける物怪たち〜','플래시백 메모리 ~시대를 달리는 요괴들~'),
('アンチプライド・カタルシス','안티프라이드 카타르시스'),('アンチプライドカタルシス','안티프라이드 카타르시스'),
('ワールドエンド','월드 엔드'),('つなぎ目の向こうに','이어진 곳 너머로'),
('スーパーポジション ～スピンアップ編～','슈퍼포지션 ~스핀업 편~'),('スーパーポジション〜スピンアップ編〜','슈퍼포지션 ~스핀업 편~'),
('アンロック・ザ・フューチャー','언록 더 퓨처'),('命に嫌われている','생명에게 미움받고 있어'),
('赤いスイートピー','붉은 스위트피'),('強がりなシルエット','강한 척하는 실루엣'),
('はじめましてリリィです！','처음 뵙겠습니다, 릴리입니다!'),('星をつかんだ日','별을 잡은 날'),
('授業中ランデブー','수업 중 랑데부'),('限界までPompon！！','한계까지 Pompon!!'),
('DESIRE -情熱−','DESIRE -정열-'),('世界の中心で','세상의 중심에서'),('自販機の怪','자판기의 괴이'),
('起死開戦','기사개전'),('スタットネオネオン','스타트 네오네온'),('エコー','에코'),
('竹内順子','타케우치 준코'),('D4DJチャンネル','D4DJ 채널'),('グルミク','그루믹스'),
('ネトゲ廃人シュプレヒコール','네토게 폐인 슈프레히코어'),('ローリンガール','롤링 걸'),
('神曲','신곡'),('さつきがてんこもりさん','사츠키가텐코모리 님'),('とくPさん','토쿠P 님'),
('みゅーたいぷ','뮤타입'),('鉄道むすめ','철도무스메'),('てつりょー','테츠료'),('いっかだんらん','잇카단란'),
('ときめきフォトスタジオ','두근두근 포토 스튜디오'),('ひめゆり','히메유리'),
('#信澤収イラスト展','#노부사와오사무일러스트전'),('#FLOWフェス','#FLOW페스'),
('#夢限大みゅーたいぷ','#무겐다이뮤타입'),('#유메미타47_東京','#유메미타47_도쿄'),
('#ふつつかな悪女ではございますが','#못난이악녀입니다만'),('#ふつつかな悪女','#못난이악녀'),
('#マキ活','#마키활동'),('#2026声優アーティスト育成プログラム・セレクション','#2026성우아티스트육성프로그램셀렉션'),
('#おそ松さん','#오소마츠상'),('#きみ死ぬアニメ','#키미시누애니'),('#こどもの日','#어린이날'),('#さくらの日','#사쿠라의날'),
('#ときめきフォトスタジオ','#두근두근포토스튜디오'),('#ひめゆり2025','#히메유리2025'),('#るるりら','#루루리라'),
('#アミューズクリエイティブスタジオ','#아뮤즈크리에이티브스튜디오'),('#オセロニア10周年','#오셀로니아10주년'),
('#逆転オセロニア','#역전오셀로니아'),('#キンキーブーツ','#킹키부츠'),('#ジュンチャンス','#준찬스'),
('#フロフェちゃん','#후로페짱'),('#ミュージカルh12','#뮤지컬H12'),('#宿題は終わりました','#숙제는끝났습니다'),
('#戦国繚乱美少女伝','#전국요란미소녀전'),('#炎炎ノ消防隊','#불꽃소방대'),('#神立塔子生誕祭','#칸다치토코생탄제'),
('#뱅드림10周年ライブ','#뱅드림10주년라이브'),('#뱅드림の日','#뱅드림의날'),('#뱅드림ストア','#뱅드림스토어'),
('#사사코이アトレ','#사사코이아트레'),('#사사코이サンリオ','#사사코이산리오'),
('#るるりりファンアート','#루루리리팬아트'),('#るるりりプロフ帳','#루루리리프로필북'),('#るるりり','#루루리리'),
('#ひかなつ舞台','#히카나츠무대'),('#てつりょー会','#테츠료회'),('#てつりょー','#테츠료'),('#鉄むす20th','#철도무스메20th'),
('#アニメジャパン','#애니메재팬'),('#アミュボch','#아뮤보ch'),('#アツドリ','#아츠도리'),('#マチアソビ','#마치아소비'),
('#ミュージカルH12','#뮤지컬H12'),('#舞台ささ恋','#무대사사코이'),('#ささ恋','#사사코이'),
('#ぴえろ魔法少女シリーズ','#피에로마법소녀시리즈'),('#ぴえろ魔法少女','#피에로마법소녀'),
('#けもフレ３','#케모프레3'),('#けものフレンズ','#케모노프렌즈'),('#ウマ娘','#우마무스메'),
('#グルミク','#그루믹스'),('#トミックス','#토믹스'),('#鉄道むすめ','#철도무스메'),
('#クリィミーマミ','#크리미마미'),('#死亡遊戯','#사망유희'),('#エリスの聖杯','#에리스의성배'),
('#薫る花は凛と咲く','#향기로운꽃은늠름하게핀다'),('#多聞くん今どっち','#타몬군지금어느쪽'),
('#スキップとローファー','#스킵과로퍼'),('#スキミュ','#스킵과로퍼뮤지컬'),('#ミクの日','#미쿠의날'),
('#アニメユメミタ','#애니메유메미타'),('#アニメゆめみた','#애니메유메미타'),('#アニメ유메미타','#애니메유메미타')]
EDITORIAL=sorted(EDITORIAL,key=lambda x:len(x[0]),reverse=True)

def normalize(ja,ko):
    for term in terms:
        srcs=term.get('ja') or [];target=term.get('ko') or ''
        if not target or not any(s and s in ja for s in srcs):continue
        for alias in sorted(set(term.get('aliases') or []),key=len,reverse=True):
            if alias and alias!=target:ko=ko.replace(alias,target)
        for src in sorted(srcs,key=len,reverse=True):
            if src and src!=target:ko=ko.replace(src,target)
    for src,target in EDITORIAL:
        if src in ja:ko=ko.replace(src,target)
    if 'さん' in ja:ko=ko.replace('さん','님')
    # User-confirmed readings that older translations rendered phonetically from the kanji.
    if '桜花' in ja:ko=ko.replace('오우카짱','사쿠라짱').replace('오우카','사쿠라')
    if '兎寝' in ja:ko=ko.replace('우네짱','토네짱').replace('우네','토네')
    if '佐多みさき' in ja:ko=ko.replace('사타 미사키','사다 미사키')
    if '野々山' in ja or '風ちゃん' in ja:ko=ko.replace('카제짱','후짱').replace('카제','후')
    if 'こんぺとリリィ' in ja:ko=ko.replace('콘페와 릴리','콤페토 리리').replace('콘페토 릴리','콤페토 리리').replace('콘페토 리리','콤페토 리리')
    # Hashtags cannot contain spaces; use compact Korean spellings there.
    ko=ko.replace('#루루토 릴리','#루루토릴리').replace('#데이트 워즈','#데이트워즈').replace('#뱅드림 TV LIVE','#뱅드림TVLIVE')
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
print('manual',len(final),'missing text posts',len(missing),'editorial fixes',changed,'total',len(posts))
