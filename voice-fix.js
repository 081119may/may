let voiceFileMapPromise=null;
function getVoiceFileMap(){
  if(!voiceFileMapPromise) voiceFileMapPromise=fetch('data/voice-map.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`voice map ${r.status}`);return r.json()});
  return voiceFileMapPromise;
}
window.wireVoice=function(){
  const audio=$('#voicePlayer');
  if(!audio)return;
  audio.preload='metadata';
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
    }catch(e){
      console.error(e);
      reset();state.playing=null;
      $('#voiceNow').textContent=t('voiceError');
    }
  });
  audio.onended=()=>{reset();state.playing=null};
  audio.onpause=()=>{if(state.playing){const b=$(`.voice-row[data-id="${state.playing}"]`);if(b){b.classList.remove('playing');const p=b.querySelector('.voice-play');if(p)p.textContent='▶'}}};
  audio.onplay=()=>{if(state.playing){const b=$(`.voice-row[data-id="${state.playing}"]`);if(b){b.classList.add('playing');const p=b.querySelector('.voice-play');if(p)p.textContent='❚❚'}}};
};