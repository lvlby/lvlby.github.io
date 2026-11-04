import sys,json
from playwright.sync_api import sync_playwright
F=sys.argv[1];O=sys.argv[2]
def run(lang,sent,refine,tag):
    with sync_playwright() as p:
        b=p.chromium.launch();ctx=b.new_context(viewport={'width':390,'height':844},service_workers='block')
        ctx.route('**/*',lambda r:r.continue_() if r.request.url.startswith('file:') else r.abort())
        pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
        pg.add_init_script("localStorage.setItem('lvlby-lang','%s');localStorage.setItem('lvlby-profile',JSON.stringify({name:'Ali',student:true,goal:0,work:'x',age:1,wake:2,sleep:2,challenge:[0,1],interests:[0,2],energy:1,dayType:0,daily:1,remind:0,exp:0,src:0,ov:2,done:true}));localStorage.setItem('lvlby-tour','1')"%lang)
        pg.goto('file://'+F);pg.wait_for_timeout(1200)
        txt=lambda:pg.evaluate("(document.getElementById('saChat')||{}).innerText||''")
        pg.fill('#quickName',sent);pg.click('#saGo');pg.wait_for_timeout(250)
        print(f'[{lang}/{tag}] typing dots visible:',pg.evaluate("!!document.querySelector('#saChat .sadots')"))
        pg.wait_for_timeout(1800);print('  BUBBLE:',txt().replace('\n',' | '))
        pg.locator('#saChat').scroll_into_view_if_needed();pg.screenshot(path=f'{O}-{lang}-{tag}-1.png')
        if refine:
            for rt in refine:
                pg.fill('.saref input',rt);pg.click('.saref button');pg.wait_for_timeout(1900);print('  REFINE',repr(rt),'->',txt().replace('\n',' | ')[:330])
            pg.screenshot(path=f'{O}-{lang}-{tag}-2.png')
        if pg.evaluate("!!sa.pending"):
            pg.click('#saChat .btn.primary');pg.wait_for_timeout(1800)
            print('  DONE:',txt().replace('\n',' | '))
            rt=pg.evaluate("(()=>{const g=data.routine.find(x=>x.id==='smart');return g?JSON.stringify(g.items.map(i=>({n:i.name,t:i.time,d:i.days&&i.days.join(''),ev:i.ev,sk:i.skip&&i.skip.join(''),u:i.until}))):null})()")
            print('  SAVED:',rt)
            pg.screenshot(path=f'{O}-{lang}-{tag}-3.png')
            pg.evaluate("document.querySelector('.tab[data-view=habits]').click()");pg.wait_for_timeout(500)
            print('  ROUTINE ROW HINT:',pg.evaluate("[...document.querySelectorAll('#routineEditor .smalltext')].map(e=>e.innerText).join(' || ')"))
            pg.screenshot(path=f'{O}-{lang}-{tag}-4.png',full_page=False)
        print('  errors',errs);b.close()
run('en','Study English every other day at 7pm except Tuesdays',['also skip Fridays','make it 6 pm'],'a')
run('fa','زبان هر ۲ روز ساعت ۷ عصر به‌جز سه‌شنبه‌ها',['جمعه‌ها هم نباشد'],'a')
