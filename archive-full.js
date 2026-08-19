(async()=>{
  try{
    const m=await fetch('data/manifest.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error(`manifest ${r.status}`);return r.json()});
    if(!m.archive_file)return;
    const b64=(await fetch(m.archive_file,{cache:'no-store'}).then(r=>{if(!r.ok)throw Error(`archive ${r.status}`);return r.text()})).replace(/\s/g,'');
    const raw=Uint8Array.from(atob(b64),c=>c.charCodeAt(0));
    if(!('DecompressionStream' in window))throw Error('이 브라우저가 압축 아카이브 해제를 지원하지 않습니다. 최신 브라우저로 열어주세요.');
    const stream=new Blob([raw]).stream().pipeThrough(new DecompressionStream('gzip'));
    const posts=JSON.parse(await new Response(stream).text());
    if(!Array.isArray(posts)||posts.length!==455)throw Error(`archive count ${posts?.length||0}`);
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
