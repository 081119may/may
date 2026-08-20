#!/usr/bin/env python3
import json,pathlib
P=pathlib.Path('data/manual-translations.json')
data=json.loads(P.read_text('utf-8'))
repls=[
 ('#유메미타47_東京','#유메미타47_도쿄'),('#アニメ유메미타','#애니메유메미타'),
 ('#못난이악녀ではございますが','#못난이악녀입니다만'),('#뱅드림10周年ライブ','#뱅드림10주년라이브'),
 ('#뱅드림の日','#뱅드림의날'),('#뱅드림ストア','#뱅드림스토어'),
 ('#사사코이アトレ','#사사코이아트레'),('#사사코이サンリオ','#사사코이산리오'),
 ('生誕祭','생탄제'),('誕生祭','탄생제'),('参ノ章','3장'),('테츠료会','테츠료회'),
 ('타케우치 준코のTake a chance ラジオ ダッシュ！','타케우치 준코의 Take a chance 라디오 대시!'),
 ('사타 미사키','사다 미사키'),('스즈미 오우카','스즈미 사쿠라'),('오우카짱','사쿠라짱'),
 ('스쿠나히토나노카미 우네','스쿠나히토나노카미 토네'),('우네짱','토네짱'),
 ('노노야마 카제','노노야마 후'),('카제짱','후짱'),
 ('콘페와 릴리','콤페토 리리'),('콘페토 릴리','콤페토 리리'),('콘페토 리리','콤페토 리리'),
 ('스가 레이카','스가 라이카'),('레이카짱','라이카짱'),('마바시 미쿠','마하시 미쿠')
]
changed=0
for tid,text in list(data.items()):
 old=text
 for a,b in repls:text=text.replace(a,b)
 if text!=old:data[tid]=text;changed+=1
P.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
print('residual manual fixes',changed)
