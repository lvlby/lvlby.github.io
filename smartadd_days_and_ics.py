import sys
from playwright.sync_api import sync_playwright
F=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':390,'height':844},service_workers='block')
    ctx.route('**/*',lambda r:r.continue_() if r.request.url.startswith('file:') else r.abort())
    pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
    pg.add_init_script("localStorage.setItem('lvlby-lang','en');localStorage.setItem('lvlby-profile',JSON.stringify({name:'Ali',student:true,goal:0,work:'x',age:1,wake:2,sleep:2,challenge:[0,1],interests:[0,2],energy:1,dayType:0,daily:1,remind:0,exp:0,src:0,ov:2,done:true}));localStorage.setItem('lvlby-tour','1')")
    pg.goto('file://'+F);pg.wait_for_timeout(1200)
    pg.fill('#quickName','Study English every 2 days at 7pm except Tuesdays');pg.press('#quickName','Enter');pg.wait_for_timeout(1800)
    pg.locator('#saChat .btn.primary').click();pg.wait_for_timeout(1200)
    r=pg.evaluate("""()=>{const o=[];for(let i=0;i<14;i++){const d=shiftDays(today(),i);const x=ensureDay(d);buildDay(d,true);const n=(ensureDay(d).tasks||[]).filter(t=>t.name==='Study English').length;o.push(d.slice(5)+'/'+'SMTWTFS'[new Date(d+'T12:00:00').getDay()]+':'+n)}return o.join('  ')}""")
    print('next 14 days (1 = has task):',r)
    ics=pg.evaluate("buildICS({routine:true,tasks:false,exams:false}).text")
    print([l for l in ics.split('\r\n') if l.startswith(('RRULE','DTSTART','SUMMARY:Study'))])
    print('errors',errs);b.close()
