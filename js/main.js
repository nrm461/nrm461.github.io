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
