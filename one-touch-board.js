/* one-touch board behaviors — STAGE ONLY, never auto-send */
(function(){
  function toast(msg){
    const t=document.getElementById('toast');
    if(!t) return;
    t.textContent=msg||'Copied';
    t.style.display='block';
    setTimeout(()=>t.style.display='none',1400);
  }
  async function copyText(text){
    try{ await navigator.clipboard.writeText(text); toast('Copied'); }
    catch(e){
      const ta=document.createElement('textarea'); ta.value=text; document.body.appendChild(ta); ta.select();
      document.execCommand('copy'); ta.remove(); toast('Copied');
    }
  }
  function rowData(row){
    return {
      email: row.dataset.email||'',
      subject: row.dataset.subject||'',
      body: row.dataset.body||'',
      mailto: row.dataset.mailto||'',
      tel: row.dataset.tel||'',
      form: row.dataset.form||'',
      primary: row.dataset.primary||''
    };
  }
  function copyDraft(row){
    const d=rowData(row);
    const block=(d.email?('To: '+d.email+'\n'):'')+'Subject: '+d.subject+'\n\n'+d.body;
    copyText(block);
  }
  function openCompose(row){
    const d=rowData(row);
    const modal=document.getElementById('compose-modal');
    if(!modal) return;
    document.getElementById('compose-to').value=d.email||'(no email — use Open form / Copy)';
    document.getElementById('compose-subj').value=d.subject||'';
    document.getElementById('compose-body').textContent=d.body||'';
    const a=document.getElementById('compose-mailto');
    if(d.mailto){ a.href=d.mailto; a.style.display=''; }
    else { a.removeAttribute('href'); a.style.display='none'; }
    modal.classList.add('on');
  }
  function applyFilter(){
    const filters=document.getElementById('filters');
    const mode=filters?((document.querySelector('#filters button.on')||{}).dataset.filter||'all'):'all';
    const srcBtn=document.querySelector('#source-filters button.on');
    const srcMode=(srcBtn&&srcBtn.dataset.filter)||'src_all';
    const qEl=document.getElementById('q');
    const q=(qEl&&qEl.value||'').trim().toLowerCase();
    let n=0;
    document.querySelectorAll('#tbody tr.row').forEach(row=>{
      const views=(row.dataset.views||'').split(/\s+/).filter(Boolean);
      const camps=(row.dataset.campaigns||'').split(/\s+/).filter(Boolean);
      let show = mode==='all' || views.indexOf(mode)!==-1 || camps.indexOf(mode)!==-1;
      if(show && srcMode && srcMode!=='src_all'){
        const want=srcMode.replace(/^src_/,'');
        const got=row.dataset.sourceLabel||'';
        if(got!==want) show=false;
      }
      if(show && q){
        const blob=row.dataset.search||'';
        show = blob.indexOf(q)!==-1;
      }
      row.style.display=show?'':'none';
      if(show) n++;
    });
    const note=document.getElementById('view-note');
    if(note){
      const srcNote=(srcMode && srcMode!=='src_all')?(' · source '+srcMode.replace(/^src_/,'')):'';
      note.textContent='Showing '+n+(mode!=='all'?(' · filter '+mode):'')+srcNote+(q?(' · search "'+q+'"'):'')+' · STAGE ONLY';
    }
  }
  const tbody=document.getElementById('tbody');
  if(tbody){
    tbody.addEventListener('click', function(e){
      const actionEl=e.target.closest('[data-action]');
      if(!actionEl) return;
      const row=actionEl.closest('tr.row');
      if(!row) return;
      const action=actionEl.getAttribute('data-action');
      if(action==='copy-draft'){ e.preventDefault(); e.stopPropagation(); copyDraft(row); return; }
      if(action==='compose'){ e.preventDefault(); e.stopPropagation(); openCompose(row); return; }
      if(action==='mailto' || action==='tel' || action==='form'){ e.stopPropagation(); return; }
    });
  }
  const filters=document.getElementById('filters');
  if(filters){
    filters.addEventListener('click', function(e){
      const btn=e.target.closest('button[data-filter]');
      if(!btn) return;
      filters.querySelectorAll('button').forEach(b=>b.classList.remove('on'));
      btn.classList.add('on');
      applyFilter();
    });
  }
  const srcFilters=document.getElementById('source-filters');
  if(srcFilters){
    srcFilters.addEventListener('click', function(e){
      const btn=e.target.closest('button[data-filter]');
      if(!btn) return;
      srcFilters.querySelectorAll('button').forEach(b=>b.classList.remove('on'));
      btn.classList.add('on');
      applyFilter();
    });
  }
  const q=document.getElementById('q');
  if(q) q.addEventListener('input', applyFilter);
  const close=document.getElementById('compose-close');
  if(close) close.onclick=function(){ document.getElementById('compose-modal').classList.remove('on'); };
  const modal=document.getElementById('compose-modal');
  if(modal) modal.onclick=function(e){ if(e.target.id==='compose-modal') e.target.classList.remove('on'); };
  const copyBtn=document.getElementById('compose-copy');
  if(copyBtn) copyBtn.onclick=function(){
    const t='Subject: '+document.getElementById('compose-subj').value+'\n\n'+document.getElementById('compose-body').textContent;
    copyText(t);
  };
  const mailtoBtn=document.getElementById('compose-mailto');
  if(mailtoBtn) mailtoBtn.addEventListener('click', function(e){
    const subj=document.getElementById('compose-subj').value||'';
    const body=document.getElementById('compose-body').textContent||'';
    const to=document.getElementById('compose-to').value||'';
    if(!to || to.indexOf('@')<0){ e.preventDefault(); toast('No email — use Open form'); return; }
    this.href='mailto:'+encodeURIComponent(to).replace(/%40/g,'@')+'?subject='+encodeURIComponent(subj)+'&body='+encodeURIComponent(body);
  });
  // initial note count
  if(document.getElementById('tbody')) applyFilter();
})();
