(()=>{
const css=`
#archiveLead{display:none!important}
.schedule-tools,.info-filters{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 18px}
.schedule-filter,.info-filter{border:1px solid var(--line);background:var(--panel);color:var(--muted);border-radius:999px;padding:7px 13px;font:inherit;font-size:13px;font-weight:850;cursor:pointer}
.schedule-filter.active,.info-filter.active{background:#e8edf2;color:#080a0d;border-color:#e8edf2}
.schedule-page .schedule-list{display:grid;gap:10px}
.info-list{border-top:1px solid var(--line)}
.info-item{border:0;border-bottom:1px solid var(--line);border-radius:0;background:transparent;overflow:visible;padding:0}
.info-item summary{list-style:none;cursor:pointer;padding:18px 4px;position:relative}
.info-item summary::-webkit-details-marker{display:none}
.info-item summary:after{content:'＋';position:absolute;right:4px;top:17px;color:var(--muted);font-size:20px;line-height:1}
.info-item[open] summary:after{content:'−'}
.info-meta{display:flex;gap:10px;align-items:center;color:var(--muted);font-size:12px}
.info-type{color:var(--accent2);font-weight:900}
.info-item h3{margin:7px 36px 0 0;font-size:18px;line-height:1.5}
.info-body{padding:0 4px 20px;color:#d9e0e7;border-top:0}
.info-body p{white-space:pre-wrap;margin:0 0 12px;line-height:1.75}
.info-body a{color:var(--accent2);font-weight:800;text-decoration:none}
.voice-transcript{margin-top:16px;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#0b0e13}
.voice-transcript.hidden{display:none!important}
.voice-transcript-row{padding:15px 17px}
.voice-transcript-row+.voice-transcript-row{border-top:1px solid var(--line)}
.voice-transcript-label{font-size:11px;font-weight:950;letter-spacing:.08em;color:var(--muted);margin-bottom:6px}
.voice-transcript-text{white-space:pre-wrap;font-size:15px;line-height:1.75}
.voice-transcript-row.ko{background:#122034}
.voice-transcript-row.ko .voice-transcript-label{color:#8ecbff}
@media(max-width:720px){.info-item h3{font-size:16px}.voice-transcript-row{padding:13px}}
`;
const style=document.createElement('style');style.textContent=css;document.head.appendChild(style);

window.informationHtml=function(p,L){
 const items=(p.information||[]).slice().sort((a,b)=>(b.date||'').localeCompare(a.date||''));
 const cats=['ALL','Media','Live','Other'];
 const filters=`<div class="info-filters">${cats.map((c,i)=>`<button type="button" class="info-filter${i?'':' active'}" data-info-cat="${c}">${c}</button>`).join('')}</div>`;
 const infos=items.map(x=>`<details class="info-item" data-info-type="${esc(x.type||'Other')}"><summary><div class="info-meta"><span class="info-type">${esc(x.type||'Other')}${x.subtype?` / ${esc(x.subtype)}`:''}</span><time>${esc(x.date||'')}</time></div><h3>${esc(x['title_'+L]||x.title_ja||'')}</h3></summary><div class="info-body"><p>${esc(x['body_'+L]||x.body_ja||'')}</p>${x.url?`<a href="${esc(x.url)}" target="_blank" rel="noopener">${t('detail')} ↗</a>`:''}</div></details>`).join('');
 const rel=(p.related_topics||[]).map(x=>`<a class="topic-card" href="${esc(x.url)}" target="_blank" rel="noopener"><time>${esc(x.date||'')}</time><strong>${esc(x['title_'+L]||x.title_ja||'')}</strong><span>↗</span></a>`).join('');
 return `<section class="information-section"><div class="section-heading"><div class="eyebrow">INFORMATION</div><h2>${t('information')}</h2></div>${filters}<div class="info-list">${infos}</div>${rel?`<div class="related-block"><h3>${t('related')}</h3><div class="topic-list">${rel}</div></div>`:''}</section>`;
};
window.wireInfoFilters=function(){
 $$('.info-filter').forEach(btn=>btn.onclick=()=>{const c=btn.dataset.infoCat;$$('.info-filter').forEach(x=>x.classList.toggle('active',x===btn));$$('.info-item').forEach(x=>{x.hidden=c!=='ALL'&&x.dataset.infoType!==c});});
};

let transcriptPromise=null;
function getVoiceTranscripts(){
 if(!transcriptPromise) transcriptPromise=fetch('data/voice-transcripts.json',{cache:'no-store'}).then(r=>r.ok?r.json():{}).catch(()=>({}));
 return transcriptPromise;
}
window.voiceTranscriptHtml=function(){return `<div id="voiceTranscript" class="voice-transcript hidden"><div class="voice-transcript-row"><div class="voice-transcript-label">日本語</div><div id="voiceTextJa" class="voice-transcript-text"></div></div><div class="voice-transcript-row ko"><div class="voice-transcript-label">한국어</div><div id="voiceTextKo" class="voice-transcript-text"></div></div></div>`};
window.wireVoiceTranscript=function(){
 $$('.voice-row').forEach(btn=>btn.addEventListener('click',async()=>{
   const box=$('#voiceTranscript'); if(!box)return;
   const data=await getVoiceTranscripts(); const v=data[btn.dataset.id]||{};
   $('#voiceTextJa').textContent=v.ja||''; $('#voiceTextKo').textContent=v.ko||'';
   box.classList.toggle('hidden',!(v.ja||v.ko));
 }));
};

window.renderProfile=function(){
 const p=state.profile;if(!p)return;const L=state.lang;
 const fields=(p.fields||[]).map(f=>`<div class="profile-field"><dt>${esc(f['label_'+L]||f.label_ja||'')}</dt><dd>${esc(f['value_'+L]||f.value_ja||'')}</dd></div>`).join('');
 $('#profileView').innerHTML=`<section class="profile-hero">${portraitHtml()}<div class="profile-copy"><div class="eyebrow">${esc(p['affiliation_'+L]||p.affiliation_ja||'')}</div><h1>${esc(p['name_'+L]||p.name_ja||'')}</h1><p class="romanized">${esc(p.romanized||'')}</p><span class="role-chip">${esc(p['occupation_'+L]||p.occupation_ja||'')}</span><a class="external-btn" href="${esc(p.source_url)}" target="_blank" rel="noopener">${t('openOfficial')}</a></div></section><dl class="profile-grid">${fields}</dl><section class="voice-section"><div class="section-heading"><div class="eyebrow">VOICE SAMPLE</div><h2>${t('voice')}</h2></div>${voiceHtml(p.voice_samples||[],L)}${voiceTranscriptHtml()}</section>${informationHtml(p,L)}`;
 loadPortrait();wireVoice();wireVoiceTranscript();wireInfoFilters();
};

window.renderSchedule=function(){
 const p=state.profile;if(!p)return;const L=state.lang;
 const all=(p.upcoming||[]).slice().filter(x=>!x.date||x.date>=new Date().toISOString().slice(0,10)).sort((a,b)=>(a.date||'').localeCompare(b.date||''));
 const card=x=>`<article class="schedule-card ${esc(x.kind||'event')}" data-kind="${esc(x.kind||'event')}"><div class="schedule-kicker">${x.kind==='broadcast'?t('broadcast'):t('event')}</div><div class="schedule-date">${esc(x['date_label_'+L]||x.date||'')}</div><h3>${esc(x['title_'+L]||x.title_ja||'')}</h3><p>${esc(x['detail_'+L]||x.detail_ja||'')}</p>${x.url?`<a href="${esc(x.url)}" target="_blank" rel="noopener">${t('detail')} ↗</a>`:''}</article>`;
 $('#scheduleView').innerHTML=`<section class="schedule-page"><div class="archive-hero"><div><div class="eyebrow">SCHEDULE</div><h1>${t('upcoming')}</h1></div></div><div class="schedule-tools"><button class="schedule-filter active" data-kind="all">${t('all')}</button><button class="schedule-filter" data-kind="event">${t('events')}</button><button class="schedule-filter" data-kind="broadcast">${t('broadcasts')}</button></div><div class="schedule-list">${all.length?all.map(card).join(''):`<div class="schedule-empty">${t('noSchedule')}</div>`}</div></section>`;
 $$('.schedule-filter').forEach(btn=>btn.onclick=()=>{const k=btn.dataset.kind;$$('.schedule-filter').forEach(x=>x.classList.toggle('active',x===btn));$$('.schedule-card').forEach(x=>x.hidden=k!=='all'&&x.dataset.kind!==k);});
};
})();