/* AmdQuant v10. AMD ROCm is required for SB. No simulated hardware or timing. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const dictionary = window.AMDQUANT_I18N;
  const store = {get(k) {try{return localStorage.getItem(k);}catch{return null;}},set(k,v){try{localStorage.setItem(k,v);}catch{}},remove(k){try{localStorage.removeItem(k);}catch{}}};
  let language = store.get('amdquant-language') || 'en';
  if (!dictionary[language]) language = 'en';
  let info=null, selected=null, result=null, active=null, pollTimer=null, stage='checking', category='channels', ownMode=false, validating=false;
  let visitPending=false;
  const drafts={};
  const key='amdquant-qubo-active-v10';
  const t = k => dictionary[language][k] || dictionary.en[k] || k;
  const esc = v => String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const number = (v,d=2) => Number(v).toLocaleString(language,{maximumFractionDigits:d});
  const ms = v => v < 1000 ? `${number(v,1)} ms` : `${number(v/1000,2)} s`;
  const errorText = code => t('error_'+code) === 'error_'+code ? t('error_run_failed') : t('error_'+code);
  function status(next) {stage=next;renderConnectionStatus();}
  function renderConnectionStatus() {
    const connecting=!info?.ready;
    $('runStatus').classList.toggle('connecting',connecting);
    $('runStatus').setAttribute('aria-busy',String(connecting));
    if(connecting){
      if(!$('runStatus').querySelector('.connection-spinner'))$('runStatus').innerHTML='<span class="connection-spinner" aria-hidden="true"></span><span>Connecting…</span>';
    }else{
      $('runStatus').textContent=dictionary.en[stage]?t(stage):errorText(stage);
    }
  }
  function busy(value) {
    $('executeButton').disabled=value || !info?.ready || !info?.public;
    $('question').disabled=value;
    document.querySelectorAll('#sampleButtons button,#categoryTabs button,#templateButton,#syntheticButton,#validateButton').forEach(b=>b.disabled=value);
    $('executeButton').disabled=value || validating || !info?.ready || !info?.public;
    $('cancelButton').hidden=!value || !active;
  }
  function showView(technical) {
    $('compareView').hidden=technical; $('technicalView').hidden=!technical;
    $('technicalButton').setAttribute('aria-pressed',String(technical));
  }
  function currentCategory(){return info?.categories?.find(c=>c.id===category);}
  function updateDescription(){
    const cat=currentCategory();if(!cat)return;
    let generated=false;
    if(ownMode){try{const d=JSON.parse($('question').value);generated=!!d.variant&&d.variant!=='standard';}catch{}}
    $('categoryDescription').textContent=(ownMode&&!generated&&cat.own_description?cat.own_description:cat.description)[language];
  }
  function clearValidation(){$('inputError').hidden=true;$('validationSuccess').hidden=true;}
  function showError(code,issues=[]){
    $('validationSuccess').hidden=true;$('inputError').hidden=false;
    $('inputError').innerHTML=`<strong>${esc(errorText(code))}</strong>${issues.length?`<ul>${issues.map(x=>`<li>${esc(x.field)}: ${esc(t('validation_'+x.code)!=='validation_'+x.code?t('validation_'+x.code):t('validation_generic'))}</li>`).join('')}</ul>`:''}`;
  }
  function setExample(p){
    if(ownMode)drafts[category]=$('question').value;
    ownMode=false;selected=p.id;category=p.category;$('question').value=p.prompts[language];
    clearValidation();samples();
  }
  function chooseOwn(){ownMode=true;selected=null;$('question').value=drafts[category]||JSON.stringify(currentCategory().template,null,2);clearValidation();samples();}
  function samples(){
    if(!info?.categories)return;
    $('categoryTabs').replaceChildren();
    for(const cat of info.categories){
      const b=document.createElement('button');b.type='button';b.id='tab-'+cat.id;b.role='tab';
      b.textContent=cat.title[language];b.className=cat.id===category?'active':'';
      b.setAttribute('aria-selected',String(cat.id===category));b.setAttribute('aria-controls','categoryPanel');b.tabIndex=cat.id===category?0:-1;b.disabled=!!active;
      b.addEventListener('click',()=>{if(ownMode)drafts[category]=$('question').value;category=cat.id;ownMode=false;setExample(info.presets.find(p=>p.category===category));});
      b.addEventListener('keydown',event=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(event.key)){event.preventDefault();const tabs=[...$('categoryTabs').children],i=tabs.indexOf(b);const next=event.key==='Home'?0:event.key==='End'?tabs.length-1:(i+(event.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;tabs[next].click();$('categoryTabs').children[next].focus();}});
      $('categoryTabs').append(b);
    }
    const cat=currentCategory();if(!cat)return;
    $('categoryPanel').setAttribute('aria-labelledby','tab-'+category);
    $('categoryTitle').textContent=cat.title[language];
    updateDescription();$('categoryHelp').textContent=cat.help[language];
    $('sampleButtons').replaceChildren();
    info.presets.filter(p=>p.category===category).forEach((p,i)=>{
      const b=document.createElement('button');b.type='button';b.textContent=`Problem ${i+1}`;b.role='tab';
      b.title=p.prompts[language];b.className=p.id===selected?'selected':'';b.setAttribute('aria-selected',String(p.id===selected));b.disabled=!!active;
      b.addEventListener('click',()=>setExample(p));$('sampleButtons').append(b);
    });
    const own=document.createElement('button');own.type='button';own.role='tab';own.textContent=t('ownProblem');own.className='own-tab'+(ownMode?' selected':'');own.disabled=!!active;own.setAttribute('aria-selected',String(ownMode));own.addEventListener('click',chooseOwn);$('sampleButtons').append(own);
    const preset=info.presets.find(p=>p.id===selected);
    $('exampleExplanation').textContent=ownMode?t('ownExplanation'):(preset?.explanation?.[language]||'');
    $('exampleScale').textContent=ownMode?'':`${number(preset?.spec.size||preset?.spec.matrix?.length,0)} ${t('variables')} · ${t('synthetic')}`;
    document.querySelector('.problem-notes').hidden=ownMode;
    $('inputGuide').hidden=!ownMode;$('validateButton').hidden=!ownMode;$('syntheticButton').hidden=!cat.synthetic;
    $('question').readOnly=!ownMode;$('question').rows=ownMode?8:3;$('question').classList.toggle('json-input',ownMode);
  }
  function translate() {
    document.documentElement.lang=language;
    document.querySelectorAll('[data-i18n]').forEach(el=>el.textContent=t(el.dataset.i18n));
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el=>el.placeholder=t(el.dataset.i18nPlaceholder));
    document.querySelectorAll('[data-lang]').forEach(el=>{
      el.classList.toggle('active',el.dataset.lang===language);
      el.setAttribute('aria-pressed',String(el.dataset.lang===language));
    });
    if(selected&&info&&!active){const p=info.presets.find(p=>p.id===selected);if(p)$('question').value=p.prompts[language];}
    samples(); status(stage); renderHardware(); if(result)render(result);else if(!active){$('resultTitle').textContent=t('resultsTitle');}
  }
  function renderHardware() {
    renderConnectionStatus();
    if(!info)return;
    const h=info.hardware || {};
    $('hardwareStatus').textContent=info.ready?`v${info.version} · Traditional: CPU · Simulated Bifurcation: ${h.sb_device_name} · AMD ROCm ${h.rocm_version}`:t('gpuDisconnected');
    document.querySelector('.runtime-dot').classList.toggle('unavailable', !info.ready);
    $('technicalHardware').textContent=JSON.stringify(h,null,2);
    renderVisitNotice();
  }
  function renderVisitNotice() {
    const state=info?.visit_alert;
    $('scopeNote').classList.toggle('gpu-alert-visible',!!info&&!info.ready);
    $('scopeNote').textContent=t(!info||info.ready?'scope':state==='accepted'?'alertAccepted':state==='checking'?'alertChecking':state==='failed'?'alertFailed':'alertOffline');
  }
  async function reportVisit() {
    if(visitPending||!info?.public||info.ready)return;
    visitPending=true;
    try{
      const data=await api('/api/public/visit',{method:'POST',headers:{'X-Amdquant-Visit':'1'},body:'{}'});
      if(info)info.visit_alert=data.visit_alert;
      renderVisitNotice();
    }catch{/* Retry on the next successful info refresh; never claim it was sent. */}
    finally{visitPending=false;}
  }
  function solution(engine) {
    const d=engine.decoded;
    const channels=result?.problem.spec.kind==='channels';
    const variant=result?.problem.spec.variant||'standard';
    const feasibleLabel=variant==='coupled'?'partitionValid':variant==='two_pools'?'assignmentValid':variant!=='standard'?'binaryValid':channels?'validChannelPlan':d.feasible?'feasible':'infeasible';
    const metrics=Object.entries(d.metrics).map(([k,v])=>`<div>${esc(t(k))}: <strong>${esc(number(v,3))}</strong></div>`).join('');
    const shown=d.selected.slice(0,12);
    const items=shown.map(v=>typeof v==='object'?`${t('worker')} ${v.worker} → ${t('task')} ${v.task}`:v).join(', ');
    const others=d.other_group.slice(0,12);
    const group=d.other_group.length?`<p class="solution-list"><strong>${esc(t(channels?'channel2':'groupB'))}:</strong> ${esc(others.join(', '))}${others.length<d.other_group.length?'…':''}</p>`:'';
    return `<span class="feasibility ${d.feasible?'':'invalid'}">${esc(t(feasibleLabel))}</span>${metrics}<p class="solution-list"><strong>${esc(t(channels?'channel1':d.other_group.length?'groupA':'selected'))}:</strong> ${esc(items||'—')}${shown.length<d.selected.length?'…':''}</p>${group}${channels?`<p class="output-note">${esc(t('fullPlanNote'))}</p>`:''}`;
  }
  function render(r) {
    $('results').hidden=false;
    const p=r.problem, c=r.engines.traditional, q=r.engines.quantum;
    const channels=p.spec.kind==='channels';
    const large=(channels&&p.data_source==='synthetic')||(p.spec.variant&&p.spec.variant!=='standard');
    $('classicalProfile').textContent=large?'CPU · 8 reads × 200 sweeps · 1 thread':'CPU · 32 reads × 1,000 sweeps · 1 thread';
    $('gpuProfile').textContent=large?'AMD GPU · 128 agents × 1,000 steps':'AMD GPU · 32 agents · max 10,000 steps · early stopping';
    $('planButton').hidden=!channels;$('planButton').disabled=!c||!q;
    $('resultTitle').textContent=t('resultsTitle')+' · '+p.variables+' '+t('variables');
    const source=t(p.data_source==='synthetic'?'synthetic':'userData');
    const adapter=r.input_adapter || {source:'preset',elapsed_ms:0};
    $('problemSummary').textContent=source+' · '+(p.spec.variant&&p.spec.variant!=='standard'?p.data.pair_interactions.toLocaleString(language)+' '+t('pairInteractions'):t('sameInput')) ;
    for(const name of ['traditional','quantum']) {
      const e=r.engines[name];
      $('download-'+name).hidden=!e;
      if(!e){$('answer-'+name).innerHTML=`<div class="engine-waiting">${esc(t('engineRunning'))}</div>`;$('metrics-'+name).textContent='';continue;}
      $('answer-'+name).innerHTML=`<div class="engine-ready">${esc(t('engineFinished'))}</div>`+solution(e);
      const gap=e.optimality_gap_percent!==null?`${number(e.optimality_gap_percent,3)}%`:e.optimality_gap_absolute!==null?`${number(e.optimality_gap_absolute,6)} (${t('absoluteError')})`:t('unknown');
      $('metrics-'+name).innerHTML=`<div class="metric-grid"><div><span class="metric-value">${esc(ms(e.solver_ms))}</span><span class="metric-label">${esc(t('solverTime'))}</span></div><div><span class="metric-value">${esc(number(e.energy,5))}</span><span class="metric-label">${esc(t('objective'))}</span></div><div><span class="metric-value">${esc(gap)}</span><span class="metric-label">${esc(t('gap'))}</span></div></div><p class="output-note">${esc(t('median'))}: ${esc(ms(e.median_ms))} · ${esc(t(e.at_proven_optimum?'proven':'bestFound'))}</p>${e.trials.some(x=>x.warnings?.length)?`<p class="output-note warning-text">${esc(t('warning'))}</p>`:''}`;
    }
    if(!r.complete||!r.comparison){
      $('comparisonSummary').textContent=t('waitingComparison');$('timingChart').replaceChildren();$('exportButton').disabled=true;
      $('evidenceContent').textContent=t('waitingVerification');return;
    }
    const ratio=r.comparison.sb_speed_ratio;
    const faster=ratio>=1?'AI ADM Quantum micro':'Traditional AI micro';
    const multiple=ratio>=1?ratio:1/ratio;
    const note=!r.comparison.both_feasible?'invalidQuality':r.comparison.same_objective?'equalQuality':'differentQuality';
    const difference=r.comparison.sb_objective_difference_percent;
    const quality=Number.isFinite(difference)?`<p>${esc(t('qualityDelta'))}: <strong>${esc(number(difference,4))}%</strong> · ${esc(t('negativeBetter'))}</p>`:'';
    $('comparisonSummary').innerHTML=`<strong>${esc(faster)} · ${esc(number(multiple,2))}× ${esc(t('faster'))}</strong><p>${esc(t(note))}</p>${quality}`;
    const max=Math.max(c.solver_ms,q.solver_ms,1);
    $('timingChart').innerHTML=`<svg viewBox="0 0 800 110" role="img" aria-label="${esc(t('solverTime'))}"><text x="0" y="19" fill="#5871a8" font-size="12">Traditional</text><rect x="125" y="4" width="${Math.max(2,c.solver_ms/max*540)}" height="22" rx="5" fill="#a8bdeb"/><text x="690" y="20" fill="#123782" font-size="12">${esc(ms(c.solver_ms))}</text><text x="0" y="63" fill="#5871a8" font-size="12">Bifurcation</text><rect x="125" y="48" width="${Math.max(2,q.solver_ms/max*540)}" height="22" rx="5" fill="#073cc9"/><text x="690" y="64" fill="#123782" font-size="12">${esc(ms(q.solver_ms))}</text><text x="125" y="99" fill="#5871a8" font-size="10">${esc(t('solverTime'))}</text></svg>`;
    $('evidenceContent').innerHTML=`<p>${esc(t('reference'))}: ${r.reference.known?esc(number(r.reference.energy,6)):esc(t('unknown'))} · ${esc(r.reference.method)}</p><p>SHA-256: <code>${esc(p.sha256)}</code></p><p>${esc(t('data'))}</p><pre>${esc(JSON.stringify(p.data,null,2))}</pre><p>QUBO: ${esc(p.convention)}</p><p>SB: ${esc(r.hardware.sb_device_name)} · PyTorch ${esc(r.hardware.torch_version)} · simulated-bifurcation ${esc(r.hardware.sb_version)} · dwave-samplers ${esc(r.hardware.classical_version)}</p><p>${esc(t('method'))}</p><p>${esc(t('gapNote'))}</p>`;
    $('exportButton').disabled=false;
  }
  async function api(url,options={}) {
    const controller=new AbortController();
    const timer=setTimeout(()=>controller.abort(),20000);
    try{
      const response=await fetch(url,{...options,signal:controller.signal,headers:{'Content-Type':'application/json',...options.headers}});
      const data=await response.json();
      if(!response.ok){const e=new Error(typeof data.detail==='string'?data.detail:data.detail?.code||'run_failed');e.http=response.status;e.issues=data.detail?.issues||[];throw e;}
      return data;
    }finally{clearTimeout(timer);}
  }
  function finish(){active=null;store.remove(key);busy(false);$('retryButton').hidden=true;}
  function accept(job) {
    if(job.partial){result={...job.partial,title:active?.title,question:job.question};render(result);}
    if(job.status==='completed'){
      result={...job.result,title:active?.title,question:job.question}; render(result); finish(); status('completed');
    }else if(job.status==='failed'||job.status==='cancelled'){
      const code=job.error||'cancelled';finish();status(code);if(job.issues?.length)showError(code,job.issues);
      if(result&&!result.complete){$('comparisonSummary').textContent=errorText(code);for(const name of ['traditional','quantum'])if(!result.engines[name])$('answer-'+name).textContent=t('engineStopped');}
    }else{
      status('running'); pollTimer=setTimeout(poll,300);
    }
  }
  async function poll(){
    clearTimeout(pollTimer); if(!active)return;
    $('retryButton').hidden=true;
    try{accept(await api('/api/public/jobs/'+active.id));}
    catch(e){
      if(e.http===404){finish();status('job_expired');}
      else{status('disconnected');$('retryButton').hidden=false;}
    }
  }
  function pending(title){
    $('results').hidden=false;$('resultTitle').textContent=t('resultsTitle');$('problemSummary').replaceChildren();
    for(const name of ['traditional','quantum']){$('answer-'+name).innerHTML=`<div class="engine-waiting">${esc(t('engineRunning'))}</div>`;$('metrics-'+name).replaceChildren();$('download-'+name).hidden=true;}
    $('comparisonSummary').textContent=t('waitingComparison');$('timingChart').replaceChildren();$('evidenceContent').replaceChildren();$('planButton').hidden=true;$('exportButton').disabled=true;
  }
  async function validateQuestion(){
    const question=$('question').value.trim();clearValidation();
    if(ownMode){
      let data;try{data=JSON.parse(question);}catch{showError('invalid_problem_json');return null;}
      if(data?.kind!==category){showError('wrong_category');return null;}
    }
    try{
      const checked=await api('/api/public/validate',{method:'POST',body:JSON.stringify({question})});
      $('validationSuccess').hidden=!ownMode;$('validationSuccess').textContent=t('validData');return checked;
    }catch(e){showError(e.message,e.issues);return null;}
  }
  $('questionForm').addEventListener('submit',async event=>{
    event.preventDefault();if(active||validating)return;
    validating=true;busy(false);const checked=await validateQuestion();validating=false;
    if(!checked){busy(false);return;}if(!info?.ready){busy(false);status('gpu_not_connected');return;}
    const question=$('question').value.trim(),specification=checked.spec;
    const solverSeed=specification.kind==='channels'&&checked.data_source==='synthetic'?1000+(specification.seed%100000)*100:2026;
    const id=crypto.randomUUID(),title=ownMode?currentCategory().title[language]+' · '+t('ownProblem'):question;
    active={id:id.replaceAll('-',''),question,title,category,ownMode,selected};store.set(key,JSON.stringify(active));
    busy(true);status('running');result=null;pending(title);
    try{accept(await api('/api/public/jobs',{method:'POST',body:JSON.stringify({request_id:id,question,seed:solverSeed,language})}));}
    catch(e){
      if(e.http&&e.http>=400&&e.http<600){finish();status(e.message);showError(e.message,e.issues);$('results').hidden=false;}
      else{status('disconnected');$('retryButton').hidden=false;}
    }
  });
  $('question').addEventListener('input',()=>{if(ownMode)drafts[category]=$('question').value;clearValidation();updateDescription();});
  $('validateButton').addEventListener('click',async()=>{if(validating||active)return;validating=true;busy(true);await validateQuestion();validating=false;busy(false);});
  $('templateButton').addEventListener('click',()=>{$('question').value=JSON.stringify(currentCategory().template,null,2);drafts[category]=$('question').value;clearValidation();updateDescription();});
  $('syntheticButton').addEventListener('click',()=>{$('question').value=JSON.stringify(currentCategory().synthetic,null,2);drafts[category]=$('question').value;clearValidation();updateDescription();});
  $('retryButton').addEventListener('click',poll);
  $('cancelButton').addEventListener('click',async()=>{
    if(!active)return;
    try{await api('/api/public/jobs/'+active.id+'/cancel',{method:'POST'});poll();}
    catch{status('disconnected');$('retryButton').hidden=false;}
  });
  $('newQuestion').addEventListener('click',()=>{$('question').focus();});
  $('technicalButton').addEventListener('click',()=>showView($('technicalView').hidden));
  $('backButton').addEventListener('click',()=>showView(false));
  document.querySelector('.brand').addEventListener('click',()=>showView(false));
  document.querySelectorAll('[data-lang]').forEach(b=>b.addEventListener('click',()=>{language=b.dataset.lang;store.set('amdquant-language',language);translate();}));
  $('exportButton').addEventListener('click',()=>{
    if(!result)return;
    const url=URL.createObjectURL(new Blob([JSON.stringify(result,null,2)],{type:'application/json'}));
    const a=document.createElement('a');a.href=url;a.download=`amdquant-qubo-${result.problem.spec.kind}-${Date.now()}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),5000);
  });
  $('planButton').addEventListener('click',()=>{
    if(!result||result.problem.spec.kind!=='channels')return;
    const c=result.engines.traditional.bits,q=result.engines.quantum.bits;
    const csv='transmitter,cpu_channel,sb_gpu_channel\n'+c.map((value,i)=>`${i+1},${value+1},${q[i]+1}`).join('\n')+'\n';
    const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
    const a=document.createElement('a');a.href=url;a.download=`channel-plan-${c.length}-${result.problem.spec.seed}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),5000);
  });
  document.querySelectorAll('[data-engine]').forEach(button=>button.addEventListener('click',()=>{
    const name=button.dataset.engine,engine=result?.engines?.[name];if(!engine)return;
    const data={schema_version:'amdquant-solution-v10',comparison_complete:!!result.complete,problem:result.problem,hardware:result.hardware,engine:name,result:engine};
    const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));
    const a=document.createElement('a');a.href=url;a.download=`amdquant-${name}-${result.problem.spec.kind}-solution.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),5000);
  }));
  async function refreshInfo() {
    try {
      const data=await api('/api/public/info');
      const wasReady=info?.ready;
      info=data;
      if(!ownMode&&!selected&&!active&&!$('question').value.trim()){
        const preset=data.presets.find(p=>p.id==='p1');
        if(preset)setExample(preset);
      }
      samples();renderHardware();busy(!!active);
      if(!active&&(!result||!data.ready||!wasReady))status(data.ready?(data.public?'ready':'private_mode'):data.error);
      void reportVisit();
    } catch {
      info={ready:false,public:true,hardware:{},presets:info?.presets||[],categories:info?.categories||[]};
      renderHardware();busy(!!active);if(!active)status('offline');
    }
  }
  translate();busy(true);
  refreshInfo().then(()=>{
    try{const saved=JSON.parse(store.get(key));if(saved&&/^[a-f0-9]{32}$/.test(saved.id)){active=saved;category=saved.category||'channels';ownMode=!!saved.ownMode;selected=saved.selected||null;$('question').value=saved.question;samples();pending(saved.title||'');busy(true);poll();}}
    catch{store.remove(key);}
  });
  setInterval(()=>{if(!active)refreshInfo();},15000);
})();
