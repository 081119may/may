const voiceCache=new Map();
async function getVoiceUrl(id){
  if(voiceCache.has(id)) return voiceCache.get(id);
  const r=await fetch(`voice_data/${id}.txt`,{cache:'no-store'});
  if(!r.ok) throw new Error(`voice ${id}: ${r.status}`);
  const b64=(await r.text()).replace(/\s/g,'');
  const bin=atob(b64), bytes=new Uint8Array(bin.length);
  for(let i=0;i<bin.length;i++) bytes[i]=bin.charCodeAt(i);
  const url=URL.createObjectURL(new Blob([bytes],{type:'audio/ogg'}));
  voiceCache.set(id,url);
  return url;
}
window.wireVoice=function(){
  const audio=$('#voicePlayer'); if(!audio)return;
  audio.preload='auto'; audio.volume=1;
  const reset=()=>$$('.voice-row').forEach(b=>{b.classList.remove('playing');const p=b.querySelector('.voice-play');if(p)p.textContent='▶'});
  $$('.voice-row').forEach(btn=>btn.onclick=async()=>{
    const id=btn.dataset.id;
    if(state.playing===id&&!audio.paused){audio.pause();reset();state.playing=null;$('#voiceNow').textContent='';return;}
    reset(); $('#voiceNow').textContent=t('voiceLoading');
    try{
      const url=await getVoiceUrl(id);
      audio.pause(); audio.src=url; audio.currentTime=0; audio.load();
      state.playing=id; btn.classList.add('playing'); btn.querySelector('.voice-play').textContent='❚❚';
      await audio.play();
      $('#voiceNow').textContent=btn.querySelector('.voice-name').textContent;
    }catch(e){
      console.error(e); reset(); state.playing=null; $('#voiceNow').textContent=t('voiceError');
    }
  });
  audio.ontimeupdate=()=>{
    if(!state.playing)return;
    const b=$(`.voice-row[data-id="${state.playing}"]`); if(!b)return;
    const sec=Math.floor(audio.currentTime||0),m=Math.floor(sec/60),s=String(sec%60).padStart(2,'0');
    $('#voiceNow').textContent=`${b.querySelector('.voice-name').textContent}  ${m}:${s}`;
  };
  audio.onended=()=>{reset();state.playing=null;$('#voiceNow').textContent='';};
  audio.onerror=()=>{reset();state.playing=null;$('#voiceNow').textContent=t('voiceError');};
};