let D,cat='all';const $=s=>document.querySelector(s);
fetch('tools.json').then(r=>r.json()).then(d=>{D=d;$('#upd').textContent=d.updated;const by=Object.fromEntries(d.tools.map(t=>[t.id,t]));
$('#uc').innerHTML=d.useCases.map(u=>`<div class="card"><h3>${u.question}</h3><ol>${u.picks.map(p=>`<li><a href="tools/${p}.html">${by[p].name}</a></li>`).join('')}</ol></div>`).join('');
$('#rel').innerHTML=d.newReleases.map(r=>`<div class="card"><span class="tag">${r.date}</span><h3><a href="${r.url}" target="_blank">${r.name}</a></h3><p>${r.summary}</p><a class="muted" href="${r.source}" target="_blank">source</a></div>`).join('');
$('#cats').innerHTML=[{id:'all',name:'All'},...d.categories].map(c=>`<button data-c="${c.id}" class="${c.id=='all'?'on':''}">${c.name}</button>`).join('');
$('#cats').onclick=e=>{if(!e.target.dataset.c)return;cat=e.target.dataset.c;document.querySelectorAll('#cats button').forEach(b=>b.classList.toggle('on',b==e.target));draw()};$('#q').oninput=draw;draw()});
function draw(){const q=$('#q').value.toLowerCase(),cn=Object.fromEntries(D.categories.map(c=>[c.id,c.name]));
$('#list').innerHTML=D.tools.filter(t=>(cat=='all'||t.category==cat)&&(t.name+t.description+t.bestFor).toLowerCase().includes(q)).map(t=>`<div class="card"><h3><a href="tools/${t.id}.html">${t.name}</a></h3><span class="tag">${cn[t.category]}</span><span class="tag ${t.pricing}">${t.pricing}</span><p>${t.description}</p><p class="muted">Best for: ${t.bestFor}</p></div>`).join('')}
document.getElementById('signup')?.addEventListener('submit',async e=>{e.preventDefault();const f=e.target,m=f.querySelector('[role=status]');m.textContent='Subscribing…';
try{const r=await fetch('/api/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:f.email.value,website:f.website.value})});
if(r.status===404){m.textContent='Newsletter launches soon — check back!';return}const j=await r.json();m.textContent=j.ok?"You're in! Watch your inbox for the next Loadout Weekly.":j.error}catch{m.textContent='Something went wrong. Try again.'}});
