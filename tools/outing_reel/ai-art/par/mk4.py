# 11/25 東福寺・六義園：違う絵21枚（使い回しなし）を場面に分けて pv3 の撮り方を作る。python3 mk4.py → tf*.json rk*.json
import json,os
U='/home/user/usagi-fudosan-media/shots'; HF='/home/user/usagi-fudosan-media/tools/outing_reel/hf'
FLAT=os.path.abspath('flat.png') if os.path.exists('flat.png') else '/tmp/claude-0/-home-user/26a03ff5-4665-5ecb-80de-75bf562d97ce/scratchpad/map/flat.png'
def S(set_,name,mv): return dict(img=f'{U}/ai-art/{set_}/{name}.jpg',dep=FLAT,dur=0,m=mv,tr='fade',ease='lin')
def PUSH(cy=.42,ray=.3,mist=.2,rx=.5,ry=.1,wind=.0045): return dict(z0=0,z1=.16,cx=.5,cy=cy,b0=1.03,b1=1.2,ray=ray,mist=mist,rx=rx,ry=ry,wind=wind)
def PAN(d=1,ray=.25,mist=.15,rx=.5,ry=.1,wind=.0045): return dict(z0=0,z1=.05,px0=.045*d,px1=-.045*d,b0=1.17,b1=1.23,ray=ray,mist=mist,rx=rx,ry=ry,wind=wind)
def VIM(ray=.2,mist=.1): return dict(z0=0,z1=.12,cx=.5,cy=.5,b0=1.03,b1=1.15,ray=ray,mist=mist,rx=.5,ry=.1,wind=.0045)
N=dict(ray=0,mist=0); T,R='tofukuji1','rikugien1'
tf=[[S(T,'15-autumn-wide',PUSH(.45,ray=.35,rx=.7)),S(T,'01-sea',PAN(1,mist=.3))],
 [S(T,'02-bridge',PUSH(.45)),S(T,'20-arch',PAN(-1)),S(T,'03-inside',PUSH(.45,ray=.35,rx=.75)),S(T,'08-ravine',PAN(1,mist=.3))],
 [S(T,'19-morning',PUSH(.42,ray=.45,mist=.35,rx=.6)),S(T,'10-roof',PAN(-1)),S(T,'11-backlit',PUSH(.45,ray=.4,rx=.7,ry=.15)),S(T,'14-steps',PAN(1))],
 [S(T,'04-golden',PUSH(.45,ray=.35,rx=.7)),S(T,'16-leaves-wood',PAN(-1,ray=.15,mist=0)),S(T,'18-water',PUSH(.5,ray=.1,mist=0,wind=0))],
 [S(T,'13-veranda',PUSH(.45,ray=.3)),S(T,'06-checker',PAN(1,mist=.1)),S(T,'07-gravel',PUSH(.42)),S(T,'21-lantern',PAN(-1))],
 [S(T,'05-gate',PUSH(.4,ray=.4,mist=.3,rx=.7)),S(T,'09-path',PAN(1,ray=.35)),S(T,'17-hall',PUSH(.42,ray=.3,rx=.3))]]
tvi=[S(T,'12-moss',VIM())]
rk=[[S(R,'17-overview-night',PUSH(.45,**N)),S(R,'01-pond-night',PAN(1,**N))],
 [S(R,'10-day-pond',PUSH(.42,ray=.3,rx=.7)),S(R,'11-day-maple',PAN(-1)),S(R,'13-path-day',PUSH(.45,ray=.35)),S(R,'12-dodan',PAN(1,ray=.15))],
 [S(R,'04-storehouse',PUSH(.45,**N)),S(R,'05-bamboo',PAN(-1,**N)),S(R,'14-gate',PUSH(.45,**N))],
 [S(R,'06-lightstream',PUSH(.45,**N)),S(R,'02-bridge-night',PAN(1,**N)),S(R,'07-ground',PUSH(.5,**N)),S(R,'15-reflection',PAN(-1,**N,wind=0))],
 [S(R,'03-teahouse',PUSH(.45,**N)),S(R,'09-matcha',PAN(1,**N,wind=0)),S(R,'16-lantern-night',PUSH(.45,**N))],
 [S(R,'08-mountain',PUSH(.42,**N)),S(R,'20-leaves-close',PAN(-1,**N)),S(R,'18-ginkgo-night',PUSH(.4,**N)),S(R,'21-island',PAN(1,**N))]]
rvi=[S(R,'19-dusk',VIM(0,0))]
for key,L,vi,d in (('tf',tf,tvi,'tofukuji-1125'),('rk',rk,rvi,'rikugien-1125')):
    if not os.path.exists(f'{HF}/{d}/times.json'): print('skip',key); continue
    sp=json.load(open(f'{HF}/{d}/spans.json')); Tm=json.load(open(f'{HF}/{d}/times.json'))
    used=[s['img'] for sc in L for s in sc]+[vi[0]['img']]; assert len(used)==len(set(used)),key
    miss=[u for u in used if not os.path.exists(u)]; print(key,'missing',len(miss),[os.path.basename(m) for m in miss])
    for k,sh in enumerate(L):
        need=sp[k]+.3
        if k==0: need=need-4.2+.4
        n=len(sh); dd=round((need+.3*(n-1))/n,3)
        for s in sh: s['dur']=dd
        json.dump(sh,open(f'{key}{k}.json','w')); print(key,k,n,dd)
    T5,T6=Tm['T'][5],Tm['T'][6]; vi[0]['dur']=round(T6+1.2-T5+.5,2); json.dump(vi,open(f'{key}vi.json','w'))
    print(key,'images',len(used))
