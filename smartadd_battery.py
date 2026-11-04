import sys,json
from playwright.sync_api import sync_playwright
PH=[
'Study English every 2 days except Tuesdays',
'Study English every other day except Tuesdays at 7pm',
'Gym every day except Tue and Fri',
'Gym every day, rest every Tuesday',
'Read every night at 10, rest on Fridays',
'Walk every day, Tuesdays off',
'Math every 3 days but not on Saturdays until Dec 1',
'Piano every Monday and Wednesday except Wednesdays',
'Meditate every morning at 7',
'Call mom every evening at 8',
'Gym every day except every day of the week',
'Do not forget to buy milk tomorrow',
'Math homework tomorrow 5pm',
'Dentist on Friday at 3pm',
'Report by Friday 6pm',
'Gym every day for 2 weeks except Tuesdays',
'Skip Tuesdays',
'تکلیف ریاضی فردا ساعت ۵ عصر',
'زبان هر ۲ روز به‌جز سه‌شنبه‌ها ساعت ۷ عصر',
'زبان یک روز در میان به جز سه شنبه',
'ورزش هر روز غیر از جمعه‌ها',
'ورزش هر روز سه‌شنبه‌ها استراحت',
'مطالعه هر شب ساعت ۱۰، جمعه‌ها استراحت',
'مدیتیشن هر صبح ساعت ۷',
'هر دوشنبه و چهارشنبه کلاس به‌جز چهارشنبه',
'ورزش هر روز به جز همه روزها',
'سلام',
]
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':390,'height':844},service_workers='block')
    ctx.route('**/*',lambda r:r.continue_() if r.request.url.startswith('file:') else r.abort())
    pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
    pg.add_init_script("localStorage.setItem('lvlby-lang','en');localStorage.setItem('lvlby-profile',JSON.stringify({name:'Ali',student:true,goal:0,work:'x',age:1,wake:2,sleep:2,challenge:[0,1],interests:[0,2],energy:1,dayType:0,daily:1,remind:0,exp:0,src:0,ov:2,done:true}));localStorage.setItem('lvlby-tour','1')")
    pg.goto('file://'+sys.argv[1]);pg.wait_for_timeout(1200)
    for t in PH:
        r=pg.evaluate("t=>{const r=SA.parse(t,saCtx(),{});const it=r.recur?{days:r.recur.days,ev:r.recur.ev,wk:r.recur.wk,from:r.from,until:r.until}:null;let occ=[];if(it){let d=r.from;for(let i=0;i<16&&occ.length<8;i++,d=shiftDays(d,1)){if(onDate(it,d))occ.push(d.slice(5)+'/'+'SMTWTFS'[new Date(d+'T12:00:00').getDay()])}}return{title:r.title,recur:r.recur&&{t:r.recur.type,ev:r.recur.ev,wk:r.recur.wk,days:r.recur.days&&r.recur.days.join(''),skip:(r.recur.skip||[]).join('')},skip:r.skip.join(''),time:r.time,date:r.date,due:r.due,until:r.until,err:r.error,ask:r.ask&&r.ask.kind,occ:occ.join(' ')}}",t)
        print(t,'\n   ',json.dumps({k:v for k,v in r.items() if v not in (None,'',[])},ensure_ascii=False))
    print('errors',errs);b.close()
