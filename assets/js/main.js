(function(){
  var burger=document.querySelector('.burger'), nav=document.querySelector('.nav');
  var scrim=document.createElement('div'); scrim.className='nav-scrim'; document.body.appendChild(scrim);
  function setOpen(open){
    if(!nav) return;
    nav.classList.toggle('is-open',open);
    scrim.classList.toggle('is-open',open);
    if(burger) burger.setAttribute('aria-expanded',open?'true':'false');
    document.body.style.overflow = open ? 'hidden' : '';
  }
  if(burger&&nav){burger.addEventListener('click',function(){setOpen(!nav.classList.contains('is-open'));});}
  scrim.addEventListener('click',function(){setOpen(false);});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'){setOpen(false);var l=document.querySelector('.lb');if(l)l.classList.remove('is-open');}});
  var lb=document.querySelector('.lb');
  if(lb){
    var img=lb.querySelector('img');
    document.querySelectorAll('.gal a').forEach(function(a){
      a.addEventListener('click',function(e){e.preventDefault();img.src=a.getAttribute('href');img.alt=a.querySelector('img').alt;lb.classList.add('is-open');});
    });
    lb.addEventListener('click',function(){lb.classList.remove('is-open');});
  }
})();
