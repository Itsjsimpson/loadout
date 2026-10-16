(function(){
const D=JSON.parse(document.getElementById('rr-data').textContent),T=D.tiers,KEY='rankroom-demo-'+D.slug;
const P=Object.fromEntries(D.players.map(p=>[p.name,p]));const ti=t=>T.indexOf(t);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>show(b.dataset.tab));
function show(t){document.querySelectorAll('.tabs button').forEach(b=>b.classList.toggle('on',b.dataset.tab===t));document.querySelectorAll('.pane').forEach(p=>p.classList.toggle('on',p.id===t));if(t==='board')renderBoard();if(t==='sheet')renderSheet();}
function chip(p,drag){return `<div class="chip" ${drag?'draggable="true"':''} data-name="${esc(p.name)}" style="--c:${p.color}">${esc(p.name)} <small>${esc(p.team)} · ${esc(p.stat)}</small></div>`}
function board(el,assign,editable){
 const rows=T.map(t=>`<div class="tier t-${t}" data-tier="${t}"><div class="lab">${t}</div><div class="drop">${D.players.filter(p=>assign[p.name]===t).map(p=>chip(p,editable)).join('')}</div></div>`);
 if(editable)rows.push(`<div class="tier t-pool" data-tier=""><div class="lab">Unranked</div><div class="drop">${D.players.filter(p=>!assign[p.name]).map(p=>chip(p,true)).join('')}</div></div>`);
 el.innerHTML=rows.join('');}
// host
const host=Object.fromEntries(D.players.map(p=>[p.name,p.host]));board(document.getElementById('hostBoard'),host,false);
// fan
let fan=JSON.parse(localStorage.getItem(KEY+'-draft')||'{}'),sel=null;const fb=document.getElementById('fanBoard');
function save(){localStorage.setItem(KEY+'-draft',JSON.stringify(fan));board(fb,fan,true);}
function move(name,t){if(t)fan[name]=t;else delete fan[name];sel=null;save();}
fb.addEventListener('dragstart',e=>{const c=e.target.closest('.chip');if(c)e.dataTransfer.setData('text/plain',c.dataset.name)});
fb.addEventListener('dragover',e=>{const t=e.target.closest('.tier');if(t){e.preventDefault();t.classList.add('over')}});
fb.addEventListener('dragleave',e=>{const t=e.target.closest('.tier');if(t)t.classList.remove('over')});
fb.addEventListener('drop',e=>{const t=e.target.closest('.tier');if(!t)return;e.preventDefault();move(e.dataTransfer.getData('text/plain'),t.dataset.tier)});
fb.addEventListener('click',e=>{const c=e.target.closest('.chip');if(c){sel=c.dataset.name;fb.querySelectorAll('.chip').forEach(x=>x.classList.toggle('sel',x===c));return}const t=e.target.closest('.tier');if(t&&sel)move(sel,t.dataset.tier)});
save();
document.getElementById('resetFan').onclick=()=>{fan={};localStorage.removeItem(KEY+'-vote');save();document.getElementById('fanMsg').textContent=''};
document.getElementById('submitFan').onclick=()=>{const n=Object.keys(fan).length,m=document.getElementById('fanMsg');if(n<D.players.length){m.textContent=`Rank all ${D.players.length} players first (${n} done).`;return}localStorage.setItem(KEY+'-vote',JSON.stringify(fan));m.textContent='Submitted! Opening the board...';show('board')};
// sample audience data: deterministic simulated votes
function rng(s){let h=2166136261;for(const c of s)h=Math.imul(h^c.charCodeAt(0),16777619);return()=>{h^=h<<13;h^=h>>>17;h^=h<<5;return((h>>>0)%10000)/10000}}
const SAMPLE=500;const sample={};
D.players.forEach(p=>{const r=rng(D.slug+p.name),bias=(r()-.5)*2.6,c=[0,0,0,0,0];for(let i=0;i<SAMPLE;i++){let v=ti(p.host)+bias+(r()+r()+r()-1.5)*1.4;v=Math.max(0,Math.min(4,Math.round(v)));c[v]++}sample[p.name]=c});
function rows(){const vote=JSON.parse(localStorage.getItem(KEY+'-vote')||'null');return D.players.map(p=>{const c=sample[p.name].slice();if(vote&&vote[p.name])c[ti(vote[p.name])]++;const n=c.reduce((a,b)=>a+b,0),avg=c.reduce((a,b,i)=>a+b*i,0)/n;return{p,avg,aud:T[Math.round(avg)],gap:ti(p.host)-avg,mine:vote&&vote[p.name],n}})}
function renderBoard(){const R=rows(),vote=R[0].mine;
 document.getElementById('compare').innerHTML=`<table><thead><tr><th>Player</th><th>Host</th>${vote?'<th>You</th>':''}<th>Audience avg</th><th>Gap</th></tr></thead><tbody>${R.sort((a,b)=>Math.abs(b.gap)-Math.abs(a.gap)).map(r=>`<tr><td>${esc(r.p.name)} <span class="muted">${esc(r.p.team)}</span></td><td><b>${r.p.host}</b></td>${vote?`<td>${r.mine}</td>`:''}<td>${r.aud} <span class="bar"><i style="width:${(4-r.avg)/4*100}%"></i></span></td><td class="${r.gap>0.4?'gap-up':r.gap<-0.4?'gap-down':''}">${Math.abs(r.gap)<0.4?'agree':r.gap>0?'fans higher by '+r.gap.toFixed(1)+' tier':'fans lower by '+(-r.gap).toFixed(1)+' tier'}</td></tr>`).join('')}</tbody></table><p class="muted">${R[0].n} votes counted (${SAMPLE} are sample audience data${vote?' + your vote':''}). Sorted by biggest disagreement.</p>`;draw(R)}
function draw(R){const V=n=>getComputedStyle(document.body).getPropertyValue(n).trim(),FF=V('--font-body')||'system-ui',FH=V('--font-head')||FF;const c=document.getElementById('cv'),x=c.getContext('2d');x.fillStyle=V('--surface');x.fillRect(0,0,1200,675);x.fillStyle=V('--accent');x.fillRect(0,0,1200,90);x.fillStyle=V('--on-accent');x.font='bold 40px '+FH;x.fillText('HOST vs AUDIENCE',40,58);x.font='22px '+FF;x.fillText(D.title.slice(0,60),560,56);
 const top=R.slice().sort((a,b)=>Math.abs(b.gap)-Math.abs(a.gap)).slice(0,6);x.fillStyle=V('--ink');x.font='bold 22px '+FH;x.fillText('Player',40,135);x.fillText('Host',640,135);x.fillText('Audience',800,135);x.fillText('Gap',1010,135);
 top.forEach((r,i)=>{const y=190+i*72;x.fillStyle=r.p.color;x.fillRect(40,y-34,10,50);x.fillStyle=V('--ink');x.font='bold 28px '+FH;x.fillText(r.p.name,64,y);x.font='18px '+FF;x.fillStyle=V('--muted');x.fillText(r.p.team,64,y+22);x.fillStyle=V('--ink');x.font='bold 34px '+FH;x.fillText(r.p.host,655,y+4);x.fillText(r.aud,830,y+4);x.fillStyle=r.gap>0?V('--up'):V('--down');x.font='bold 26px '+FH;x.fillText((r.gap>0?'▲ ':'▼ ')+Math.abs(r.gap).toFixed(1),1010,y+4)});
 x.fillStyle=V('--muted');x.font='16px '+FF;x.fillText('RankRoom demo · sample audience data · not affiliated with any show · stats: ESPN',40,650)}
document.getElementById('dlPng').onclick=()=>{const a=document.createElement('a');a.download='rankroom-'+D.slug+'.png';a.href=document.getElementById('cv').toDataURL();a.click()};
function renderSheet(){const R=rows().sort((a,b)=>Math.abs(b.gap)-Math.abs(a.gap)),up=R.filter(r=>r.gap>0.4).slice(0,3),dn=R.filter(r=>r.gap<-0.4).slice(0,3);
 const item=r=>`<li><b>${esc(r.p.name)}</b> (${esc(r.p.team)}): host ${r.p.host}, audience ${r.aud}. <span class="muted">Stat to cite: ${esc(r.p.stat)}</span></li>`;
 document.getElementById('segment').innerHTML=`<div class="seg"><h2>Segment sheet: ${esc(D.title)}</h2><p class="muted">Auto-built from the board. Uses sample audience data in this demo.</p><h3>Fans are higher than you on</h3><ol>${up.map(item).join('')||'<li>None</li>'}</ol><h3>Fans are lower than you on</h3><ol>${dn.map(item).join('')||'<li>None</li>'}</ol><h3>Run of show (6-8 min)</h3><ol><li>Reveal the host's S tier.</li><li>Show the comparison graphic and read the biggest gap.</li><li>Defend or flip one pick live.</li><li>Call to action: vote on next week's ranking from the link in the description.</li></ol><p class="muted">Source: ${esc(D.src)}.</p></div>`}
})();
