(function(){const i=document.createElement("link").relList;if(i&&i.supports&&i.supports("modulepreload"))return;for(const t of document.querySelectorAll('link[rel="modulepreload"]'))s(t);new MutationObserver(t=>{for(const n of t)if(n.type==="childList")for(const r of n.addedNodes)r.tagName==="LINK"&&r.rel==="modulepreload"&&s(r)}).observe(document,{childList:!0,subtree:!0});function a(t){const n={};return t.integrity&&(n.integrity=t.integrity),t.referrerPolicy&&(n.referrerPolicy=t.referrerPolicy),t.crossOrigin==="use-credentials"?n.credentials="include":t.crossOrigin==="anonymous"?n.credentials="omit":n.credentials="same-origin",n}function s(t){if(t.ep)return;t.ep=!0;const n=a(t);fetch(t.href,n)}})();const x=document.querySelector("#app");x.innerHTML=`
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
`;const o=e=>document.querySelector(e),c=o("#drop"),d=o("#file"),m=o("#browse"),$=o("#preview"),w=o("#previewImg"),k=o("#fileName"),v=o("#run"),h=o("#status"),I=o("#results");let f=null;function u(e){document.querySelectorAll(".p-step").forEach((i,a)=>{i.classList.toggle("active",a+1===e),i.classList.toggle("done",a+1<e)})}function p(e,i=!1){h.textContent=e,h.className="status"+(i?" err":e?" ok":"")}m.onclick=()=>d.click();c.onclick=e=>{e.target!==m&&d.click()};c.ondragover=e=>{e.preventDefault(),c.style.borderColor="#FEE101"};c.ondragleave=()=>c.style.borderColor="";c.ondrop=e=>{var a;e.preventDefault();const i=(a=e.dataTransfer)==null?void 0:a.files[0];i&&b(i)};d.onchange=()=>{var e;(e=d.files)!=null&&e[0]&&b(d.files[0])};function b(e){if(!e.type.startsWith("image/"))return p("Please upload an image",!0);f=e,w.src=URL.createObjectURL(e),k.textContent=e.name,$.classList.remove("hidden"),p("")}v.onclick=async()=>{if(!f)return;v.disabled=!0,p("Running pipeline - face → search → blockchain ..."),u(1);const e=new FormData;e.append("file",f);try{const i=await fetch("/api/pipeline/run",{method:"POST",body:e}),a=await i.json();if(!i.ok)throw new Error(a.detail||"Pipeline failed");B(a),p(`Done in ${a.total_latency_ms}ms - verified on chain`)}catch(i){p(i.message,!0)}finally{v.disabled=!1}};function B(e){I.classList.remove("hidden"),u(3);const i=e.face,a=e.search,s=e.blockchain,t=e.verify,n=o("#faceBox"),r=o("#searchBox"),y=o("#chainBox");n.innerHTML=`
    <div class="kv"><div><b>Detected</b><span>${i.detected?"Yes":"No"}</span></div>
    <div><b>Faces</b><span>${i.faces.length}</span></div>
    <div><b>BBox</b><span>${i.faces[0]?i.faces[0].bbox.join(", "):"-"}</span></div>
    <div><b>Embedding</b><span>${i.embedding?i.embedding.length+"-d":"-"}</span></div></div>
    <div style="margin-top:8px"><span class="badge ok">${i.message}</span></div>`,r.innerHTML=`
    <div style="margin-bottom:8px"><span class="badge">${a.engine}</span> <small style="color:var(--muted); font-family:'Victor Mono',monospace; font-size:10px"> ${a.latency_ms}ms</small></div>
    ${a.results.map(l=>`
      <div class="result"><div><a href="${l.url}" target="_blank">${l.title}</a> ${l.is_social?'<span class="badge" style="margin-left:6px">social</span>':""}</div>
      <small>${l.source} - ${l.snippet||""}</small><br><small style="word-break:break-all; color:var(--yellow)">${l.url}</small></div>
    `).join("")}`,y.innerHTML=`
    <div class="kv"><div><b>Block</b><span>#${s.index}</span></div><div><b>Prev</b><span>${s.previous_hash.slice(0,16)}…</span></div><div><b>Nonce</b><span>${s.nonce}</span></div></div>
    <div style="margin-top:8px"><b style="font-size:10px; color:var(--yellow); font-family:'Victor Mono',monospace; letter-spacing:0.1em">BLOCK HASH</b><div class="hash">${s.hash}</div></div>
    <div><b style="font-size:10px; color:var(--yellow); font-family:'Victor Mono',monospace; letter-spacing:0.1em">DATA HASH</b><div class="hash">${s.data_hash}</div></div>
    <div><b style="font-size:10px; color:var(--yellow); font-family:'Victor Mono',monospace; letter-spacing:0.1em">FINGERPRINT</b><div class="hash">${s.data.fingerprint}</div></div>
    <div style="margin-top:8px"><span class="badge">${t.verified?"✓ Verified on-chain":"Not verified"}</span> <small style="color:var(--muted)"> ${t.message}</small></div>`,document.getElementById("fpInput").value=s.data.fingerprint,g()}async function g(){const i=await(await fetch("/api/blockchain/chain")).json(),a=document.getElementById("explorer");a.innerHTML=`<div style="margin-bottom:8px; font-family:'Victor Mono',monospace; font-size:11px"><b>Length:</b> ${i.length} &nbsp; <span class="badge">${i.is_valid?"valid chain":"INVALID"}</span></div>
  ${i.chain.slice().reverse().slice(0,5).map(s=>`
    <div class="block"><div><b>#${s.index}</b> - ${new Date(s.timestamp).toLocaleString()} <span style="float:right; font-family:'Victor Mono',monospace; font-size:10px; color:var(--yellow)">${s.hash.slice(0,12)}…</span></div>
    <small style="color:var(--muted)">${s.data.post_title} - ${s.data.post_url}</small><div class="hash" style="margin-top:6px">${s.data.fingerprint.slice(0,32)}…</div></div>
  `).join("")}`}document.getElementById("verifyBtn").onclick=async()=>{const e=document.getElementById("fpInput").value.trim();if(!e)return;const a=await(await fetch(`/api/blockchain/verify/${encodeURIComponent(e)}`)).json(),s=document.getElementById("verifyOut");s.innerHTML=`<div><span class="badge">${a.verified?"✓ Verified":"✗ Not found"}</span> ${a.message}${a.block?`<div class="hash" style="margin-top:6px">${a.block.hash}</div>`:""}</div>`};g();
