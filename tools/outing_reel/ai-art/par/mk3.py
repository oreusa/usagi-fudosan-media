import json,os
U='/home/user/usagi-fudosan-media/shots'
FLAT=os.path.abspath('flat.png')
def S(set_,name,mv):
    img=f'{U}/ai-art/{set_}/{name}.jpg'; d=f'{U}/ai-depth-{set_}/{name}-depth.png'
    return dict(img=img,dep=d if os.path.exists(d) else FLAT,dur=0,m=mv,tr='fade',ease='lin')
def PUSH(cy=.42,ray=.3,mist=.2,rx=.5,ry=.1,wind=.0045): return dict(z0=0,z1=.16,cx=.5,cy=cy,b0=1.03,b1=1.2,ray=ray,mist=mist,rx=rx,ry=ry,wind=wind)
def PAN(d=1,ray=.25,mist=.15,rx=.5,ry=.1,wind=.0045): return dict(z0=0,z1=.05,px0=.045*d,px1=-.045*d,b0=1.17,b1=1.23,ray=ray,mist=mist,rx=rx,ry=ry,wind=wind)
N=dict(ray=0,mist=0)
J2,J4,J5,J7='jingoji2','jingoji4','jingoji5','jingoji7'
G2,G4,G5,G6,G7='gaien2','gaien4','gaien5','gaien6','gaien7'
jm=[[S(J4,'8-rays',PUSH(.35,ray=.4,rx=.62)),S(J2,'1-steps',PAN(1))],
 [S(J7,'23-bridge',PUSH(.45)),S(J7,'24-river',PAN(-1,mist=.3)),S(J7,'25-leafwater',PUSH(.5,ray=.15,mist=0,wind=0))],
 [S(J7,'27-terrace',PUSH(.4,ray=.4,rx=.7)),S(J7,'26-saucers',PAN(1)),S(J5,'20-kawarake',PUSH(.35,ray=.3)),S(J4,'11-valley',PAN(-1,mist=.4))],
 [S(J4,'12-lantern',PUSH(.45)),S(J4,'9-branch',PAN(1,rx=.75)),S(J7,'32-moss',PUSH(.5,ray=.1,mist=0))],
 [S(J7,'30-approach',PUSH(.35,ray=.4)),S(J4,'7-gate',PAN(-1,rx=.7)),S(J2,'4-wall',PUSH(.45)),S(J7,'28-pagoda',PAN(1))],
 [S(J4,'10-eave',PAN(-1,rx=.8)),S(J2,'5-kondo',PUSH(.42,rx=.3)),S(J7,'31-sunset',PAN(1,ray=.35,rx=.3,ry=.2)),S(J2,'6-valley',PUSH(.45,mist=.35))]]
jvi=[S(J2,'3-leaves',dict(z0=0,z1=.12,cx=.5,cy=.5,b0=1.03,b1=1.15,ray=.2,mist=.1,rx=.5,ry=.1,wind=.0045))]
gm=[[S(G4,'7-tunnel',PUSH(.45,ray=.35,rx=.75)),S(G2,'1-walk',PAN(1)),S(G7,'28-backlit',PUSH(.4,ray=.4,rx=.6,ry=.15))],
 [S(G5,'13-aerial',PUSH(.45,ray=.15,mist=.1)),S(G7,'25-trunks',PUSH(.45)),S(G7,'24-morning',PAN(-1,mist=.3)),S(G7,'30-sidewalk',PUSH(.45))],
 [S(G2,'4-rows',PUSH(.42)),S(G5,'14-aerial2',PAN(1,ray=.15)),S(G4,'9-path',PUSH(.45)),S(G7,'23-leafsky',PAN(-1,ray=.2,mist=0))],
 [S(G7,'26-canopy',PAN(1,ray=.35)),S(G2,'2-up',PUSH(.4,ray=.35))],
 [S(G4,'10-dusk',PUSH(.45,**N)),S(G7,'31-dusk2',PAN(-1,**N)),S(G6,'22-night',PUSH(.45,**N)),S(G7,'27-reflect',PAN(1,**N))],
 [S(G2,'3-carpet',PUSH(.5)),S(G7,'29-pile',PAN(-1)),S(G4,'12-sky',PUSH(.4,ray=.4,rx=.8))]]
gvi=[S(G2,'5-eve',dict(z0=0,z1=.12,cx=.5,cy=.5,b0=1.03,b1=1.15,ray=.15,mist=.1,rx=.5,ry=.1,wind=.0045))]
sp={'jm':[8.21,8.2,10.59,6.45,7.47,7.86],'gm':[9.56,9.72,8.83,5.58,9.34,6.59]}
VI={'jm':(45.38,56.88),'gm':(46.22,56.87)}
for key,L,vi in (('jm',jm,jvi),('gm',gm,gvi)):
    used=[s['img'] for sc in L for s in sc]+[vi[0]['img']]; assert len(used)==len(set(used)),key
    for k,sh in enumerate(L):
        need=sp[key][k]+.3
        if k==0: need=need-3.6+.4
        n=len(sh); d=round((need+.3*(n-1))/n,3)
        for s in sh: s['dur']=d
        json.dump(sh,open(f'{key}{k}.json','w')); print(key,k,n,d)
    a,b=VI[key]; vi[0]['dur']=round(b+1.2-a+.5,2); json.dump(vi,open(f'{key}vi.json','w'))
    print(key,'images',len(used))
