let voiceFileMapPromise=null;
function getVoiceFileMap(){
  if(!voiceFileMapPromise) voiceFileMapPromise=fetch('data/voice-map.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`voice map ${r.status}`);return r.json()});
  return voiceFileMapPromise;
}
window.wireVoice=function(){
  const audio=$('#voicePlayer');
  if(!audio)return;
  audio.preload='metadata';
  audio.controls=true;
  audio.style.width='100%';
  audio.style.marginTop='14px';

  let tools=$('#voiceSeekTools');
  if(!tools){
    tools=document.createElement('div');
    tools.id='voiceSeekTools';
    tools.className='voice-seek-tools';
    tools.innerHTML='<button type="button" data-seek="-5">−5초</button><span id="voiceSeekTime">0:00 / 0:00</span><button type="button" data-seek="5">+5초</button>';
    audio.insertAdjacentElement('afterend',tools);
  }

  const fmt=s=>{
    s=Number.isFinite(s)?Math.max(0,Math.floor(s)):0;
    return `${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}`;
  };
  const updateTime=()=>{
    const el=$('#voiceSeekTime');
    if(el)el.textContent=`${fmt(audio.currentTime)} / ${fmt(audio.duration)}`;
  };
  $$('#voiceSeekTools button').forEach(b=>b.onclick=()=>{
    if(!Number.isFinite(audio.duration))return;
    audio.currentTime=Math.min(audio.duration,Math.max(0,audio.currentTime+Number(b.dataset.seek||0)));
    updateTime();
  });

  const reset=()=>$$('.voice-row').forEach(b=>{b.classList.remove('playing');const p=b.querySelector('.voice-play');if(p)p.textContent='▶'});
  const stop=()=>{audio.pause();reset();state.playing=null;};
  $$('.voice-row').forEach(btn=>btn.onclick=async()=>{
    const id=btn.dataset.id;
    if(state.playing===id&&!audio.paused){stop();return;}
    reset();
    $('#voiceNow').textContent=t('voiceLoading');
    try{
      const files=await getVoiceFileMap();
      const src=files[id];
      if(!src)throw new Error(`missing voice ${id}`);
      if(audio.getAttribute('src')!==src){audio.src=src;audio.load();}
      state.playing=id;
      btn.classList.add('playing');
      btn.querySelector('.voice-play').textContent='❚❚';
      $('#voiceNow').textContent=btn.querySelector('.voice-name').textContent;
      audio.currentTime=0;
      await audio.play();
      updateTime();
    }catch(e){
      console.error(e);
      reset();state.playing=null;
      $('#voiceNow').textContent=t('voiceError');
    }
  });
  audio.ontimeupdate=updateTime;
  audio.onloadedmetadata=updateTime;
  audio.onended=()=>{reset();state.playing=null;updateTime()};
  audio.onpause=()=>{if(state.playing){const b=$(`.voice-row[data-id="${state.playing}"]`);if(b){b.classList.remove('playing');const p=b.querySelector('.voice-play');if(p)p.textContent='▶'}}updateTime()};
  audio.onplay=()=>{if(state.playing){const b=$(`.voice-row[data-id="${state.playing}"]`);if(b){b.classList.add('playing');const p=b.querySelector('.voice-play');if(p)p.textContent='❚❚'}}updateTime()};
};

(()=>{
  const s=document.createElement('style');
  s.textContent='.voice-seek-tools{display:flex;align-items:center;justify-content:center;gap:12px;margin:8px 0 2px}.voice-seek-tools button{border:1px solid var(--line);background:var(--panel2);color:var(--text);border-radius:999px;padding:7px 12px;font:inherit;font-size:12px;font-weight:850;cursor:pointer}.voice-seek-tools span{min-width:92px;text-align:center;color:var(--muted);font-size:12px;font-variant-numeric:tabular-nums}';
  document.head.appendChild(s);
})();