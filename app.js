let D,cat='all';const $=s=>document.querySelector(s);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
if($('#list'))fetch('tools.json').then(r=>r.json()).then(d=>{D=d;$('#upd').textContent=d.updated;const by=Object.fromEntries(d.tools.map(t=>[t.id,t]));
$('#uc').innerHTML=d.useCases.map(u=>`<div class="card uc"><h3>${esc(u.question)}</h3><ol>${u.picks.map(p=>`<li><a href="tools/${p}">${esc(by[p].name)}</a></li>`).join('')}</ol></div>`).join('');
$('#rel').innerHTML=d.newReleases.map(r=>`<div class="card"><span class="tag">${esc(r.date)}</span><h3><a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.name)}</a></h3><p>${esc(r.summary)}</p><a class="muted" href="${esc(r.source)}" target="_blank" rel="noopener">source</a></div>`).join('');
const n=c=>c=='all'?d.tools.length:d.tools.filter(t=>t.category==c).length;
$('#cats').innerHTML=[{id:'all',name:'All'},...d.categories].map(c=>`<button type="button" data-c="${c.id}" class="chip ${c.id=='all'?'on':''}" aria-pressed="${c.id=='all'}">${esc(c.name)} <span>${n(c.id)}</span></button>`).join('');
$('#cats').onclick=e=>{const b=e.target.closest('button');if(!b)return;cat=b.dataset.c;document.querySelectorAll('#cats button').forEach(x=>{x.classList.toggle('on',x==b);x.setAttribute('aria-pressed',x==b)});draw()};
$('#q').oninput=draw;$('#price').onchange=draw;const q=new URLSearchParams(location.search).get('q');if(q){$('#q').value=q;$('#hq').value=q}draw()});
function draw(){const q=$('#q').value.toLowerCase().trim(),pr=$('#price').value,cn=Object.fromEntries(D.categories.map(c=>[c.id,c.name]));
const L=D.tools.filter(t=>(cat=='all'||t.category==cat)&&(!pr||t.pricing==pr)&&(t.name+' '+t.description+' '+t.bestFor+' '+cn[t.category]).toLowerCase().includes(q));
$('#count').textContent=`${L.length} of ${D.tools.length} tools`;
$('#list').innerHTML=L.length?L.map(t=>`<div class="card"><h3><a href="tools/${t.id}">${esc(t.name)}</a></h3><span class="tag">${esc(cn[t.category])}</span><span class="tag ${t.pricing}">${t.pricing}</span><p>${esc(t.description)}</p><p class="muted">Best for: ${esc(t.bestFor)}</p></div>`).join(''):'<p class="muted">No tools match. Try a different search or category.</p>'}
document.querySelectorAll('[data-filter]').forEach(i=>{const items=[...document.querySelectorAll(i.dataset.filter)],c=document.querySelector('[data-count]');const f=()=>{const q=i.value.toLowerCase().trim();let k=0;items.forEach(a=>{const s=a.textContent.toLowerCase().includes(q);a.hidden=!s;k+=s});if(c)c.textContent=`${k} of ${items.length}`};i.oninput=f;f()});
document.querySelectorAll('details.dd').forEach(d=>document.addEventListener('click',e=>{if(!d.contains(e.target))d.open=false}));
document.getElementById('signup')?.addEventListener('submit',async e=>{e.preventDefault();const f=e.target,m=f.querySelector('[role=status]');m.textContent='Subscribing…';
try{const r=await fetch('/api/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:f.email.value,website:f.website.value})});
if(r.status===404){m.textContent='Newsletter launches soon — check back!';return}const j=await r.json();if(j.redirect){location.href=j.redirect;return}m.textContent=j.ok?"You're in! Watch your inbox for the next Loadout Weekly.":j.error}catch{m.textContent='Something went wrong. Try again.'}});
