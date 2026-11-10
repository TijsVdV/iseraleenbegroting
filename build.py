#!/usr/bin/env python3
"""Builds the NL, FR and DE versions of every page from src/.
Run after editing anything in src/:  python3 build.py
Outputs: /index.html /uitleg.html /spel.html /privacy.html and the same under /fr/ and /de/.
data.json is not touched (the scheduled task owns it); its current contents are baked in as the snapshot."""
import json, re, html, os, sys
ROOT=os.path.dirname(os.path.abspath(__file__)); SRC=os.path.join(ROOT,'src')
SITE='https://iseraleenbegroting.be'
LANGS={
 'nl':{'tag':'nl-BE','og':'nl_BE','base':'/','locale':'nl-BE','ogimg':'og.png','name':'Nederlands','short':'NL'},
 'fr':{'tag':'fr-BE','og':'fr_BE','base':'/fr/','locale':'fr-BE','ogimg':'og-fr.png','name':'Français','short':'FR'},
 'de':{'tag':'de-BE','og':'de_BE','base':'/de/','locale':'de-BE','ogimg':'og-de.png','name':'Deutsch','short':'DE'},
}
PAGES=['index','uitleg','spel','privacy']
def load(p): return json.load(open(os.path.join(SRC,p),encoding='utf-8'))
def read(p): return open(os.path.join(SRC,p),encoding='utf-8').read()
I18N={l:load('i18n/%s.json'%l) for l in LANGS}
DATA=json.load(open(os.path.join(ROOT,'data.json'),encoding='utf-8'))
QCOLORS=['var(--p-rood)','var(--p-blauw)','var(--p-groen)','var(--p-oranje)','var(--p-turkoois)','var(--p-magenta)','var(--p-geel)','var(--p-bordeaux)','var(--p-marine)','var(--p-groen)']
MONTHS={'nl':['jan.','feb.','maart','apr.','mei','juni','juli','aug.','sep.','okt.','nov.','dec.'],
        'fr':['janv.','févr.','mars','avr.','mai','juin','juil.','août','sept.','oct.','nov.','déc.'],
        'de':['Jan.','Feb.','März','Apr.','Mai','Juni','Juli','Aug.','Sep.','Okt.','Nov.','Dez.']}
def qdate(d,l):
    y,m,dd=map(int,d.split('-')); return ('%d. %s %d' if l=='de' else '%d %s %d')%(dd,MONTHS[l][m-1],y)
def page_url(page,l): return SITE+LANGS[l]['base']+('' if page=='index' else page+'.html')
def jsstr(v): return json.dumps(v,ensure_ascii=False).replace('</','<\\/')

def render(tpl,l,page,extra=None):
    T=dict(I18N[l].get('common',{})); T.update(I18N[l].get(page,{}))
    if extra: T.update(extra)
    c=I18N[l]['common']
    def hreflang():
        out=['<link rel="alternate" hreflang="%s" href="%s">'%(LANGS[x]['tag'][:2],page_url(page,x)) for x in LANGS]
        out.append('<link rel="alternate" hreflang="x-default" href="%s">'%page_url(page,'nl'))
        return '\n'.join(out)
    def langswitch():
        a=[]
        for x in LANGS:
            href=LANGS[x]['base']+('' if page=='index' else page+'.html')
            a.append('<a href="%s" hreflang="%s" lang="%s" title="%s"%s>%s</a>'%(href,x,x,LANGS[x]['name'],' aria-current="true"' if x==l else '',LANGS[x]['short']))
        return '<nav class="langs" aria-label="%s">%s</nav>'%(html.escape(c['lang_label']),''.join(a))
    def skins():
        return ('<span class="skins" role="group" aria-label="%s"><span>%s</span>'%(html.escape(c['theme_aria']),c['theme_label'])+
                ''.join('<button type="button" data-skin="%s">%s</button>'%(k,c['skin_'+k]) for k in ('partijen','belgie','retro'))+'</span>')
    def quote(i):
        q=QUOTES[i]; side='cite-l' if i%2==0 else 'cite-r'
        cap='<b>%s</b> (%s), %s · %s · <a href="%s" rel="noopener">%s ↗</a>'%(html.escape(q['who']),html.escape(q['party']),html.escape(q['role'][l]),qdate(q['date'],l),html.escape(q['url']),html.escape(q['src']))
        if q.get('tr'): cap+=' · <span class="tr">%s</span>'%html.escape(c['quote_translated'])
        return ('  <div class="cite-slot %s"><figure class="cite" style="--qc:%s"><blockquote lang="nl" cite="%s"><p>%s</p></blockquote><figcaption>%s</figcaption></figure></div>'
                %(side,QCOLORS[i%len(QCOLORS)],html.escape(q['url']),html.escape(q['q']),cap))
    jsonld={"@context":"https://schema.org","@type":"WebSite","name":T.get('site_name',''),"alternateName":T.get('ld_alt',''),"url":page_url('index',l),"inLanguage":LANGS[l]['tag'],"description":T.get('ld_desc','')}
    fixed={'LANG':l,'LANGTAG':LANGS[l]['tag'],'OGLOCALE':LANGS[l]['og'],'BASE':LANGS[l]['base'],'CANON':page_url(page,l),
           'OGIMAGE':LANGS[l]['ogimg'],'LOCALE':LANGS[l]['locale']}
    missing=[]
    def sub(m):
        kind,key=m.group(1),m.group(2)
        if kind=='HREFLANG': return hreflang()
        if kind=='LANGSWITCH': return langswitch()
        if kind=='SKINS': return skins()
        if kind=='JSONLD': return json.dumps(jsonld,ensure_ascii=False)
        if kind=='SNAP': return jsstr(DATA)
        if kind in fixed: return fixed[kind]
        if kind=='BODY': return extra['__body']
        if kind=='j':
            if key in fixed: return jsstr(fixed[key])
            if key not in T: missing.append(key); return '""'
            return jsstr(T[key])
        if key not in T: missing.append(key); return ''
        v=T[key]
        if kind=='a': return html.escape(v if isinstance(v,str) else json.dumps(v),quote=True)
        if kind=='t': return v
        if kind=='J': return jsstr(v)
        raise ValueError(kind)
    out=re.sub(r'\{\{(t|a|j|J|HREFLANG|LANGSWITCH|SKINS|JSONLD|SNAP|QUOTE|LANG|LANGTAG|OGLOCALE|BASE|CANON|OGIMAGE|LOCALE|BODY)(?:[.:]([A-Za-z0-9_]+))?\}\}',sub,tpl)
    if missing: raise SystemExit('Missing %s keys for %s/%s: %s'%(l,page,'',sorted(set(missing))))
    left=re.findall(r'\{\{[^}]*\}\}',out)
    if left: raise SystemExit('Unresolved placeholders in %s/%s: %s'%(l,page,left[:5]))
    return out

def main():
    for l in LANGS:
        outdir=ROOT if l=='nl' else os.path.join(ROOT,l)
        os.makedirs(outdir,exist_ok=True)
        for page in PAGES:
            if os.path.exists(os.path.join(SRC,page+'.tpl.html')):
                tpl=read(page+'.tpl.html'); extra=None
                body=os.path.join(SRC,'%s.body.%s.html'%(page,l))
                if os.path.exists(body): extra={'__body':read('%s.body.%s.html'%(page,l))}
                out=render(tpl,l,page,extra)
                open(os.path.join(outdir,page+'.html'),'w',encoding='utf-8').write(out)
                print('built',os.path.relpath(os.path.join(outdir,page+'.html'),ROOT))
    # sitemap with language alternates
    urls=[]
    for page,freq in (('index','daily'),('uitleg','weekly'),('spel','monthly')):
        for l in LANGS:
            alts=''.join('\n    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>'%(x,page_url(page,x)) for x in LANGS)
            urls.append('  <url>\n    <loc>%s</loc>\n    <changefreq>%s</changefreq>%s\n  </url>'%(page_url(page,l),freq,alts))
    open(os.path.join(ROOT,'sitemap.xml'),'w',encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'+'\n'.join(urls)+'\n</urlset>\n')
    print('built sitemap.xml')
if __name__=='__main__': main()
