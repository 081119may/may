const voiceCache=new Map();
async function getVoiceUrl(id){
  if(voiceCache.has(id)) return voiceCache.get(id);
  const r=await fetch(`voice_data/${id}.txt`,{cache:'force-cache'});
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
  $$('.voice-row').forEach(btn=>btn.onclick=async()=>{
    const id=btn.dataset.id;
    if(state.playing===id&&!audio.paused){audio.pause();btn.classList.remove('playing');btn.querySelector('.voice-play').textContent='▶';state.playing=null;return;}
    $$('.voice-row').forEach(b=>{b.classList.remove('playing');b.querySelector('.voice-play').textContent='▶'});
    $('#voiceNow').textContent=t('voiceLoading');
    try{
      const url=await getVoiceUrl(id);
      if(audio.src!==url){audio.src=url;audio.load();}
      state.playing=id;btn.classList.add('playing');btn.querySelector('.voice-play').textContent='❚❚';$('#voiceNow').textContent=btn.querySelector('.voice-name').textContent;
      await audio.play();
    }catch(e){console.error(e);$('#voiceNow').textContent=t('voiceError');state.playing=null;}
  });
  audio.onended=()=>{const b=$(`.voice-row[data-id="${state.playing}"]`);if(b){b.classList.remove('playing');b.querySelector('.voice-play').textContent='▶'}state.playing=null};
  audio.onpause=()=>{const b=$(`.voice-row[data-id="${state.playing}"]`);if(b)b.querySelector('.voice-play').textContent='▶'};
  audio.onplay=()=>{const b=$(`.voice-row[data-id="${state.playing}"]`);if(b)b.querySelector('.voice-play').textContent='❚❚'};
};