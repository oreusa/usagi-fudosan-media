# 声の長さから時刻を決めて index.html を作る（場面＝声の長さ）
import subprocess,sys
def dur(f):return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]).decode())
D=[dur(f"a/d{i}.wav") for i in range(5)]+[dur("a/e0.wav")]
v=[1.8];T=[None]
for k in range(4):
    e=v[k]+D[k];T.append(round(e+0.35,2));v.append(round(T[-1]+0.6,2))
v4=v[4];T5=round(v4+D[4]+0.35,2);v5=round(T5+0.6,2);END=round(v5+D[5]+2.4,2)
T1,T2,T3,T4=T[1:]
s=open("index-v3.html").read()
R=[('data-duration="30.5" data-width','data-duration="%s" data-width'%END),
('rokaL.mp4" muted data-start="19.5" data-duration="5.9"','rokaL.mp4" muted data-start="%s" data-duration="%s"'%(T3,round(T4-T3+.8,2))),
('pondL.mp4" muted data-start="13.0" data-duration="7.1"','pondL.mp4" muted data-start="%s" data-duration="%s"'%(T2,round(T3-T2+.8,2))),
('gateL.mp4" muted data-start="7.0" data-duration="6.6"','gateL.mp4" muted data-start="%s" data-duration="%s"'%(T1,round(T2-T1+.8,2))),
('hookL.mp4" muted data-start="0.9" data-duration="6.5"','hookL.mp4" muted data-start="0.9" data-duration="%s"'%round(T1-0.9+.8,2)),
('a/bgm31.m4a" data-start="0" data-duration="30.5"','a/bgm45.m4a" data-start="0" data-duration="%s"'%END),
('flip.wav" data-start="7.0"','flip.wav" data-start="%s"'%T1),('flip.wav" data-start="13.0"','flip.wav" data-start="%s"'%T2),
('flip.wav" data-start="19.5"','flip.wav" data-start="%s"'%T3),('flip.wav" data-start="24.8"','flip.wav" data-start="%s"'%T4),
('<audio src="a/c0.wav" data-start="1.9" data-duration="4.8"','<audio src="a/d0.wav" data-start="%s" data-duration="%s"'%(v[0],round(D[0],2))),
('<audio src="a/c1.wav" data-start="7.9" data-duration="4.7"','<audio src="a/d1.wav" data-start="%s" data-duration="%s"'%(v[1],round(D[1],2))),
('<audio src="a/c2.wav" data-start="13.9" data-duration="5.2"','<audio src="a/d2.wav" data-start="%s" data-duration="%s"'%(v[2],round(D[2],2))),
('<audio src="a/c3.wav" data-start="20.4" data-duration="4.0"','<audio src="a/d3.wav" data-start="%s" data-duration="%s"'%(v[3],round(D[3],2))),
('<audio src="a/c4.wav" data-start="25.5" data-duration="3.8" data-volume="1.7"></audio>','<audio src="a/d4.wav" data-start="%s" data-duration="%s" data-volume="1.7"></audio>\n <audio src="a/e0.wav" data-start="%s" data-duration="%s" data-volume="1.7"></audio>\n <audio src="a/flip.wav" data-start="%s" data-duration="0.5" data-volume="0.8"></audio>'%(v4,round(D[4],2),v5,round(D[5],2),T5)),
('[["#s0","#s1",7.0],["#s1","#s2",13.0],["#s2","#s3",19.5],["#s3","#s4",24.8]]','[["#s0","#s1",%s],["#s1","#s2",%s],["#s2","#s3",%s],["#s3","#s4",%s],["#s4","#s5",%s]]'%(T1,T2,T3,T4,T5)),
('[["#s0",1.9],["#s1",7.8],["#s2",13.8],["#s3",20.3]]','[["#s0",%s],["#s1",%s],["#s2",%s],["#s3",%s]]'%(v[0]-.1,v[1]-.1,v[2]-.1,v[3]-.1)),
('stagger:.1},25.2)','stagger:.1},%s)'%(T4+.4)),
('.55,1.8,7.6,true);\nglow','.55,1.8,%s,true);\nglow'%(T1+.6)),('.7,1.8,7.6,true);','.7,1.8,%s,true);'%(T1+.6)),('26,1.8,7.6,','26,1.8,%s,'%(T1+.6)),
('.55,19.9,25.4,true)','.55,%s,%s,true)'%(T3+.4,T4+.6)),
('.7,19.9,25.4,true);glow(f3,830,816,110,"255,190,110",.7,19.9,25.4,true)','.7,%s,%s,true);glow(f3,830,816,110,"255,190,110",.7,%s,%s,true)'%(T3+.4,T4+.6,T3+.4,T4+.6)),
('22,19.9,25.4,','22,%s,%s,'%(T3+.4,T4+.6)),
('rays(document.getElementById("fx1"),7.4,13.6);rays(document.getElementById("fx2"),13.4,20.1)','rays(document.getElementById("fx1"),%s,%s);rays(document.getElementById("fx2"),%s,%s)'%(T1+.4,T2+.6,T2+.4,T3+.6)),
('const T5=@T5@;','const T5=%s;'%T5),('data-volume="0.45" data-fade-in="0.6" data-fade-out="1.8"','data-volume="0" data-fade-in="0.6" data-fade-out="1.8"'),
('ease:"back.out(1.6)"},28.4)','ease:"back.out(1.6)"},%s)'%(T4+2.2)),
('{opacity:1,duration:.1},30.4)','{opacity:1,duration:.1},%s)'%(END-.1))]
for a,b in R:
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
open("index.html","w").write(s);print("END",END,"T",T,"T5",T5,"v",v,v5);import json;json.dump(dict(END=END,v=v+[v5],T=T[1:]+[T5]),open("times.json","w"))
