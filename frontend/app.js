const $ = s => document.querySelector(s);
const drop = $("#drop"), fileInput = $("#file"), browse = $("#browse");
const preview = $("#preview"), previewImg = $("#previewImg"), fileName = $("#fileName");
const runBtn = $("#run"), status = $("#status"), results = $("#results");

let selectedFile = null;

function setStep(n){
  document.querySelectorAll(".step").forEach((el,i)=>{
    el.classList.toggle("active", i+1===n);
    el.classList.toggle("done", i+1<n);
  });
}

browse.onclick = () => fileInput.click();
drop.onclick = (e)=>{ if(e.target!==browse) fileInput.click(); };
drop.ondragover = e=>{ e.preventDefault(); drop.style.borderColor="var(--accent)"; };
drop.ondragleave = ()=> drop.style.borderColor="";
drop.ondrop = e=>{
  e.preventDefault();
  const f=e.dataTransfer.files[0];
  if(f) handleFile(f);
};
fileInput.onchange = ()=>{ if(fileInput.files[0]) handleFile(fileInput.files[0]); };

function handleFile(f){
  if(!f.type.startsWith("image/")) return setStatus("Please upload an image", true);
  selectedFile=f;
  previewImg.src=URL.createObjectURL(f);
  fileName.textContent=f.name;
  preview.classList.remove("hidden");
  setStatus("");
}

function setStatus(msg, isErr=false){
  status.textContent=msg;
  status.className="status"+(isErr?" err":msg?" ok":"");
}

runBtn.onclick = async ()=>{
  if(!selectedFile) return;
  runBtn.disabled=true; setStatus("Running pipeline - face → search → blockchain ..."); setStep(1);
  const fd=new FormData(); fd.append("file", selectedFile);
  try{
    const r=await fetch("/api/pipeline/run",{method:"POST",body:fd});
    const data=await r.json();
    if(!r.ok) throw new Error(data.detail||"Pipeline failed");
    render(data);
    setStatus(`Done in ${data.total_latency_ms}ms - verified on chain`, false);
  }catch(e){ setStatus(e.message,true);}
  finally{ runBtn.disabled=false; }
};

function render(d){
  results.classList.remove("hidden");
  setStep(3);
  const face=d.face, search=d.search, block=d.blockchain, verify=d.verify;

  $("#faceBox").innerHTML=`
    <div class="kv">
      <div><b>Detected</b><span>${face.detected?"Yes":"No"}</span></div>
      <div><b>Faces</b><span>${face.faces.length}</span></div>
      <div><b>BBox</b><span>${face.faces[0]?face.faces[0].bbox.join(", "):"-"}</span></div>
      <div><b>Embedding</b><span>${face.embedding?face.embedding.length+"-d":"-"}</span></div>
    </div>
    ${face.cropped_face_path?`<small style="color:var(--muted)">Cropped face saved server-side</small>`:""}
    <div class="badge" style="margin-top:8px">${face.message}</div>
  `;

  $("#searchBox").innerHTML=`
    <div style="margin-bottom:8px"><span class="badge">Engine: ${search.engine}</span> <small style="color:var(--muted)">${search.latency_ms}ms</small></div>
    ${search.results.map(r=>`
      <div class="result">
        <div><a href="${r.url}" target="_blank">${r.title}</a> ${r.is_social?'<span class="badge social">social</span>':''}</div>
        <small>${r.source} - ${r.snippet||""}</small><br>
        <small style="word-break:break-all;color:var(--accent2)">${r.url}</small>
      </div>
    `).join("")}
  `;

  $("#chainBox").innerHTML=`
    <div class="kv">
      <div><b>Block</b><span>#${block.index}</span></div>
      <div><b>Prev hash</b><span>${block.previous_hash.slice(0,16)}…</span></div>
      <div><b>Nonce</b><span>${block.nonce}</span></div>
    </div>
    <div style="margin-top:8px"><b style="font-size:12px;color:var(--muted)">Block hash</b><div class="hash">${block.hash}</div></div>
    <div><b style="font-size:12px;color:var(--muted)">Data hash</b><div class="hash">${block.data_hash}</div></div>
    <div><b style="font-size:12px;color:var(--muted)">Fingerprint</b><div class="hash">${block.data.fingerprint}</div></div>
    <div style="margin-top:8px"><span class="badge">${verify.verified?"✓ Verified on-chain":"Not verified"}</span> <small>${verify.message}</small></div>
  `;
  $("#fpInput").value=block.data.fingerprint;
  loadChain();
}

async function loadChain(){
  const r=await fetch("/api/blockchain/chain");
  const data=await r.json();
  $("#explorer").innerHTML=`
    <div style="margin-bottom:8px"><b>Length:</b> ${data.length} &nbsp; <span class="badge">${data.is_valid?"valid chain":"INVALID"}</span></div>
    ${data.chain.slice().reverse().slice(0,5).map(b=>`
      <div class="block">
        <div><b>#${b.index}</b> - ${new Date(b.timestamp).toLocaleString()} <span style="float:right;font-family:monospace;font-size:11px">${b.hash.slice(0,12)}…</span></div>
        <small>${b.data.post_title} - ${b.data.post_url}</small>
        <div class="hash" style="margin-top:6px">${b.data.fingerprint.slice(0,32)}…</div>
      </div>
    `).join("")}
  `;
}

$("#verifyBtn").onclick=async()=>{
  const fp=$("#fpInput").value.trim();
  if(!fp) return;
  const r=await fetch(`/api/blockchain/verify/${encodeURIComponent(fp)}`);
  const d=await r.json();
  $("#verifyOut").innerHTML=`<div style="margin-top:10px"><span class="badge">${d.verified?"✓ Verified":"✗ Not found"}</span> ${d.message}${d.block?`<div class="hash" style="margin-top:6px">${d.block.hash}</div>`:""}</div>`;
};

loadChain();
