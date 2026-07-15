/* Device class (ProdCo uses .desktop / .mobile on body for hover behavior) */
(function(){
	var isTouch = ('ontouchstart' in window) || navigator.maxTouchPoints > 0;
	document.body.classList.add(isTouch ? 'mobile' : 'desktop');
})();

/* Viewport height var (mobile-safe 100vh) */
(function(){
	function setH(){ document.documentElement.style.setProperty('--h', window.innerHeight + 'px'); }
	setH(); window.addEventListener('resize', setH);
})();

/* Lazy loading: swap data-src in when near viewport, fade in */
(function(){
	var imgs = document.querySelectorAll('img.lazy');
	if(!('IntersectionObserver' in window)){
		imgs.forEach ? imgs.forEach(load) : Array.prototype.forEach.call(imgs, load);
		return;
	}
	var io = new IntersectionObserver(function(entries){
		entries.forEach(function(en){
			if(en.isIntersecting){ load(en.target); io.unobserve(en.target); }
		});
	}, { rootMargin: '200px' });
	Array.prototype.forEach.call(imgs, function(img){ io.observe(img); });
	function load(img){
		var src = img.getAttribute('data-src');
		if(!src){ img.classList.remove('lazy'); return; }
		var pre = new Image();
		pre.onload = function(){ img.src = src; img.classList.remove('lazy'); };
		pre.onerror = function(){ img.classList.remove('lazy'); };
		pre.src = src;
	}
})();

/* Black & white toggle (desktop only, persisted) */
(function(){
	var toggle = document.getElementById('toggle-mode');
	try{
		if(localStorage.getItem('mode') === 'dark') document.body.classList.add('dark-mode');
	}catch(e){}
	if(!toggle) return;
	toggle.addEventListener('click', function(e){
		if(e.target.classList.contains('black')) document.body.classList.add('dark-mode');
		if(e.target.classList.contains('white')) document.body.classList.remove('dark-mode');
		try{ localStorage.setItem('mode', document.body.classList.contains('dark-mode') ? 'dark' : 'light'); }catch(e){}
	});
})();

/* Archive category filtering */
(function(){
	var filters = document.querySelectorAll('.archive-filter');
	if(!filters.length) return;
	var cards = document.querySelectorAll('.module-project');
	function chipFor(cat){
		var found = null;
		Array.prototype.forEach.call(filters, function(f){ if(f.getAttribute('data-filter') === cat) found = f; });
		return found;
	}
	function applyFilter(cat){
		if(!chipFor(cat)) cat = 'all';
		Array.prototype.forEach.call(filters, function(x){ x.classList.toggle('active', x.getAttribute('data-filter') === cat); });
		Array.prototype.forEach.call(cards, function(c){
			var dc = c.getAttribute('data-category') || '';
			var show = (cat === 'all') || (('|' + dc + '|').indexOf('|' + cat + '|') !== -1);
			c.classList.toggle('filtered-out', !show);
		});
		try{ sessionStorage.setItem('archiveFilter', cat); }catch(e){}
	}
	Array.prototype.forEach.call(filters, function(f){
		f.addEventListener('click', function(){ applyFilter(f.getAttribute('data-filter')); });
	});
	/* re-apply the last-used filter (e.g. after closing a project and returning to the archive) */
	var saved = 'all';
	try{ saved = sessionStorage.getItem('archiveFilter') || 'all'; }catch(e){}
	if(saved !== 'all') applyFilter(saved);
})();

/* Navigation context: arrows on project pages follow the grid you came from */
(function(){
	var b = document.body.classList;
	try{
		if(b.contains('page-hidden')) sessionStorage.setItem('navctx', 'hidden');
		else if(b.contains('page-archive')) sessionStorage.setItem('navctx', 'archive');
		else if(b.contains('page-index')) sessionStorage.setItem('navctx', 'landing');
	}catch(e){}
	if(!b.contains('page-project') || !window.NAV_LISTS) return;
	var ctx = 'archive';
	try{ ctx = sessionStorage.getItem('navctx') || 'archive'; }catch(e){}
	var slug = location.pathname.replace(/\/+$/, '').split('/').pop();
	var list = window.NAV_LISTS[ctx] || [];
	if(list.indexOf(slug) === -1){ ctx = 'archive'; list = window.NAV_LISTS.archive || []; }
	var i = list.indexOf(slug);
	if(i === -1) return;
	var prev = document.getElementById('prev'), next = document.getElementById('next'), close = document.getElementById('close');
	if(prev) prev.href = '../' + list[(i - 1 + list.length) % list.length] + '/';
	if(next) next.href = '../' + list[(i + 1) % list.length] + '/';
	if(close) close.href = ctx === 'archive' ? '../archive/' : (ctx === 'hidden' ? '../hidden/' : '../');
})();

/* Remember grid scroll position: restore when returning via [CLOSE] / back */
(function(){
	if(!document.body.classList.contains('page-index') && !document.body.classList.contains('page-works')) return;
	var key = 'scroll:' + location.pathname;
	try{
		var saved = sessionStorage.getItem(key);
		if(saved !== null){
			var y = parseInt(saved, 10);
			window.scrollTo(0, y);
			window.addEventListener('load', function(){ window.scrollTo(0, y); });
		}
	}catch(e){}
	window.addEventListener('pagehide', function(){
		try{ sessionStorage.setItem(key, String(window.scrollY || window.pageYOffset || 0)); }catch(e){}
	});
})();

/* Video facades: click swaps thumbnail for autoplaying Vimeo player (supports multiple per page) */
(function(){
	var facades = document.querySelectorAll('.video-facade');
	if(!facades.length) return;
	Array.prototype.forEach.call(facades, function(f){
		f.addEventListener('click', function(){
			var id = f.getAttribute('data-vimeo');
			var params = 'badge=0&autopause=0&player_id=0&title=0&byline=0&portrait=0' +
				'&vimeo_logo=0&pip=0&cc=0&transcript=0&airplay=0&chromecast=0' +
				'&watch_full_video=0&dnt=1';
			/* mobile can only autoplay muted (unmute pill) — load without autoplay there instead */
			if(!document.body.classList.contains('mobile')) params += '&autoplay=1';
			var box = f.querySelector('div');
			box.innerHTML = '<iframe src="https://player.vimeo.com/video/' + id + '?' + params +
				'" frameborder="0" allow="autoplay; fullscreen; picture-in-picture; encrypted-media" title="video"></iframe>';
			f.style.cursor = 'default';
		}, {once:true});
	});
})();

/* Mobile swipe navigation between project pages */
(function(){
	var prev = document.getElementById('prev'), next = document.getElementById('next');
	if(!prev || !next || !document.body.classList.contains('page-project')) return;
	var x0 = null, y0 = null;
	document.addEventListener('touchstart', function(e){
		if(e.target.closest('iframe, .thumb-carousel')) return;
		x0 = e.touches[0].clientX; y0 = e.touches[0].clientY;
	}, {passive:true});
	document.addEventListener('touchend', function(e){
		if(x0 === null) return;
		var dx = e.changedTouches[0].clientX - x0;
		var dy = e.changedTouches[0].clientY - y0;
		x0 = y0 = null;
		if(Math.abs(dx) > 70 && Math.abs(dx) > Math.abs(dy) * 2){
			window.location = dx < 0 ? next.href : prev.href;
		}
	}, {passive:true});
})();

/* Prev / next keyboard navigation on project pages */
(function(){
	var prev = document.getElementById('prev'), next = document.getElementById('next'), close = document.getElementById('close');
	if(!prev && !next) return;
	document.addEventListener('keydown', function(e){
		if(e.key === 'ArrowLeft' && prev) window.location = prev.href;
		if(e.key === 'ArrowRight' && next) window.location = next.href;
		if(e.key === 'Escape' && close) window.location = close.href;
	});
})();
