(()=>{
  const strip=document.querySelector('#monthStrip');
  const year=document.querySelector('#yearFilter');
  const month=document.querySelector('#monthFilter');
  if(!strip||!year||!month)return;

  function selectedMonth(){
    return year.value&&month.value?`${year.value}-${month.value}`:'';
  }

  function syncMonthChip(){
    const selected=selectedMonth();
    strip.querySelectorAll('.month-chip').forEach(btn=>{
      const active=(btn.dataset.month||'')===selected;
      btn.classList.toggle('active',active);
      btn.setAttribute('aria-pressed',active?'true':'false');
    });
  }

  strip.addEventListener('click',event=>{
    const btn=event.target.closest('.month-chip');
    if(!btn)return;
    // app.js updates the year/month selects in the button's onclick handler.
    queueMicrotask(syncMonthChip);
  });

  year.addEventListener('change',syncMonthChip);
  month.addEventListener('change',syncMonthChip);

  const reset=document.querySelector('#resetFilters');
  if(reset)reset.addEventListener('click',()=>queueMicrotask(syncMonthChip));

  // app.js rebuilds the month strip when the language/archive data changes.
  new MutationObserver(()=>queueMicrotask(syncMonthChip)).observe(strip,{childList:true});
  syncMonthChip();
})();
