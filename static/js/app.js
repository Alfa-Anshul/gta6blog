const API='';
let currentArticle=null;

document.addEventListener('DOMContentLoaded',()=>{
  loadStats();
  loadFeatured();
  loadArticles();
  initSR();
});

async function loadStats(){
  try{
    const r=await fetch('/api/stats');
    const d=await r.json();
    animNum(document.getElementById('statArticles'),d.articles);
    animNum(document.getElementById('statViews'),d.views);
    animNum(document.getElementById('statComments'),d.comments);
  }catch(e){console.warn('stats',e);}
}

function animNum(el,target){
  if(!el||!target)return;
  const t0=performance.now();
  (function s(now){
    const p=Math.min((now-t0)/1400,1);
    const e=1-Math.pow(1-p,3);
    el.textContent=Math.round(target*e);
    if(p<1)requestAnimationFrame(s);
  })(t0);
}

async function loadFeatured(){
  try{
    const r=await fetch('/api/articles?limit=3');
    const arts=await r.json();
    const c=document.getElementById('featuredCards');
    if(!arts.length){c.innerHTML='';return;}
    c.innerHTML=arts.slice(0,3).map((a,i)=>`
      <div class="featured-card scroll-reveal" style="animation-delay:${i*0.12}s" onclick="openArticle('${a.slug}')">
        <img src="${a.image_url}" alt="GTA 6 - ${esc(a.title)}" loading="lazy" onerror="this.src='https://img.youtube.com/vi/QdBZExpB0ao/maxresdefault.jpg'">
        <div class="featured-card-overlay">
          <div class="fc-category">${a.category.toUpperCase()}</div>
          <div class="fc-title">${esc(a.title)}</div>
          <div class="fc-subtitle">${esc(a.subtitle||'')}</div>
        </div>
      </div>`).join('');
    initSR();
  }catch(e){console.warn('featured',e);}
}

async function loadArticles(cat){
  const grid=document.getElementById('articlesGrid');
  grid.innerHTML='<div class="loading-state"><div class="loader-ring"></div><span>LOADING INTEL...</span></div>';
  try{
    const r=await fetch(cat?`/api/articles?category=${encodeURIComponent(cat)}`:'/api/articles');
    const arts=await r.json();
    document.getElementById('articleCount').textContent=`— ${arts.length} PIECE${arts.length!==1?'S':''}`;
    if(!arts.length){
      grid.innerHTML='<div class="loading-state"><span>NO INTEL FOUND</span></div>';
      return;
    }
    grid.innerHTML=arts.map((a,i)=>`
      <div class="article-card scroll-reveal" style="animation-delay:${(i%6)*0.07}s" onclick="openArticle('${a.slug}')">
        <div class="card-image">
          <img src="${a.image_url}" alt="GTA 6 - ${esc(a.title)}" loading="lazy" onerror="this.src='https://img.youtube.com/vi/QdBZExpB0ao/maxresdefault.jpg'">
          <span class="card-category-badge badge-${a.category}">${a.category.toUpperCase()}</span>
        </div>
        <div class="card-body">
          <div class="card-title">${esc(a.title)}</div>
          <div class="card-subtitle">${esc(a.subtitle||'')}</div>
          <div class="card-meta">
            <span>${a.views} VIEWS</span>
            <span class="card-read-more">READ &#8594;</span>
          </div>
        </div>
      </div>`).join('');
    initSR();
  }catch(e){
    grid.innerHTML='<div class="loading-state"><span>ERROR LOADING — CHECK API</span></div>';
    console.error(e);
  }
}

function filterCategory(cat){
  document.querySelectorAll('.cat-pill').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(l=>l.classList.remove('active'));
  if(!cat){
    document.querySelector('.cat-pill:first-child')?.classList.add('active');
    document.querySelector('.nav-link[data-page="home"]')?.classList.add('active');
    document.getElementById('sectionTitle').textContent='ALL INTEL';
  } else {
    document.querySelectorAll('.cat-pill').forEach(p=>{
      if(p.textContent.trim().toUpperCase()===cat.toUpperCase()||p.textContent.trim().toUpperCase()===catLabel(cat))p.classList.add('active');
    });
    document.querySelector(`.nav-link[data-cat="${cat}"]`)?.classList.add('active');
    document.getElementById('sectionTitle').textContent=cat.toUpperCase();
  }
  loadArticles(cat);
  closeArticle(true);
  document.getElementById('articles-section').scrollIntoView({behavior:'smooth'});
  // close mobile menu
  document.getElementById('navLinks')?.classList.remove('open');
}

function catLabel(cat){
  const map={criticism:'CRITIQUE'};
  return(map[cat]||cat).toUpperCase();
}

async function openArticle(slug){
  const det=document.getElementById('article-detail');
  const hero=document.getElementById('hero-section');
  const fs=document.getElementById('featured-strip');
  const as=document.getElementById('articles-section');
  try{
    const r=await fetch(`/api/articles/${slug}`);
    if(!r.ok)throw new Error('not found');
    const art=await r.json();
    currentArticle=art;
    hero.style.display='none';
    fs.style.display='none';
    as.style.display='none';
    det.classList.remove('hidden');
    renderDetail(art);
    renderComments(art);
    window.scrollTo({top:0,behavior:'smooth'});
  }catch(e){console.error('openArticle',e);}
}

function renderDetail(art){
  let html='';
  let sr=false;
  (art.content||[]).forEach(b=>{
    if(b.type==='stat'){
      if(!sr){html+='<div class="stats-row">';sr=true;}
      html+=`<div class="content-stat"><div class="stat-value">${esc(b.value)}</div><div class="stat-label-small">${esc(b.label)}</div></div>`;
    } else {
      if(sr){html+='</div>';sr=false;}
      if(b.type==='intro') html+=`<p class="content-intro">${esc(b.text)}</p>`;
      else if(b.type==='heading') html+=`<h2 class="content-heading">${esc(b.text)}</h2>`;
      else if(b.type==='paragraph') html+=`<p class="content-paragraph">${esc(b.text)}</p>`;
      else if(b.type==='quote') html+=`<div class="content-quote"><blockquote>${esc(b.text)}</blockquote><cite>${esc(b.source||'')}</cite></div>`;
      else if(b.type==='spec_table'){
        html+=`<div style="overflow-x:auto"><table class="spec-table"><thead><tr><th>Config</th><th>CPU</th><th>GPU</th><th>RAM</th><th>Storage</th></tr></thead><tbody>`;
        (b.rows||[]).forEach(row=>{
          html+=`<tr><td>${esc(row.tier)}</td><td>${esc(row.cpu)}</td><td>${esc(row.gpu)}</td><td>${esc(row.ram)}</td><td>${esc(row.storage)}</td></tr>`;
        });
        html+=`</tbody></table></div>`;
      }
    }
  });
  if(sr)html+='</div>';

  const tags=JSON.parse(art.tags||'[]');
  const bc=`badge-${art.category}`;

  document.getElementById('articleContent').innerHTML=
    `<img class="detail-hero-img" src="${art.image_url}" alt="GTA 6 - ${esc(art.title)}" loading="lazy" onerror="this.src='https://img.youtube.com/vi/QdBZExpB0ao/maxresdefault.jpg'">
    <span class="card-category-badge ${bc} detail-category-tag">${(art.category||'').toUpperCase()}</span>
    <h1 class="detail-title">${esc(art.title)}</h1>
    ${art.subtitle?`<p class="detail-subtitle">${esc(art.subtitle)}</p>`:''}
    <div class="detail-meta">
      <span>&#128065; ${art.views} VIEWS</span>
      <span>&#128172; ${(art.comments||[]).length} COMMENTS</span>
      <span>${tags.map(t=>'#'+t).join(' ')}</span>
    </div>
    ${html}
    <div class="vote-bar">
      <span class="vote-label">WAS THIS USEFUL?</span>
      <button class="vote-btn up" onclick="vote('up')">&#128077; <span id="upvoteCount">${art.upvotes||0}</span> YEAH</button>
      <button class="vote-btn down" onclick="vote('down')">&#128078; <span id="downvoteCount">${art.downvotes||0}</span> NAH</button>
    </div>`;
}

function renderComments(art){
  const cs=art.comments||[];
  document.getElementById('commentsSection').innerHTML=
    `<h3 class="comments-title">COMMENTS (${cs.length})</h3>
    <div class="comment-form">
      <input type="text" id="commentAuthor" placeholder="YOUR HANDLE (OPTIONAL)" maxlength="50" autocomplete="off">
      <textarea id="commentText" placeholder="DROP YOUR TAKE ON GTA 6..." maxlength="1000"></textarea>
      <button class="comment-submit" onclick="submitComment()">POST COMMENT</button>
    </div>
    <div id="commentsList">${cs.length===0?'<p class="no-comments">NO COMMENTS YET — BE FIRST</p>':cs.map(c=>rcmt(c)).join('')}</div>`;
}

function rcmt(c){
  return `<div class="comment-item"><div class="comment-author">${esc(c.author)}<span class="comment-date">${fmtDate(c.created_at)}</span></div><div class="comment-text">${esc(c.content)}</div></div>`;
}

async function submitComment(){
  if(!currentArticle)return;
  const author=(document.getElementById('commentAuthor').value||'').trim()||'Anonymous';
  const content=(document.getElementById('commentText').value||'').trim();
  if(!content)return;
  const btn=document.querySelector('.comment-submit');
  btn.textContent='POSTING...';
  btn.disabled=true;
  try{
    const r=await fetch(`/api/articles/${currentArticle.slug}/comment`,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({author,content})
    });
    if(r.ok){
      document.getElementById('commentAuthor').value='';
      document.getElementById('commentText').value='';
      const list=document.getElementById('commentsList');
      const no=list.querySelector('.no-comments');
      if(no)no.remove();
      list.insertAdjacentHTML('afterbegin',rcmt({author,content,created_at:new Date().toISOString()}));
      const h3=document.querySelector('.comments-title');
      const n=parseInt(h3.textContent.match(/\d+/)?.[0]||'0');
      h3.textContent=`COMMENTS (${n+1})`;
      loadStats();
    }
  }catch(e){console.error(e);}
  btn.textContent='POST COMMENT';
  btn.disabled=false;
}

async function vote(type){
  if(!currentArticle)return;
  try{
    const r=await fetch(`/api/articles/${currentArticle.slug}/vote`,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({type})
    });
    const d=await r.json();
    document.getElementById('upvoteCount').textContent=d.upvotes;
    document.getElementById('downvoteCount').textContent=d.downvotes;
  }catch(e){console.error(e);}
}

function closeArticle(silent=false){
  document.getElementById('article-detail').classList.add('hidden');
  document.getElementById('hero-section').style.display='';
  document.getElementById('featured-strip').style.display='';
  document.getElementById('articles-section').style.display='';
  currentArticle=null;
  if(!silent)window.scrollTo({top:0,behavior:'smooth'});
}

function showHome(){
  closeArticle(true);
  document.querySelectorAll('.cat-pill').forEach((p,i)=>{if(i===0)p.classList.add('active');else p.classList.remove('active');});
  document.querySelectorAll('.nav-link').forEach(l=>{if(l.dataset.page==='home')l.classList.add('active');else l.classList.remove('active');});
  document.getElementById('sectionTitle').textContent='ALL INTEL';
  loadArticles();
  window.scrollTo({top:0,behavior:'smooth'});
  document.getElementById('navLinks')?.classList.remove('open');
}

function toggleMenu(){
  document.getElementById('navLinks')?.classList.toggle('open');
}

function initSR(){
  if(!window.IntersectionObserver){
    document.querySelectorAll('.scroll-reveal').forEach(el=>el.classList.add('visible'));
    return;
  }
  const ob=new IntersectionObserver(entries=>{
    entries.forEach(e=>{
      if(e.isIntersecting){e.target.classList.add('visible');ob.unobserve(e.target);}
    });
  },{threshold:0.08,rootMargin:'0px 0px -40px 0px'});
  document.querySelectorAll('.scroll-reveal:not(.visible)').forEach(el=>ob.observe(el));
}

function esc(s){
  if(!s)return'';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');
}

function fmtDate(s){
  if(!s)return'';
  try{return new Date(s).toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});}catch(e){return s;}
}