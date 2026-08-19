const VOICE_SPRITE='audio/voice_all.mp3';
const VOICE_SEGMENTS={
  voice_sample_1:[0,23.823673],
  voice_sample_2:[23.823673,55.797551],
  voice_sample_3:[55.797551,97.697959],
  voice_sample_4:[97.697959,133.067755],
  voice_sample_5:[133.067755,163.631020],
  narration:[163.631020,194.847347]
};
window.wireVoice=function(){
  const audio=$('#voicePlayer');
  if(!audio)return;
  audio.preload='auto';
  audio.src=VOICE_SPRITE;
  let activeEnd=0;
  const resetButtons=()=>$$('.voice-row').forEach(b=>{b.classList.remove('playing');const p=b.querySelector('.voice-play');if(p)p.textContent='▶'});
  const stop=()=>{audio.pause();resetButtons();state.playing=null;activeEnd=0;};
  const playSegment=async(btn)=>{
    const id=btn.dataset.id;
    const seg=VOICE_SEGMENTS[id];
    if(!seg){$('#voiceNow').textContent=state.lang==='ko'?'음성 구간 정보가 없습니다.':'音声区間情報がありません。';return;}
    if(state.playing===id&&!audio.paused){stop();return;}
    resetButtons();
    state.playing=id;
    activeEnd=seg[1];
    btn.classList.add('playing');
    btn.querySelector('.voice-play').textContent='❚❚';
    $('#voiceNow').textContent=btn.querySelector('.voice-name').textContent;
    try{
      if(audio.readyState<1){
        await new Promise((resolve,reject)=>{
          const ok=()=>{cleanup();resolve()};
          const bad=()=>{cleanup();reject(audio.error||new Error('audio load failed'))};
          const cleanup=()=>{audio.removeEventListener('loadedmetadata',ok);audio.removeEventListener('error',bad)};
          audio.addEventListener('loadedmetadata',ok,{once:true});
          audio.addEventListener('error',bad,{once:true});
          audio.load();
        });
      }
      audio.currentTime=seg[0]+0.01;
      await audio.play();
    }catch(e){
      console.error(e);
      resetButtons();
      state.playing=null;
      $('#voiceNow').textContent=state.lang==='ko'?'음성을 재생하지 못했습니다. 새로고침 후 다시 눌러주세요.':'音声を再生できませんでした。再読み込みしてもう一度お試しください。';
    }
  };
  $$('.voice-row').forEach(btn=>btn.onclick=()=>playSegment(btn));
  audio.ontimeupdate=()=>{
    if(state.playing&&activeEnd&&audio.currentTime>=activeEnd-0.03)stop();
    else if(state.playing){
      const b=$(`.voice-row[data-id="${state.playing}"]`);
      if(b){const seg=VOICE_SEGMENTS[state.playing];const elapsed=Math.max(0,audio.currentTime-seg[0]);const m=Math.floor(elapsed/60),s=String(Math.floor(elapsed%60)).padStart(2,'0');$('#voiceNow').textContent=`${b.querySelector('.voice-name').textContent}  ${m}:${s}`;}
    }
  };
  audio.onended=stop;
  audio.onerror=()=>{resetButtons();state.playing=null;$('#voiceNow').textContent=state.lang==='ko'?'음원 파일을 불러오지 못했습니다.':'音声ファイルを読み込めませんでした。';};
};