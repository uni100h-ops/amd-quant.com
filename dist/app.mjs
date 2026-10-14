import {translations,translate,samples} from './i18n.mjs';
const $=id=>document.getElementById(id),variants=['classical','hybrid'];
let language='en';
try{const saved=localStorage.getItem('amdquant.language');if(Object.hasOwn(translations,saved))language=saved;}catch{}
let info=null,lastComparison=null,lastJob=null,qwenReport=null,active=null,pollTimer=null;
let busy=false,ready=false,status='loading',toastTimer;
const t=(key,values)=>translate(language,key,values);
const number=(n,places=1)=>new Intl.NumberFormat(language,{minimumFractionDigits:places,maximumFractionDigits:places}).format(n);
const ms=n=>n<1000?number(n,n<10?2:1)+' ms':n<60000?number(n/1000,2)+' s':number(n/60000,1)+' min';
async function call(action,data){
 const response=await fetch('/api/public/'+action,{method:data?'POST':'GET',headers:data?{'Content-Type':'application/json'}:{},...(data?{body:JSON.stringify(data)}:{}),signal:AbortSignal.timeout(35000)});
 if(!response.ok){const error=new Error('api');error.status=response.status;throw error;}return response.json();
}
function errorText(e){if(e.status===429)return t('busyError');if(e.status===422)return t('promptTooLong');if(e.status===503||e.message==='unavailable')return t('unavailable');return t('networkError');}
function amdFailureText(job){const code=job?.amd_diagnostic?.http_status;if(Number.isInteger(code)&&code>=300&&code<=599)return t('amdHttpError',{status:code});return t(job?.error_code==='amd_quota'?'amd_quota':'amdError');}
function saveActive(){try{if(active)localStorage.setItem('amdquant.active.v3',JSON.stringify(active));else localStorage.removeItem('amdquant.active.v3');}catch{}}
function toast(message){clearTimeout(toastTimer);$('toast').textContent=message;$('toast').hidden=false;toastTimer=setTimeout(()=>$('toast').hidden=true,6500);}
function setBusy(value){busy=value;document.querySelectorAll('#question,#newQuestion,#sampleButtons button').forEach(el=>el.disabled=value);$('executeButton').disabled=value||!ready;$('executeLabel').textContent=t(value?'running':'execute');$('cancelButton').hidden=!value||!active?.job_id;}
function renderStatus(){
 let text=t(status);
 if(status==='running'){const stage=lastJob?.stage||'';text=t(stage==='amd_normalizing'?'amdNormalizing':stage==='ibm_running'?'ibmRunning':stage.startsWith('ibm_')?'ibmWaiting':'measuring');}
 if(status==='failed'&&lastJob?.error_code==='daily_limit')text=t('dailyLimit');
 if(status==='failed'&&lastJob?.error_code?.startsWith('amd_'))text=amdFailureText(lastJob);
 if(status==='failed'&&lastJob?.error_code==='interrupted')text=t('interrupted');
 $('runStatus').textContent=text;
}
function renderSamples(){const box=$('sampleButtons');box.replaceChildren();for(const [label,prompt]of samples[language]||samples.en){const button=document.createElement('button');button.type='button';button.textContent=label;button.disabled=busy;button.onclick=()=>{$('question').value=prompt;invalidate();$('question').focus();};box.append(button);}}
function renderMetrics(variant,r){
 const box=$('metrics-'+variant);box.replaceChildren();const value=document.createElement('strong'),label=document.createElement('span');
 value.className='metric-value';value.textContent=ms(r.end_to_end_ms??r.elapsed_ms);label.className='metric-label';label.textContent=t('totalTime');box.append(value,label);
 const detail=document.createElement('span');detail.className='model-only';detail.textContent=t('modelTime',{time:ms(r.elapsed_ms)});box.append(detail);
 if(r.stop_reason==='max_tokens'){const note=document.createElement('p');note.className='output-note';note.textContent=t('outputCap');box.append(note);}
}
function renderAnswer(variant,r){$('answer-'+variant).classList.remove('pending');$('answer-'+variant).textContent=r.text||t('emptyAnswer');renderMetrics(variant,r);}
function renderNormalization(){const amd=lastJob?.amd||lastComparison?.amd;$('normalization').hidden=!amd?.normalized_prompt;if(!amd)return;$('normalizedPrompt').textContent=amd.normalized_prompt||'';$('amdTiming').textContent=t('amdTime',{time:ms(amd.elapsed_ms)});}
function renderComparison(){
 if(!lastComparison)return;const r=lastComparison,c=r.classical,h=r.hybrid;$('resultTitle').textContent=r.prompt;variants.forEach(v=>renderAnswer(v,r[v]));
 const box=$('comparisonSummary');box.replaceChildren();const headline=document.createElement('strong'),note=document.createElement('p');
 const ct=c.end_to_end_ms,ht=h.end_to_end_ms,difference=Math.abs(ct-ht),close=difference<.5||difference/Math.max(ct,ht)<.05;
 headline.textContent=close?t('closeTimes'):t('winner',{model:$(ht<ct?'hybridTitle':'classicalTitle').textContent,ratio:number(Math.max(ct,ht)/Math.max(.001,Math.min(ct,ht)),2)});
 note.textContent=(c.text===h.text?t('sameAnswer'):t('compareAnswers'))+' '+t('qualityNote');box.append(headline,note);
}
function renderEvidence(){const jobs=lastJob?.ibm_jobs||[];const done=lastComparison?.physical_quantum_hardware===true;$('quantumEvidence').textContent=done?t('physicalVerified',{backend:lastComparison.ibm_backend}):jobs.length?t('hardwarePending',{backend:jobs[0].backend||info?.quantum?.backend||'IBM'}):'';const list=$('ibmJobList');list.replaceChildren();for(const job of jobs){if(!job.ibm_job_id)continue;const item=document.createElement('li');item.textContent=job.ibm_job_id+' · '+job.status;list.append(item);}$('evidenceDetails').hidden=jobs.length===0;}
function renderBenchmark(){if(!qwenReport)return;$('qwenRows').replaceChildren();for(const [label,key,format]of [['lossRow','answer_nll',x=>number(x,4)],['latencyRow','median_ms',ms]]){const row=document.createElement('tr');for(const cell of [t(label),...['base','classical','hybrid'].map(v=>format(qwenReport.results[v][key]))]){const td=document.createElement('td');td.textContent=cell;row.append(td);}$('qwenRows').append(row);}}
function setLanguage(next){
 if(!Object.hasOwn(translations,next))return;language=next;document.documentElement.lang=language;
 document.querySelectorAll('[data-i18n]').forEach(el=>el.textContent=t(el.getAttribute('data-i18n')));document.querySelectorAll('[data-i18n-placeholder]').forEach(el=>el.placeholder=t(el.getAttribute('data-i18n-placeholder')));
 document.querySelectorAll('[data-lang]').forEach(el=>{const chosen=el.getAttribute('data-lang')===language;el.classList.toggle('active',chosen);el.setAttribute('aria-pressed',String(chosen));});
 renderSamples();renderStatus();renderNormalization();renderComparison();renderEvidence();renderBenchmark();setBusy(busy);
 try{localStorage.setItem('amdquant.language',language);}catch{}
}
function showView(){const technical=location.hash==='#technical';$('technicalView').hidden=!technical;$('compareView').hidden=technical;$('technicalButton').setAttribute('aria-pressed',String(technical));document.title='AmdQuant — '+t(technical?'technicalData':'title');}
function navigate(technical){location.hash=technical?'technical':'compare';window.scrollTo({top:0,behavior:'auto'});}
function invalidate(){lastComparison=null;lastJob=null;$('results').hidden=true;$('normalization').hidden=true;$('exportButton').disabled=true;$('comparisonSummary').replaceChildren();renderEvidence();if(!busy){status=ready?'ready':'unavailable';renderStatus();}}
function pendingView(prompt){$('results').hidden=false;$('resultTitle').textContent=prompt;for(const v of variants){$('answer-'+v).textContent=t('computing');$('answer-'+v).classList.add('pending');$('metrics-'+v).replaceChildren();}}
function applyJob(job){
 lastJob=job;$('results').hidden=false;$('resultTitle').textContent=job.prompt||active?.prompt||'';
 if(job.classical)renderAnswer('classical',job.classical);
 if(job.hybrid_partial){$('answer-hybrid').textContent=job.hybrid_partial.text+'\n\n'+t('partial');}
 $('exportButton').disabled=false;status=job.status==='queued'||job.status==='running'?'running':job.status==='completed'?'complete':job.status;
 if(job.status==='completed'){
  const r=job.result;if(r?.amd_api_call_succeeded!==true||r?.physical_quantum_hardware!==true||!r.ibm_jobs?.length||r.ibm_jobs.some(j=>j.simulator!==false||!j.consumed_by_model))throw new Error('unavailable');
  lastComparison=r;renderComparison();
 }
 if(['completed','unsupported','failed','cancelled'].includes(job.status)){
  active=null;saveActive();setBusy(false);$('retryButton').hidden=true;
  if(job.status==='unsupported')for(const v of variants){$('answer-'+v).classList.remove('pending');$('answer-'+v).textContent=t('unsupported');}
  else if(job.status!=='completed'){
   $('answer-hybrid').classList.remove('pending');$('answer-hybrid').textContent=(job.hybrid_partial?.text?job.hybrid_partial.text+'\n\n':'')+t('noFallback');
   if(!job.classical){$('answer-classical').classList.remove('pending');$('answer-classical').textContent=job.error_code?.startsWith('amd_')?amdFailureText(job):t('failed');}
  }
 }else setBusy(true);
 renderNormalization();renderEvidence();renderStatus();
}
async function poll(){
 if(!active?.job_id)return;
 try{const job=await call('jobs/'+active.job_id);active.missing_since=null;applyJob(job);if(active)pollTimer=setTimeout(poll,5000);}
 catch(e){
  if(e.status===404){
   // Allow the original submission time to reach the provider status checks.
   active.missing_since??=Date.now();saveActive();
   if(Date.now()-active.missing_since<90000){pollTimer=setTimeout(poll,5000);return;}
   active=null;saveActive();status='interrupted';setBusy(false);$('retryButton').hidden=true;
   for(const v of variants){$('answer-'+v).classList.remove('pending');if(!lastJob?.[v])$('answer-'+v).textContent=t('interrupted');}
  }else{status='connectionLost';$('retryButton').hidden=false;toast(errorText(e));}
  renderStatus();
 }
}
async function submitActive(){
 if(!active)return;$('retryButton').hidden=true;setBusy(true);status='running';renderStatus();
 try{const job=await call('jobs',{prompt:active.prompt,request_id:active.request_id});applyJob(job);if(active)pollTimer=setTimeout(poll,5000);}
 catch(e){
  toast(errorText(e));
  if([409,422,429,503].includes(e.status)){active=null;saveActive();setBusy(false);status='failed';$('results').hidden=true;}
  else{status='connectionLost';$('retryButton').hidden=false;}
  renderStatus();
 }
}
async function refreshInfo(){
 try{const d=await call('info');info=d;ready=!!(d.ready&&d.accepting_jobs&&d.amd?.configured&&d.quantum?.configured&&d.quantum?.simulator===false);if(!active){status=ready?'ready':d.status==='starting'?'loading':'unavailable';renderStatus();setBusy(false);}}
 catch{ready=false;if(!active){status='unavailable';renderStatus();setBusy(false);}}
 if(!ready)setTimeout(refreshInfo,10000);
}
$('technicalButton').onclick=()=>navigate(location.hash!=='#technical');$('backButton').onclick=()=>navigate(false);window.addEventListener('hashchange',showView);
document.querySelectorAll('[data-lang]').forEach(el=>el.onclick=()=>{setLanguage(el.getAttribute('data-lang'));showView();});
$('question').addEventListener('input',invalidate);$('question').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing){e.preventDefault();if(!busy&&ready)$('questionForm').requestSubmit();}});
$('newQuestion').onclick=()=>{$('question').value='';invalidate();$('question').focus();window.scrollTo({top:0,behavior:'smooth'});};
$('questionForm').onsubmit=async e=>{e.preventDefault();if(busy||!ready)return;const prompt=$('question').value.trim();if(!prompt)return toast(t('enterQuestion'));invalidate();const request_id=crypto.randomUUID();active={prompt,request_id,job_id:request_id.replaceAll('-','')};saveActive();pendingView(prompt);await submitActive();};
$('retryButton').onclick=()=>{clearTimeout(pollTimer);$('retryButton').hidden=true;return poll();};
$('cancelButton').onclick=async()=>{if(!active?.job_id)return;try{await call('jobs/'+active.job_id+'/cancel',{});status='cancelling';renderStatus();}catch(e){toast(errorText(e));}};
$('exportButton').onclick=()=>{if(!lastJob)return;const url=URL.createObjectURL(new Blob([JSON.stringify({...lastJob,interface_language:language},null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='amdquant-amd-ibm-'+Date.now()+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
setLanguage(language);showView();setBusy(true);
(async()=>{
 try{const saved=JSON.parse(localStorage.getItem('amdquant.active.v3')||'null');if(saved&&typeof saved.prompt==='string'&&/^[a-f0-9]{32}$/.test(saved.job_id))active=saved;}catch{}
 await refreshInfo();
 if(active){$('question').value=active.prompt;pendingView(active.prompt);setBusy(true);await poll();}else setBusy(false);renderStatus();
})();
fetch('./models/qwen-benchmark.json').then(r=>{if(!r.ok)throw new Error('benchmark');return r.json();}).then(data=>{qwenReport=data;renderBenchmark();}).catch(()=>$('qwenConclusion').textContent=t('benchmarkError'));
