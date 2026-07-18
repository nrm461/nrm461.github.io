(async function(){
const $=id=>document.getElementById(id);
(function(){var t=('ontouchstart'in window)||navigator.maxTouchPoints>0;document.body.classList.add(t?'mobile':'desktop');})();
/* Light/dark toggle (same control as the main site). Deck keeps its own
   preference and DEFAULTS TO DARK, so the portfolio's light default never
   forces the deck light. */
(function(){ const b=document.body; let m; try{m=localStorage.getItem('deckmode');}catch(e){}
	if(m==='light') b.classList.remove('dark-mode'); else b.classList.add('dark-mode');
	const t=$('toggle-mode'); if(t) t.addEventListener('click',e=>{
		if(e.target.classList.contains('black')) b.classList.add('dark-mode');
		if(e.target.classList.contains('white')) b.classList.remove('dark-mode');
		try{localStorage.setItem('deckmode', b.classList.contains('dark-mode')?'dark':'light');}catch(e){}
	});
})();
(function(){var c=$('ctrl'),h=document.querySelector('header'),sd=$('side');function p(){var hh=h?Math.round(h.getBoundingClientRect().height):0;if(c)c.style.top=hh+'px';var ch=c?Math.round(c.getBoundingClientRect().height):0;if(sd&&matchMedia('(min-width:761px)').matches)sd.style.top=(hh+ch+6)+'px';}p();addEventListener('resize',p);addEventListener('load',p);})();
const ADMIN=new URLSearchParams(location.search).get('admin')==='1';
const HUE_SW={red:'#c33',orange:'#d73',yellow:'#cb2',green:'#4a4',teal:'#2a9',blue:'#36c',purple:'#84c',magenta:'#c4a',pink:'#e79',neutral:'#888',white:'#eee',black:'#222'};
const FMT_OPTS=[['','—'],['f35','Film 35mm'],['f16','Film 16mm'],['s8','Film Super 8mm'],['f65','Film 65/70mm'],['imax','IMAX'],['tape','Tape'],['dig','Digital'],['dlf','Digital Large Format'],['anim','Animation']];
const FMT_LBL=Object.fromEntries(FMT_OPTS);
let DATA,TAGS={},FMT={films:{},frames:{}};
/* perf: fire all data fetches in parallel (was 4 serial round-trips). format cache-bust only in admin. */
const _fmtUrl='../data/deck_format.json'+(ADMIN?'?_='+Date.now():'');
const _pDATA=fetch('../data/deck.json').then(r=>r.json());
const _pTAGS=fetch('../data/deck_tags.json').then(r=>r.json()).catch(()=>({}));
const _pFMT=fetch(_fmtUrl).then(r=>r.json()).catch(()=>({films:{},frames:{}}));
const _pCR=fetch('../data/deck_credits.json').then(r=>r.json()).catch(()=>({}));
try{ DATA=await _pDATA; }
catch(e){ $('empty').style.display='block'; $('empty').textContent='deck.json not found.'; return; }
TAGS=await _pTAGS; FMT=await _pFMT;
FMT.films=FMT.films||{}; FMT.frames=FMT.frames||{};

/* flatten */
const FRAMES=[];
DATA.films.forEach((F,fi)=>{
	const ratio=F.dar||16/9;
	(F.frames||[]).forEach(fr=>{
		const key=F.slug+'/'+fr[0];
		const tg=TAGS[key]||{};
		FRAMES.push({slug:F.slug,fi,label:F.label,cats:F.cats||[],arb:F.ar,ratio,page:F.page,pslug:F.page_slug,rnd:Math.random(),
			f:fr[0],key,pal:fr[1],wts:fr[2],hue:fr[3],h:fr[4],s:fr[5],lum:fr[6],cls:fr[7]||[],
			fs:tg.fs||'',tod:tg.tod||'',ie:tg.ie||'',pp:(tg.pp===undefined?'':tg.pp),loc:tg.loc||'',
			st:tg.st||[],cmp:tg.cmp||[],lt:tg.lt||[],lty:tg.lty||[],fl:tg.fl||[],kw:tg.kw||[]});
	});
});
const hasTags=Object.keys(TAGS).length>0;
const lumBand=l=>l<25?'d':(l>60?'b':'m');
const src=x=>'../assets/deck2/'+x.slug+'/'+x.f+'.jpg';
const fmtOf=x=>FMT.frames[x.key]||FMT.films[x.slug]||'';

/* value label maps */
const NM={d_l:'Dark',m_l:'Mid',b_l:'Bright',
 warm:'Warm',cool:'Cool',mixed:'Mixed',sat:'Saturated',desat:'Desaturated',sepia:'Sepia',bw:'Black & White',
 ew:'Extreme Wide',w:'Wide',mw:'Medium Wide',m:'Medium',mcu:'Medium Close Up',cu:'Close Up',ecu:'Extreme Close Up',
 i:'Interior',e:'Exterior',
 d:'Day',n:'Night',du:'Dusk',da:'Dawn',sr:'Sunrise',ss:'Sunset',
 aer:'Aerial',ovh:'Overhead',ha:'High angle',la:'Low angle',dut:'Dutch angle',est:'Establishing',ots:'Over shoulder',cs:'Clean single','2s':'2 shot','3s':'3 shot',grp:'Group shot',ins:'Insert',
 c:'Center',lh:'Left heavy',rh:'Right heavy',bal:'Balanced',sym:'Symmetrical',shs:'Short side',
 soft:'Soft',hard:'Hard',hc:'High contrast',lc:'Low contrast',sil:'Silhouette',top:'Top light',und:'Underlight',side:'Side light',back:'Backlight',edge:'Edge light',
 day:'Daylight',sun:'Sunny',ovc:'Overcast',moon:'Moonlight',art:'Artificial',prac:'Practical',fluo:'Fluorescent',fire:'Firelight',mix:'Mixed light',
 prod:'Product',food:'Food',bev:'Beverage',veh:'Vehicle',logo:'Logo/branding',hand:'Hands',anim:'Animal/pet',scr:'Device screen',bty:'Beauty application',sprt:'Sport/action',dnc:'Dance/performance',drv:'Driving',
 '0':'None','1':'1','2':'2','3':'3','4':'4','5':'5','6':'6+'};
const nm=v=>NM[v]||v;
const COLOR_LBL={red:'Red',orange:'Orange',yellow:'Yellow',green:'Green',teal:'Teal',blue:'Blue',purple:'Purple',magenta:'Magenta',pink:'Pink',neutral:'Neutral',white:'White',black:'Black',warm:'Warm',cool:'Cool',mixed:'Mixed',sat:'Saturated',desat:'Desaturated',sepia:'Sepia',bw:'Black & White'};

const SECTIONS=[
 {key:'film',label:'Film',type:'film',hide:1,get:x=>[x.slug]},
 {key:'cats',label:'Genre',get:x=>x.cats},
 {key:'color',label:'Color',combo:1,noscroll:1,hues:['red','orange','yellow','green','teal','blue','magenta','pink'],classes:['warm','cool','mixed','sat','desat','bw'],get:x=>[x.hue,...x.cls],order:['cool','warm','mixed','sat','desat','bw','red','orange','yellow','green','teal','blue','magenta','pink'],lblmap:COLOR_LBL},
 {key:'lum',label:'Brightness',get:x=>[lumBand(x.lum)+'_l'],order:['d_l','m_l','b_l']},
 {key:'fmt',label:'Format',get:x=>{const f=fmtOf(x);return f?[f]:[]},order:FMT_OPTS.map(o=>o[0]).filter(Boolean),lblmap:FMT_LBL},
 {key:'arb',label:'Aspect Ratio',get:x=>[x.arb]},
 {key:'fs',label:'Frame Size',ai:1,get:x=>x.fs?[x.fs]:[],order:['ew','w','mw','m','mcu','cu','ecu']},
 {key:'st',label:'Shot Type',ai:1,multi:1,get:x=>x.st,order:['aer','ovh','ha','la','dut','est','ots','cs','2s','3s','grp','ins']},
 {key:'cmp',label:'Composition',ai:1,multi:1,get:x=>x.cmp,order:['c','lh','rh','bal','sym','shs']},
 {key:'lt',label:'Lighting',ai:1,multi:1,get:x=>x.lt,order:['soft','hard','hc','lc','sil','top','und','side','back','edge']},
 {key:'lty',label:'Lighting Type',ai:1,multi:1,get:x=>x.lty,order:['day','sun','ovc','moon','art','prac','fluo','fire','mix']},
 {key:'tod',label:'Time of Day',ai:1,get:x=>x.tod&&x.tod!=='x'?[x.tod]:[],order:['d','n','du','da','sr','ss']},
 {key:'ie',label:'Interior / Exterior',ai:1,get:x=>x.ie&&x.ie!=='x'?[x.ie]:[],order:['i','e']},
 {key:'pp',label:'Number of People',ai:1,get:x=>x.pp!==''?[String(x.pp)]:[],order:['0','1','2','3','4','5','6']},
 {key:'fl',label:'Commercial Flags',ai:1,multi:1,get:x=>x.fl,order:['prod','food','bev','veh','logo','hand','anim','scr','bty','sprt','dnc','drv']},
];
const state={sets:{},pick:null,q:'',sort:'shuffle'};
SECTIONS.forEach(s=>{if(s.type!=='picker')state.sets[s.key]=new Set();});
const filmLabel={}; DATA.films.forEach(F=>filmLabel[F.slug]=F.label);
let filmCr={}; try{ filmCr=await _pCR; }catch(e){}
const _DL=(typeof window!=='undefined'&&window.DECK_LANDING)||[]; // films on the main landing grid
let landingSet=new Set(_DL), landingActive=false, landingDismissed=(_DL.length===0); // default view scoped to landing; any search/filter reveals the full library
const openSecs=new Set(['color']);
const listScroll={};

function hex2rgb(h){h=h.replace('#','');return [parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)];}
function near(pal,rgb,tol){for(const p of pal){const r=parseInt(p.slice(0,2),16)-rgb[0],g=parseInt(p.slice(2,4),16)-rgb[1],b=parseInt(p.slice(4,6),16)-rgb[2];if(Math.sqrt(r*r*.6+g*g+b*b*.4)<tol)return true;}return false;}
function matchesQ(x,q){ if(x.label.toLowerCase().includes(q))return true; for(const k of x.kw)if(k.includes(q))return true; return false; }
function passes(x,skipKey){
	if(state.q && !matchesQ(x,state.q)) return false;
	if(state.pick && skipKey!=='pick' && !near(x.pal,state.pick,+($('tol')?.value||60))) return false;
	for(const s of SECTIONS){
		if(s.type==='picker'||s.key===skipKey) continue;
		const set=state.sets[s.key]; if(!set||!set.size) continue;
		if(s.combo){
			const selH=[...set].filter(v=>s.hues.includes(v));
			const selC=[...set].filter(v=>s.classes.includes(v));
			if(selH.length && !selH.includes(x.hue)) return false;
			if(selC.length && !selC.some(c=>x.cls.includes(c))) return false;
			continue;
		}
		const vals=s.get(x);
		if(!vals.some(v=>set.has(v))) return false;
	}
	return true;
}
function optName(s,v){ return s.type==='film'?filmLabel[v]:(s.lblmap?s.lblmap[v]:nm(v)); }

function buildSidebar(){
	const sideScroll=$('side').scrollTop;
	const root=$('secs'); root.innerHTML='';
	SECTIONS.forEach(s=>{
		if(s.hide) return;                 // kept in SECTIONS (film set drives project routing) but not shown in the menu
		if(s.ai&&!hasTags) return;
		if(s.key==='fmt'&&Object.keys(FMT.films).length===0&&Object.keys(FMT.frames).length===0&&!ADMIN) return;
		const sec=document.createElement('div'); sec.className='sec'; if(openSecs.has(s.key))sec.classList.add('open');
		const h=document.createElement('div'); h.className='sec-h';
		h.innerHTML='<span>'+s.label+'</span><span class="car">&#9660;</span>';
		h.onclick=()=>{sec.classList.toggle('open'); sec.classList.contains('open')?openSecs.add(s.key):openSecs.delete(s.key);};
		const b=document.createElement('div'); b.className='sec-b';
		sec.appendChild(h); sec.appendChild(b); root.appendChild(sec);
		if(s.type==='picker'){
			b.innerHTML='<div id="pickrow"><input type="color" id="pick" value="#3a6ea5"><input type="range" id="tol" min="20" max="120" value="60"><button id="pickon">match</button></div>';
			$('pickon').onclick=()=>{state.pick=state.pick?null:hex2rgb($('pick').value);$('pickon').classList.toggle('on',!!state.pick);apply();};
			$('pick').oninput=()=>{if(state.pick){state.pick=hex2rgb($('pick').value);apply();}};
			$('tol').oninput=()=>{if(state.pick)apply();};
			return;
		}
		const counts={};
		FRAMES.forEach(x=>{ if(passes(x,s.key)) s.get(x).forEach(v=>counts[v]=(counts[v]||0)+1); });
		let keys=Object.keys(counts); state.sets[s.key].forEach(v=>{if(!keys.includes(v))keys.push(v);});
		if(s.order) keys=keys.filter(k=>s.order.indexOf(k)>=0).sort((a,b)=>s.order.indexOf(a)-s.order.indexOf(b));
		else keys.sort((a,b)=>optName(s,a).toLowerCase()<optName(s,b).toLowerCase()?-1:1);
		let list=b;
		if((s.type==='film'||keys.length>14)&&!s.noscroll){
			const fs=document.createElement('input'); fs.className='subsearch'; fs.placeholder=s.type==='film'?'find film…':'filter…'; fs.autocomplete='off';
			fs.oninput=()=>{ list.querySelectorAll('.opt').forEach(o=>{o.style.display=o.dataset.t.includes(fs.value.toLowerCase())?'':'none';}); };
			b.appendChild(fs);
			list=document.createElement('div'); list.className='scrolllist'; b.appendChild(list);
			list.addEventListener('scroll',()=>{listScroll[s.key]=list.scrollTop;});
		}
		keys.forEach(v=>{
			const on=state.sets[s.key].has(v);
			const o=document.createElement('div'); o.className='opt'+(on?' on':'')+(counts[v]?'':' zero'); o.dataset.t=optName(s,v).toLowerCase();
			o.innerHTML='<span class="ol">'+optName(s,v)+'</span><span class="n">'+(counts[v]?counts[v].toLocaleString():'')+'</span>';
			o.onclick=()=>{ state.sets[s.key].has(v)?state.sets[s.key].delete(v):state.sets[s.key].add(v); apply(); };
			list.appendChild(o);
		});
		if(list!==b) list.scrollTop=listScroll[s.key]||0;
	});
	$('side').scrollTop=sideScroll;
}
function buildChips(){
	const c=$('chips'); c.innerHTML='';
	const add=(label,val,off)=>{const el=document.createElement('span');el.className='chip';el.innerHTML=label+': <b>'+val+'</b><span class="x">&#10005;</span>';el.querySelector('.x').onclick=off;c.appendChild(el);};
	if(state.q) add('Search',state.q,()=>{state.q='';$('search').value='';apply();});
	if(state.pick) add('Color match','#'+state.pick.map(v=>v.toString(16).padStart(2,'0')).join(''),()=>{state.pick=null;$('pickon')&&$('pickon').classList.remove('on');apply();});
	SECTIONS.forEach(s=>{ if(s.type==='picker')return; if(s.key==='film'&&curProject)return; state.sets[s.key].forEach(v=>add(s.label,optName(s,v),()=>{state.sets[s.key].delete(v);apply();})); });
}

/* justified grid */
let shown=[];
const TARGET_H=158, GAP=5;
let layout=[], totalH=0;
const rendered=new Map();          // rowIndex -> row element (only visible rows live in DOM)
function computeLayout(){
	const W=$('grid').clientWidth; layout=[]; totalH=0; if(W<50) return;
	if(window.innerWidth<=760){          // mobile: 3-up square grid (ShotDeck style)
		const cols=3, cw=(W-GAP*(cols-1))/cols; let top=10;
		for(let i=0;i<shown.length;i+=cols){ layout.push({top,h:cw,s:i,e:Math.min(i+cols,shown.length),sq:cw}); top+=cw+GAP; }
		totalH=top; return;
	}
	let i=0, top=10;
	while(i<shown.length){
		let j=i,sum=0;
		while(j<shown.length){ sum+=shown[j].ratio*TARGET_H+GAP; j++; if(sum-GAP>=W) break; }
		let denom=0; for(let k=i;k<j;k++) denom+=shown[k].ratio*TARGET_H;
		let h=TARGET_H*((W-GAP*((j-i)-1))/denom);
		if(j>=shown.length && h>TARGET_H*1.3) h=TARGET_H;
		layout.push({top,h,s:i,e:j}); top+=h+GAP; i=j;
	}
	totalH=top;
}
function buildRow(ri){
	const r=layout[ri];
	const row=document.createElement('div'); row.className='row';
	row.style.cssText='position:absolute;left:0;right:0;top:'+r.top+'px;margin:0';
	for(let idx=r.s; idx<r.e; idx++){
		const x=shown[idx];
		const cell=document.createElement('div'); cell.className='cell'+(ADMIN?' admtag':'');
		if(r.sq){ cell.style.width=r.sq+'px'; cell.style.height=r.sq+'px'; } else { cell.style.width=(x.ratio*r.h)+'px'; cell.style.height=r.h+'px'; }
		cell.dataset.label=x.label; cell.dataset.i=idx;
		if(ADMIN){const f=fmtOf(x); if(f)cell.dataset.fmt=FMT_LBL[f];}
		const img=document.createElement('img'); img.loading='lazy'; img.decoding='async'; img.src=src(x); cell.appendChild(img);
		cell.onclick=()=>openOv(idx);
		row.appendChild(cell);
	}
	return row;
}
function firstRow(y){ let a=0,b=layout.length-1,ans=0; while(a<=b){const m=(a+b)>>1; if(layout[m].top+layout[m].h>=y){ans=m;b=m-1;}else a=m+1;} return ans<0?0:ans; }
function lastRow(y){ let a=0,b=layout.length-1,ans=layout.length-1; while(a<=b){const m=(a+b)>>1; if(layout[m].top<=y){ans=m;a=m+1;}else b=m-1;} return ans<0?0:ans; }
function renderVisible(){
	if(!layout.length) return;
	const sy=window.scrollY||window.pageYOffset||0;
	const gt=$('grid').getBoundingClientRect().top + sy;   // grid's document offset
	const buf=1200;
	const lo=firstRow(sy-gt-buf), hi=lastRow(sy-gt+window.innerHeight+buf);
	for(const [ri,el] of rendered){ if(ri<lo||ri>hi){ el.remove(); rendered.delete(ri); } }
	for(let ri=lo; ri<=hi; ri++){ if(!rendered.has(ri)){ const el=buildRow(ri); $('grid').appendChild(el); rendered.set(ri,el); } }
}
function resetGrid(){
	rendered.clear(); $('grid').innerHTML='';
	computeLayout();
	$('grid').style.position='relative'; $('grid').style.padding='0'; $('grid').style.height=totalH+'px';
	renderVisible();
}
let raf=0; window.addEventListener('scroll',()=>{ if(raf) return; raf=requestAnimationFrame(()=>{ raf=0; renderVisible(); }); },{passive:true});
let rto; window.addEventListener('resize',()=>{ clearTimeout(rto); rto=setTimeout(resetGrid,150); });

/* ---- project routing (ShotDeck-style #/movie/<slug>~<Name>) ---- */
let curProject=null;
function projSlug(){ const m=location.hash.match(/^#\/movie\/([^~\/?]+)/); return m?decodeURIComponent(m[1]):null; }
function goProject(slug,label){ const nm=(label||slug).replace(/\s*\|\s*/g,' '); location.hash='#/movie/'+slug+'~'+encodeURIComponent(nm).replace(/%20/g,'+'); }
function exitProject(){ curProject=null; SECTIONS.forEach(s=>state.sets[s.key]&&state.sets[s.key].clear()); state.pick=null;$('pickon')&&$('pickon').classList.remove('on'); state.q='';$('search').value=''; if(location.hash) history.replaceState(null,'',location.pathname+location.search); apply(); }
function route(){
	const slug=projSlug();
	if(slug!==null && filmLabel[slug]!==undefined){
		curProject=slug;
		SECTIONS.forEach(s=>state.sets[s.key]&&state.sets[s.key].clear());
		state.pick=null;$('pickon')&&$('pickon').classList.remove('on'); state.q='';$('search').value='';
		state.sets['film'].add(slug);
	} else curProject=null;
	apply();
}
window.addEventListener('hashchange',route);
function renderProjectHeader(){
	const ph=$('projhead');
	if(!curProject){ ph.style.display='none'; ph.innerHTML=''; return; }
	const F=DATA.films.find(f=>f.slug===curProject)||{};
	const label=filmLabel[curProject]||curProject;
	const nice=label.replace(' | ',' &mdash; &ldquo;')+(label.includes(' | ')?'&rdquo;':'')+' <span>('+((F.cats&&F.cats[0])||'')+')</span>';
	const cr=filmCr[curProject]||{};
	const crows=[]; if(cr.d)crows.push(['Director',cr.d]); if(cr.dp)crows.push(['Cinematographer',cr.dp]); if(cr.e)crows.push(['Editor',cr.e]);
	const n=shown.length;
	ph.innerHTML='<a id="projback">&lsaquo; All shots</a><div id="projtitle">'+nice+'</div><div id="projcount">'+n+' shot'+(n===1?'':'s')+'</div>'+(crows.length?'<div id="projcredits">'+crows.map(r=>'<div><b>'+r[0]+'</b><span>'+r[1]+'</span></div>').join('')+'</div>':'');
	$('projback').onclick=exitProject;
	ph.style.display='block';
}
let sidebarQueued=false;
function apply(){
	const anyFilter = !!state.q || !!state.pick || SECTIONS.some(s=>state.sets[s.key]&&state.sets[s.key].size);
	shown=FRAMES.filter(x=>passes(x,null));
	landingActive = (!anyFilter && !curProject && landingSet.size>0 && !landingDismissed);
	if(landingActive) shown=shown.filter(x=>landingSet.has(x.slug));
	if(state.sort==='hue')shown.sort((a,b)=>(a.s<12)-(b.s<12)||a.h-b.h||a.lum-b.lum);
	else if(state.sort==='lum')shown.sort((a,b)=>a.lum-b.lum);
	else if(state.sort==='shuffle')shown.sort((a,b)=>a.rnd-b.rnd);
	const nf=new Set(shown.map(x=>x.slug)).size;
		$('showing').innerHTML=(anyFilter||curProject)?('<b>'+shown.length.toLocaleString()+'</b> result'+(shown.length===1?'':'s')):'';
		$('empty').style.display=shown.length?'none':'block';
		window.scrollTo(0,0); resetGrid(); buildChips(); renderProjectHeader();
		/* perf: paint the grid first; build the heavy facet-count sidebar off the critical path (coalesced) */
		if(!sidebarQueued){ sidebarQueued=true; (window.requestIdleCallback||(cb=>setTimeout(cb,0)))(()=>{ sidebarQueued=false; buildSidebar(); }, {timeout:200}); }
	if(ADMIN)buildFmtPanel();
}
$('sort').value=state.sort; $('sort').onchange=e=>{state.sort=e.target.value;apply();};
let qto; $('search').oninput=e=>{clearTimeout(qto);qto=setTimeout(()=>{state.q=e.target.value.trim().toLowerCase();apply();},250);};
/* blinking terminal cursor on the search field — shown only when empty & unfocused */
(function(){var sw=$('searchwrap'),si=$('search');if(!sw||!si)return;function tog(){sw.classList.toggle('typing',document.activeElement===si||si.value.length>0);}si.addEventListener('focus',tog);si.addEventListener('blur',tog);si.addEventListener('input',tog);tog();})();
$('clearall').onclick=()=>{SECTIONS.forEach(s=>state.sets[s.key]&&state.sets[s.key].clear());state.pick=null;state.q='';$('search').value='';curProject=null;landingDismissed=false;if(location.hash)history.replaceState(null,'',location.pathname+location.search);apply();};
let showPal=false;
function isNarrow(){return matchMedia('(max-width:760px)').matches}
function railReset(){ if(!isNarrow()) requestAnimationFrame(()=>{ if(typeof resetGrid==='function') resetGrid(); }); }
function openSide(){ if(isNarrow()){$('side').classList.add('open');$('sideback').classList.add('on');} else {$('deckrow').classList.remove('railoff'); railReset();} $('fbtn').classList.add('on'); }
function closeSide(){ if(isNarrow()){$('side').classList.remove('open');$('sideback').classList.remove('on');} else {$('deckrow').classList.add('railoff'); railReset();} $('fbtn').classList.remove('on'); }
$('fbtn').onclick=()=>{ if(isNarrow()){ $('side').classList.contains('open')?closeSide():openSide(); } else { $('deckrow').classList.contains('railoff')?openSide():closeSide(); } };
if(!isNarrow()) $('fbtn').classList.add('on');
$('sideclose').onclick=closeSide; $('sideback').onclick=closeSide;
$('paltoggle').querySelector('input').onchange=e=>{ showPal=e.target.checked; $('ovpal').style.display=showPal?'':'none'; };

/* overlay */
const arrName=(x,f)=>(x[f]||[]).map(nm).join(', ');
function simScore(a,b){ let s=0;
	if(a.hue===b.hue)s+=2;
	s+=a.cls.filter(c=>b.cls.includes(c)).length*1.5;
	s+=a.st.filter(v=>b.st.includes(v)).length*1.2;
	s+=a.lt.filter(v=>b.lt.includes(v)).length;
	s+=a.cmp.filter(v=>b.cmp.includes(v)).length*0.8;
	s+=a.lty.filter(v=>b.lty.includes(v)).length*0.8;
	if(a.fs&&a.fs===b.fs)s+=1;
	if(a.tod&&a.tod===b.tod)s+=0.6;
	if(a.ie&&a.ie===b.ie)s+=0.4;
	if(a.pp!==''&&a.pp===b.pp)s+=0.4;
	if(Math.abs(a.lum-b.lum)<18)s+=0.5;
	return s;
}
let ovIdx=-1, ovList=[];
let ovGridList=[], ovGridTab='sim';
function justify(el,list,targetH){
	el.innerHTML=''; if(!list||!list.length)return;
	const W=el.clientWidth||960, GAP=5;
	if(window.innerWidth<=760){          // mobile: 3-up square, like ShotDeck
		const cols=3, cw=(W-GAP*(cols-1))/cols; let row;
		list.forEach((f,k)=>{ if(k%cols===0){ row=document.createElement('div'); row.className='ovrow'; el.appendChild(row); }
			const im=document.createElement('img'); im.src=src(f); im.loading='lazy'; im.style.width=cw+'px'; im.style.height=cw+'px'; const idx=k; im.onclick=()=>openOv(idx,list); row.appendChild(im); });
		return;
	}
	let i=0;
	while(i<list.length){
		let sum=0,j=i;
		while(j<list.length){ sum+=list[j].ratio*targetH+GAP; j++; if(sum-GAP>=W)break; }
		let denom=0; for(let k=i;k<j;k++)denom+=list[k].ratio*targetH;
		let h=targetH*((W-GAP*((j-i)-1))/denom);
		if(j>=list.length && (sum-GAP)<W) h=Math.min(h,targetH);
		const row=document.createElement('div'); row.className='ovrow';
		for(let k=i;k<j;k++){ const f=list[k]; const im=document.createElement('img'); im.src=src(f); im.loading='lazy'; im.style.height=Math.round(h)+'px'; im.style.width=Math.round(f.ratio*h)+'px'; const idx=k; im.onclick=()=>openOv(idx,list); row.appendChild(im); }
		el.appendChild(row); i=j;
	}
}
/* detail gallery uses CSS grid; no JS relayout */
function openOv(i,list){
	ovList=list||shown; ovIdx=i; const x=ovList[i]; if(!x) return;
	$('ovtitle').textContent=x.label;
		$('ovimg').src=src(x);
		$('ovpal').innerHTML=x.pal.map((p,k)=>'<span style="background:#'+p+'" data-h="#'+p+'"></span>').join('');
		$('ovpal').querySelectorAll('span').forEach(el=>el.onclick=()=>navigator.clipboard.writeText(el.dataset.h));
		$('ovpal').style.display=showPal?'':'none';
		const cr=filmCr[x.slug]||{};
		let hero='';
		if(cr.d)hero+='<p>Dir. '+cr.d+'</p>';
		if(cr.dp)hero+='<p>DP: '+cr.dp+'</p>';
		if(cr.e)hero+='<p>Edit: '+cr.e+'</p>';
		hero+='<p>Color: <a href="https://instagram.com/nick__metcalf" target="_blank" rel="noopener">@nick__metcalf</a></p>';
		$('ovcredits').innerHTML=hero;
		const TOD={d:'Day',n:'Night',du:'Dusk',da:'Dawn',sr:'Sunrise',ss:'Sunset'};
					const low=s=>String(s).toLowerCase();
			const slash=a=>a.filter(Boolean).map(low).join(' / ');
			// filters block: "Label: value / value" — label capitalised, values lowercase & light grey; empties skipped
			const rows=[
				['Color',slash([nm(x.hue),...x.cls.map(nm)])],
				['Brightness',low(NM[lumBand(x.lum)+'_l'])],
				['Aspect',low(x.arb)],
				['Frame size',x.fs?low(nm(x.fs)):''],
				['Shot type',slash((x.st||[]).map(nm))],
				['Composition',slash((x.cmp||[]).map(nm))],
				['Lighting',slash((x.lt||[]).map(nm))],
				['Lighting type',slash((x.lty||[]).map(nm))],
				['Time of day',x.tod&&TOD[x.tod]?low(TOD[x.tod]):''],
				['Int / ext',x.ie==='i'?'interior':x.ie==='e'?'exterior':''],
				['People',x.pp!==''?low(nm(String(x.pp))):''],
				['Location',x.loc==='loc'?'location':x.loc==='stu'?'studio':''],
				['Flags',slash((x.fl||[]).map(nm))],
				['Format',fmtOf(x)?low(FMT_LBL[fmtOf(x)]):''],
			];
			let meta='<p class="spacer">&nbsp;</p>'+rows.filter(r=>r[1]).map(r=>'<p><span class="ml">'+r[0]+':</span> <span class="mv">'+r[1]+'</span></p>').join('');
			if(x.page&&x.pslug)meta+='<p class="spacer">&nbsp;</p><p><a class="ovfilm" href="../'+x.pslug+'/" target="_blank" rel="noopener">[ open film page ]</a></p>';
			$('ovmeta').innerHTML=meta;
			$('ovkw').innerHTML=x.kw.length?'<p class="ovkw">'+x.kw.map(k=>'<span class="kwtag">'+k+'</span>').join(' ')+'</p>':'';
			$('ovkw').querySelectorAll('.kwtag').forEach(el=>el.onclick=()=>{state.q=el.textContent;$('search').value=el.textContent;closeOv();apply();});
	// admin per-still format override
	const adm=$('ovadm');
	if(ADMIN){
		adm.classList.add('on');
		const cur=FMT.frames[x.key]||'';
		adm.innerHTML='<b>OVERRIDE FORMAT (this still):</b><select id="ovfmt">'+FMT_OPTS.map(o=>'<option value="'+o[0]+'"'+(o[0]===cur?' selected':'')+'>'+o[1]+'</option>').join('')+'</select> <span style="color:var(--dim);font-size:10px">film default: '+(FMT.films[x.slug]?FMT_LBL[FMT.films[x.slug]]:'none')+'</span>';
		$('ovfmt').onchange=e=>{ if(e.target.value)FMT.frames[x.key]=e.target.value; else delete FMT.frames[x.key]; fmtDirty=true; $('fmtsave').disabled=false; };
	} else adm.classList.remove('on');
	const more=FRAMES.filter(f=>f.slug===x.slug&&f!==x).slice(0,120);
	const sim=FRAMES.filter(f=>f.slug!==x.slug).map(f=>[f,simScore(x,f)]).filter(a=>a[1]>0).sort((a,b)=>b[1]-a[1]).slice(0,60).map(a=>a[0]);
	$('ovgrid').innerHTML=''; more.forEach((f,mi)=>{const im=document.createElement('img');im.src=src(f);im.loading='lazy';im.decoding='async';im.onclick=()=>openOv(mi,more);$('ovgrid').appendChild(im);});
	$('ov').classList.add('open'); $('ov').scrollTop=0; document.body.style.overflow='hidden';
}
function closeOv(){$('ov').classList.remove('open');document.body.style.overflow='';}
$('close').onclick=closeOv;
$('ov').addEventListener('click',e=>{if(e.target.id==='ov')closeOv();});
$('prev').onclick=()=>openOv((ovIdx-1+ovList.length)%ovList.length,ovList);
$('next').onclick=()=>openOv((ovIdx+1)%ovList.length,ovList);
document.addEventListener('keydown',e=>{ if(!$('ov').classList.contains('open'))return; if(e.key==='Escape')closeOv(); if(e.key==='ArrowLeft')$('prev').click(); if(e.key==='ArrowRight')$('next').click(); });
/* swipe left/right in the detail overlay -> next/prev still (horizontal beats vertical scroll) */
let _tsx=0,_tsy=0,_tst=0;
$('ov').addEventListener('touchstart',e=>{const t0=e.changedTouches[0];_tsx=t0.clientX;_tsy=t0.clientY;_tst=e.timeStamp;},{passive:true});
$('ov').addEventListener('touchend',e=>{ if(!$('ov').classList.contains('open'))return; const t0=e.changedTouches[0],dx=t0.clientX-_tsx,dy=t0.clientY-_tsy; if(Math.abs(dx)>45&&Math.abs(dx)>Math.abs(dy)*1.4&&(e.timeStamp-_tst)<600){ if(dx<0)$('next').click(); else $('prev').click(); } },{passive:true});

/* ---- FORMAT ADMIN ---- */
let fmtDirty=false;
function buildFmtPanel(){
	if(!ADMIN)return;
	const counts={}; FRAMES.forEach(x=>counts[x.slug]=(counts[x.slug]||0)+1);
	const rows=DATA.films.map(F=>F.slug).sort((a,b)=>filmLabel[a].toLowerCase()<filmLabel[b].toLowerCase()?-1:1);
	$('fmtrows').innerHTML='';
	rows.forEach(sl=>{
		const r=document.createElement('div'); r.className='fmtrow';
		const cur=FMT.films[sl]||'';
		r.innerHTML='<span class="fn" title="'+filmLabel[sl]+'">'+filmLabel[sl]+'</span><select>'+FMT_OPTS.map(o=>'<option value="'+o[0]+'"'+(o[0]===cur?' selected':'')+'>'+o[1]+'</option>').join('')+'</select><span class="cnt">'+(counts[sl]||0)+'</span>';
		r.querySelector('select').onchange=e=>{ if(e.target.value)FMT.films[sl]=e.target.value; else delete FMT.films[sl]; fmtDirty=true; $('fmtsave').disabled=false; };
		$('fmtrows').appendChild(r);
	});
}
$('fmtsave').onclick=async()=>{
	const token=localStorage.getItem('ghtoken');
	if(!token){$('fmtstatus').textContent='No GitHub token in this browser (open admin page first).';return;}
	$('fmtsave').disabled=true; $('fmtstatus').textContent='Saving…';
	try{
		const api='https://api.github.com/repos/nrm461/nrm461.github.io/contents/data/deck_format.json';
		let sha=null;
		try{ const g=await (await fetch(api,{headers:{Authorization:'token '+token,Accept:'application/vnd.github+json'}})).json(); sha=g.sha; }catch(e){}
		const body={message:'deck: update format tags',content:btoa(unescape(encodeURIComponent(JSON.stringify({films:FMT.films,frames:FMT.frames},null,1))))};
		if(sha)body.sha=sha;
		const r=await fetch(api,{method:'PUT',headers:{Authorization:'token '+token,Accept:'application/vnd.github+json'},body:JSON.stringify(body)});
		if(r.ok){$('fmtstatus').textContent='Saved ✓ (rebuild not needed — reload to see facet counts)';fmtDirty=false;apply();}
		else{$('fmtstatus').textContent='Save failed: '+r.status;$('fmtsave').disabled=false;}
	}catch(e){$('fmtstatus').textContent='Error: '+e.message;$('fmtsave').disabled=false;}
};
if(ADMIN){ $('brand').classList.add('adm'); $('brand').textContent='DECK · ADMIN'; $('fmtpanel').classList.add('on'); $('main').style.marginRight='340px'; }

route();
})();