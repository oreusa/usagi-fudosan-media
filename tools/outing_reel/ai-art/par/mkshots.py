import json,sys
U='/home/user/usagi-fudosan-media/shots'
FLAT='/tmp/claude-0/-home-user/26a03ff5-4665-5ecb-80de-75bf562d97ce/scratchpad/map/flat.png'
def S(set_, name, dur, mv, tr='fade', ease='o2'):
    img=f'{U}/ai-art/{set_}/{name}.jpg'; dep=FLAT if name=='6-down' else f'{U}/ai-depth-{set_}/{name}-depth.png'
    return dict(img=img,dep=dep,dur=dur,m=mv,tr=tr,ease=ease)
PUSH=lambda cy=.4,ray=0,mist=0,rx=.5,ry=0,b0=1.02,b1=1.24,z=.2: dict(z0=0,z1=z,cx=.5,cy=cy,b0=b0,b1=b1,ray=ray,mist=mist,rx=rx,ry=ry)
CRANE=lambda ray=0,mist=0,rx=.5,ry=0: dict(z0=0,z1=.08,py0=.07,py1=-.05,b0=1.22,b1=1.16,ray=ray,mist=mist,rx=rx,ry=ry)
PAN=lambda d=1,ray=0,mist=0,rx=.5,ry=0: dict(z0=0,z1=.06,px0=.06*d,px1=-.06*d,b0=1.2,b1=1.2,ray=ray,mist=mist,rx=rx,ry=ry)
ROT=lambda d=1,ray=0,rx=.5,ry=.2: dict(z0=0,z1=.05,r0=-.11*d,r1=.03*d,b0=1.32,b1=1.1,ray=ray,rx=rx,ry=ry)
PULL=lambda: dict(z0=0,z1=0,b0=1.3,b1=1.03,py0=-.03,py1=.01)
J,G='jingoji2','jingoji4'
jg=[[S(G,'8-rays',3.0,PUSH(.35,ray=.45,mist=.25,rx=.62,ry=.1)),S(J,'1-steps',3.1,PUSH(.32,ray=.4,mist=.3,ry=.12),'zoomin'),S(G,'7-gate',3.6,PUSH(.45,ray=.35,mist=.25,rx=.7,ry=.05))],
 [S(J,'2-canopy',4.0,ROT(1,ray=.35)),S(G,'9-branch',4.3,PUSH(.45,ray=.3,rx=.75,ry=.05,b0=1.0,b1=1.16,z=.08))],
 [S(J,'3-leaves',3.8,PUSH(.55,b1=1.2,z=.14)),S(G,'12-lantern',3.93,PUSH(.45,ray=.25,mist=.15,ry=.0))],
 [S(J,'4-wall',3.9,CRANE(ray=.3,mist=.2,ry=.05)),S(G,'10-eave',3.99,PAN(1,ray=.2,rx=.8,ry=.1),'smoothleft')],
 [S(J,'5-kondo',4.1,PUSH(.42,ray=.3,mist=.15,rx=.3,ry=.0,b1=1.2,z=.12)),S(G,'11-valley',4.12,PAN(-1,mist=.45,ray=.2,rx=.5,ry=.1))],
 [S(J,'6-down',3.7,PULL()),S(J,'6-valley',3.7,PUSH(.45,mist=.35,ray=.2,b1=1.18,z=.12))]]
A,B='gaien2','gaien4'
ga=[[S(B,'7-tunnel',5.2,PUSH(.45,ray=.35,rx=.75,ry=.1,b1=1.26,z=.22)),S(A,'1-walk',5.44,PUSH(.45,ray=.3,rx=.3,ry=.1,b1=1.24),'zoomin')],
 [S(A,'2-up',4.1,ROT(1,ray=.35)),S(B,'12-sky',4.26,ROT(-1,ray=.4,rx=.85,ry=.15))],
 [S(A,'3-carpet',4.0,PUSH(.5,ray=.2,b1=1.22,z=.16)),S(B,'9-path',4.22,PAN(1,ray=.25,rx=.2,ry=.1))],
 [S(A,'4-rows',4.5,CRANE(ray=.3,ry=.05)),S(B,'7-tunnel',4.48,PAN(-1,ray=.25,rx=.7,ry=.1),'smoothleft')],
 [S(A,'5-eve',3.5,PUSH(.45,ray=.3,b1=1.2,z=.14)),S(B,'10-dusk',3.64,PUSH(.45,b1=1.2,z=.16))],
 [S(A,'6-drone',7.14,dict(z0=0,z1=.1,b0=1.28,b1=1.04,py0=.03,py1=-.01,ray=.15),ease='io')]]
spans={'jg':[8.8,7.7,7.13,7.29,7.62,6.8],'ga':[10.04,7.76,7.62,8.38,6.54,6.84]}
for key,L in (('jg',jg),('ga',ga)):
    for k,sh in enumerate(L):
        tot=sum(s['dur'] for s in sh)-.3*(len(sh)-1); need=spans[key][k]+.3
        sh[-1]['dur']=round(sh[-1]['dur']+need-tot,2)
        json.dump(sh,open(f'{key}{k}.json','w'))
        print(key,k,round(sum(s['dur'] for s in sh)-.3*(len(sh)-1),2),need)
