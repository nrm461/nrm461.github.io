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
	Array.prototype.forEach.call(filters, function(f){
		f.addEventListener('click', function(){
			Array.prototype.forEach.call(filters, function(x){ x.classList.remove('active'); });
			f.classList.add('active');
			var cat = f.getAttribute('data-filter');
			Array.prototype.forEach.call(cards, function(c){
				var show = (cat === 'all') || (c.getAttribute('data-category') === cat);
				c.classList.toggle('filtered-out', !show);
			});
		});
	});
})();

/* Video facade: click swaps thumbnail for autoplaying Vimeo player */
(function(){
	var f = document.querySelector('.video-facade');
	if(!f) return;
	f.addEventListener('click', function(){
		var id = f.getAttribute('data-vimeo');
		var params = 'badge=0&autopause=0&player_id=0&title=0&byline=0&portrait=0' +
			'&vimeo_logo=0&pip=0&cc=0&transcript=0&airplay=0&chromecast=0' +
			'&watch_full_video=0&dnt=1&autoplay=1';
		var box = f.querySelector('div');
		box.innerHTML = '<iframe src="https://player.vimeo.com/video/' + id + '?' + params +
			'" frameborder="0" allow="autoplay; fullscreen; picture-in-picture; encrypted-media" title="video"></iframe>';
		f.style.cursor = 'default';
	}, {once:true});
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
