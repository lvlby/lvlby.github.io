import sys
from playwright.sync_api import sync_playwright
F=sys.argv[1];O=sys.argv[2]
with sync_playwright() as p:
    b=p.chromium.launch()
    for lang in ['en','fa']:
        ctx=b.new_context(viewport={'width':390,'height':844},service_workers='block')
        ctx.route('**/*',lambda r:r.continue_() if r.request.url.startswith('file:') else r.abort())
        pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
        pg.add_init_script("localStorage.setItem('lvlby-lang','%s');localStorage.setItem('lvlby-profile',JSON.stringify({name:'Ali',student:true,goal:0,work:'x',age:1,wake:2,sleep:2,challenge:[0,1],interests:[0,2],energy:1,dayType:0,daily:1,remind:0,exp:0,src:0,ov:2,done:true}));localStorage.setItem('lvlby-tour','1')"%lang)
        pg.goto('file://'+F);pg.wait_for_timeout(1200)
        txt=lambda:pg.evaluate("(document.getElementById('saChat')||{}).innerText||''").replace('\n',' | ')
        def say(t,w=1800):
            pg.fill('#quickName',t);pg.press('#quickName','Enter');pg.wait_for_timeout(w);return txt()
        en=lang=='en'
        print(f'--- {lang}')
        print('greeting:',say('hi' if en else 'سلام')[:230])
        print('help:',say('help' if en else 'راهنما')[:200])
        print('thanks:',say('thanks' if en else 'مرسی',1200))
        print('empty-title:',say('tomorrow at 5pm' if en else 'فردا ساعت ۵ عصر')[:160])
        print('ambiguous:',say('Call mom every day at 7' if en else 'زنگ به مامان هر روز ساعت ۷')[:200])
        pg.locator('#saChat .btn').nth(1).click();pg.wait_for_timeout(1800);print(' after PM chip:',txt()[:260])
        pg.locator('#saChat .btn.primary').click();pg.wait_for_timeout(1500);print(' done:',txt()[:200])
        print('plain task:',say('Buy milk tomorrow 5pm' if en else 'خرید شیر فردا ساعت ۵ عصر')[:200])
        print('dup:',say('Buy milk tomorrow 5pm' if en else 'خرید شیر فردا ساعت ۵ عصر',1500)[:140])
        print('skip-all:',say('Gym every day except Sunday Monday Tuesday Wednesday Thursday Friday Saturday' if en else 'ورزش هر روز به جز یکشنبه دوشنبه سه شنبه چهارشنبه پنجشنبه جمعه شنبه')[:200])
        # day lists
        r=pg.evaluate("""()=>{const out={};['2026-11-08','2026-11-10','2026-11-12'].forEach(d=>{const x=ensureDay(d);if(!x.built)buildDay(d);buildDay(d,true);out[d]=(ensureDay(d).tasks||[]).filter(t=>/Call mom|مامان/.test(t.name||'')).length});return out}""")
        print('call-mom per day (every day => 1 each):',r)
        print('errors',errs);ctx.close()
    b.close()
