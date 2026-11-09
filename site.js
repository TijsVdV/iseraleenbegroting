// Shared by the sub pages: theme switcher (same storage key as the home page) and the analytics consent.
(function(){
  var SKIN_KEY='begroting-skin', GA_ID='G-Q7V0Q88KNQ', CONSENT_KEY='begroting-consent';
  function applySkin(k,user){
    if(k!=='belgie'&&k!=='retro')k='partijen';
    if(k==='partijen')document.documentElement.removeAttribute('data-skin');else document.documentElement.setAttribute('data-skin',k);
    var bs=document.querySelectorAll('.skins button');
    for(var i=0;i<bs.length;i++)bs[i].setAttribute('aria-pressed',bs[i].getAttribute('data-skin')===k?'true':'false');
    if(user){try{localStorage.setItem(SKIN_KEY,k)}catch(e){}
      if(typeof window.gtag==='function')window.gtag('event','theme_select',{theme:k});}
  }
  applySkin(document.documentElement.getAttribute('data-skin')||'partijen',false);
  var sb=document.querySelectorAll('.skins button');
  for(var j=0;j<sb.length;j++)sb[j].addEventListener('click',function(){applySkin(this.getAttribute('data-skin'),true)});

  // Analytics only for visitors who already said yes on the home page. No banner here: the choice is made there.
  var c=null;try{c=localStorage.getItem(CONSENT_KEY)}catch(e){}
  if(c==='yes'){
    window.dataLayer=window.dataLayer||[];
    window.gtag=function(){dataLayer.push(arguments)};
    gtag('consent','default',{analytics_storage:'granted',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});
    gtag('set','allow_google_signals',false);
    gtag('js',new Date());gtag('config',GA_ID);
    var s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id='+GA_ID;document.head.appendChild(s);
  }
})();
