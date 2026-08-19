(async()=>{
  try{
    const m=await fetch('data/manifest.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error(`manifest ${r.status}`);return r.json()});
    const files=m.archive_parts||[];
    if(!files.length)throw Error('archive parts missing');
    const [parts,mediaMap]=await Promise.all([
      Promise.all(files.map(u=>fetch(u,{cache:'no-store'}).then(r=>{if(!r.ok)throw Error(`${u} ${r.status}`);return r.text()}))),
      fetch('data/media-map.json',{cache:'no-store'}).then(r=>r.ok?r.json():{}).catch(()=>({}))
    ]);
    const b64=parts.join('').replace(/\s/g,'');
    const raw=Uint8Array.from(atob(b64),c=>c.charCodeAt(0));
    if(!('DecompressionStream' in window))throw Error('gzip unsupported');
    const stream=new Blob([raw]).stream().pipeThrough(new DecompressionStream('gzip'));
    const posts=JSON.parse(await new Response(stream).text());
    if(!Array.isArray(posts)||!posts.length)throw Error(`archive count ${posts?.length||0}`);
    for(const p of posts){
      const synced=mediaMap?.[String(p.id)];
      if(Array.isArray(synced)&&synced.length){p.media=synced;p.has_media=true;}
      else p.has_media=!!p.media?.length;
    }
    state.manifest=m;
    state.posts=posts;
    document.querySelector('#archiveTotal').textContent=String(posts.length);
    populateFilters();
    applyFilters();
  }catch(e){
    console.error('full archive load failed',e);
    const feed=document.querySelector('#feed');
    if(feed)feed.insertAdjacentHTML('afterbegin',`<div class="fatal">X 아카이브 전체 데이터를 불러오지 못했습니다: ${esc(e.message)}</div>`);
  }
})();