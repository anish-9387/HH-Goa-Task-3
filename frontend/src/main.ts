import './style.css'

type SearchResult = { title:string; url:string; thumbnail?:string; source:string; snippet?:string; is_social:boolean }

const app = document.querySelector<HTMLDivElement>('#app')!
app.innerHTML = `
<header class="hh-header">
  <div class="hh-header-inner">
    <div class="brand">
      <div class="brand-mark">HH</div>
      <div class="brand-text"><b>HACKER HOUSE GOA</b><span>28 - 31 Oct 2026 • Task 3 - Face → Search → Blockchain</span></div>
    </div>
    <nav class="nav">
      <a href="https://hhgoa.com" target="_blank">HHGOA.COM</a>
      <a href="/docs" target="_blank">API DOCS</a>
      <button class="cta-apply" onclick="window.open('https://hhgoa.com','_blank')">APPLY</button>
    </nav>
  </div>
</header>

<section class="hero">
  <h1>Face Identification<br><em>& Blockchain Verification</em></h1>
  <div class="hero-sub"><span>GOA, INDIA · 28 – 31 OCT 2026</span><span>·</span><span>2:47 PM STUDIO</span><span>·</span><span>HH GOA 2026 - TASK 3</span></div>
  <p class="hero-desc">Pipeline that takes a face scan, finds a real matching social post via genuine reverse-image search, and writes a tamper-evident fingerprint to a blockchain. Green is the house. Yellow is the signal.</p>
  <div class="pipeline" id="pipeline">
    <div class="p-step active" id="s1"><b>1</b> Face Scan</div><div class="p-line"></div>
    <div class="p-step" id="s2"><b>2</b> Web Search</div><div class="p-line"></div>
    <div class="p-step" id="s3"><b>3</b> Blockchain</div>
  </div>
</section>

<main class="wrap">
  <section class="card upload-card">
    <h2>Upload face image</h2>
    <p style="margin:0 0 10px; color:var(--muted); font-size:12px; font-family:'Victor Mono', monospace; letter-spacing:0.06em">JPG / PNG - any face image. Detection via InsightFace (if installed) → Haar fallback.</p>
    <div id="drop" class="drop">
      <input type="file" id="file" accept="image/*" hidden>
      <p>Drag & drop or <button id="browse" class="link">browse</button></p>
      <small style="color:var(--muted)">Powered by local PoW chain · SerpAPI + live HTTP fallback</small>
    </div>
    <div id="preview" class="preview hidden">
      <img id="previewImg" alt="preview">
      <div style="display:flex; flex-direction:column; gap:10px">
        <span id="fileName" style="font-family:'Victor Mono', monospace; font-size:11px; color:var(--yellow)"></span>
        <button id="run" class="btn primary">Run Pipeline →</button>
      </div>
    </div>
    <div id="status" class="status"></div>
  </section>

  <section id="results" class="hidden">
    <div class="grid">
      <div class="card"><h3>① Face Identification</h3><div id="faceBox"></div></div>
      <div class="card"><h3>② Social / Web Search</h3><div id="searchBox"></div></div>
      <div class="card"><h3>③ Blockchain Verification</h3><div id="chainBox"></div></div>
    </div>
    <div class="card"><h3>Blockchain Explorer</h3><div id="explorer"></div></div>
    <div class="card"><h3>Verify fingerprint</h3>
      <div class="verify-row"><input id="fpInput" placeholder="fingerprint / data_hash / block hash"><button id="verifyBtn" class="btn">Verify</button></div>
      <div id="verifyOut" style="margin-top:10px"></div>
    </div>
  </section>
  <div class="footer">© 2026 HH-GOA · 2:47 PM STUDIO · GOA, INDIA · Less Noise. More Signal. · <a href="https://hhgoa.com" target="_blank">hhgoa.com</a></div>
</main>
`

const $ = <T extends HTMLElement>(s:string)=> document.querySelector(s) as T
const drop = $('#drop') as HTMLDivElement
const fileInput = $('#file') as HTMLInputElement
const browse = $('#browse') as HTMLButtonElement
const preview = $('#preview') as HTMLDivElement
const previewImg = $('#previewImg') as HTMLImageElement
const fileNameEl = $('#fileName') as HTMLSpanElement
const runBtn = $('#run') as HTMLButtonElement
const statusEl = $('#status') as HTMLDivElement
const results = $('#results') as HTMLElement

let selectedFile: File | null = null

function setStep(n:number){
  document.querySelectorAll('.p-step').forEach((el,i)=>{
    el.classList.toggle('active', i+1===n)
    el.classList.toggle('done', i+1 < n)
  })
}
function setStatus(msg:string, isErr=false){
  statusEl.textContent = msg
  statusEl.className = 'status' + (isErr ? ' err' : msg ? ' ok' : '')
}
browse.onclick = () => fileInput.click()
drop.onclick = (e)=>{ if((e.target as HTMLElement)!==browse) fileInput.click() }
drop.ondragover = e=>{ e.preventDefault(); (drop as HTMLElement).style.borderColor='#FEE101' }
drop.ondragleave = ()=> (drop as HTMLElement).style.borderColor=''
drop.ondrop = e=>{
  e.preventDefault(); const f=(e as DragEvent).dataTransfer?.files[0]; if(f) handleFile(f)
}
fileInput.onchange = ()=>{ if(fileInput.files?.[0]) handleFile(fileInput.files[0]) }

function handleFile(f:File){
  if(!f.type.startsWith('image/')) return setStatus('Please upload an image', true)
  selectedFile=f
  previewImg.src=URL.createObjectURL(f)
  fileNameEl.textContent=f.name
  preview.classList.remove('hidden')
  setStatus('')
}

runBtn.onclick = async ()=>{
  if(!selectedFile) return
  runBtn.disabled=true; setStatus('Running pipeline - face → search → blockchain ...'); setStep(1)
  const fd=new FormData(); fd.append('file', selectedFile)
  try{
    const r=await fetch('/api/pipeline/run',{method:'POST', body:fd})
    const data=await r.json()
    if(!r.ok) throw new Error(data.detail || 'Pipeline failed')
    render(data); setStatus(`Done in ${data.total_latency_ms}ms - verified on chain`)
  }catch(e:any){ setStatus(e.message, true)}
  finally{ runBtn.disabled=false}
}

function render(d:any){
  results.classList.remove('hidden'); setStep(3)
  const face=d.face, search=d.search, block=d.blockchain, verify=d.verify
  const faceBox = $('#faceBox') as HTMLDivElement
  const searchBox = $('#searchBox') as HTMLDivElement
  const chainBox = $('#chainBox') as HTMLDivElement
  faceBox.innerHTML = `
    <div class="kv"><div><b>Detected</b><span>${face.detected?'Yes':'No'}</span></div>
    <div><b>Faces</b><span>${face.faces.length}</span></div>
    <div><b>BBox</b><span>${face.faces[0]?face.faces[0].bbox.join(', '):'-'}</span></div>
    <div><b>Embedding</b><span>${face.embedding?face.embedding.length+'-d':'-'}</span></div></div>
    <div style="margin-top:8px"><span class="badge ok">${face.message}</span></div>`
  searchBox.innerHTML = `
    <div style="margin-bottom:8px"><span class="badge">${search.engine}</span> <small style="color:var(--muted); font-family:'Victor Mono',monospace; font-size:10px"> ${search.latency_ms}ms</small></div>
    ${search.results.map((r:SearchResult)=>`
      <div class="result"><div><a href="${r.url}" target="_blank">${r.title}</a> ${r.is_social?'<span class="badge" style="margin-left:6px">social</span>':''}</div>
      <small>${r.source} - ${r.snippet||''}</small><br><small style="word-break:break-all; color:var(--yellow)">${r.url}</small></div>
    `).join('')}`
  chainBox.innerHTML = `
    <div class="kv"><div><b>Block</b><span>#${block.index}</span></div><div><b>Prev</b><span>${block.previous_hash.slice(0,16)}…</span></div><div><b>Nonce</b><span>${block.nonce}</span></div></div>
    <div style="margin-top:8px"><b style="font-size:10px; color:var(--yellow); font-family:'Victor Mono',monospace; letter-spacing:0.1em">BLOCK HASH</b><div class="hash">${block.hash}</div></div>
    <div><b style="font-size:10px; color:var(--yellow); font-family:'Victor Mono',monospace; letter-spacing:0.1em">DATA HASH</b><div class="hash">${block.data_hash}</div></div>
    <div><b style="font-size:10px; color:var(--yellow); font-family:'Victor Mono',monospace; letter-spacing:0.1em">FINGERPRINT</b><div class="hash">${block.data.fingerprint}</div></div>
    <div style="margin-top:8px"><span class="badge">${verify.verified?'✓ Verified on-chain':'Not verified'}</span> <small style="color:var(--muted)"> ${verify.message}</small></div>`
  ;(document.getElementById('fpInput') as HTMLInputElement).value = block.data.fingerprint
  loadChain()
}

async function loadChain(){
  const r=await fetch('/api/blockchain/chain'); const data=await r.json()
  const el = document.getElementById('explorer') as HTMLDivElement
  el.innerHTML = `<div style="margin-bottom:8px; font-family:'Victor Mono',monospace; font-size:11px"><b>Length:</b> ${data.length} &nbsp; <span class="badge">${data.is_valid?'valid chain':'INVALID'}</span></div>
  ${data.chain.slice().reverse().slice(0,5).map((b:any)=>`
    <div class="block"><div><b>#${b.index}</b> - ${new Date(b.timestamp).toLocaleString()} <span style="float:right; font-family:'Victor Mono',monospace; font-size:10px; color:var(--yellow)">${b.hash.slice(0,12)}…</span></div>
    <small style="color:var(--muted)">${b.data.post_title} - ${b.data.post_url}</small><div class="hash" style="margin-top:6px">${b.data.fingerprint.slice(0,32)}…</div></div>
  `).join('')}`
}
;(document.getElementById('verifyBtn') as HTMLButtonElement).onclick = async ()=>{
  const fp=(document.getElementById('fpInput') as HTMLInputElement).value.trim(); if(!fp) return
  const r=await fetch(`/api/blockchain/verify/${encodeURIComponent(fp)}`); const d=await r.json()
  const out=document.getElementById('verifyOut') as HTMLDivElement
  out.innerHTML = `<div><span class="badge">${d.verified?'✓ Verified':'✗ Not found'}</span> ${d.message}${d.block?`<div class="hash" style="margin-top:6px">${d.block.hash}</div>`:''}</div>`
}
loadChain()
