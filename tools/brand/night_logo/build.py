# 夜のロゴを一度に作る（11/2 オーナー「雑い、綺麗にやれ」）
# すき間の判定は360pxで行い、塗りと光は1200pxで作ってから360pxに縮める（ふちがなめらか、ざらつき無し）
# 使い方: python3 build.py ../../../links/assets/logo.png ../../../links/assets/logo-s-night.png
import sys, os, subprocess, tempfile, numpy as np
from PIL import Image, ImageFilter, ImageDraw
from scipy import ndimage as nd
src,dst=sys.argv[1:3]; HERE=os.path.dirname(os.path.abspath(__file__)); T=tempfile.mkdtemp()
def clear_face(im,r):
    A=np.array(im).astype(float);a=A[...,3]
    b=np.array(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.BoxBlur(r))).astype(float)
    A[(a<150)&(b<150)&(a>0),3]=0;return Image.fromarray(A.astype(np.uint8))
base=Image.open(src).convert('RGBA')
lo=clear_face(base.resize((360,360),Image.LANCZOS),3)
HI=1200;hi=clear_face(base.resize((HI,HI),Image.LANCZOS),10)
# --- 1. すき間（360px） gap.py と同じ考え方
A=np.array(lo).astype(float);a=A[...,3];W=360;S=W/720;K=3
poly=[(200,420),(250,320),(330,288),(420,298),(470,336),(540,336),(585,400),(625,470),(645,525),(625,605),(565,665),(470,650),(400,630),(300,625),(225,610),(195,520)]
pm=Image.new('L',(W,W),0);ImageDraw.Draw(pm).polygon([(x*S,y*S) for x,y in poly],fill=255);P=np.array(pm)>0
tr=a<60;op=~tr
closed=nd.binary_dilation(op,iterations=K//2)
lab,n=nd.label(~closed);ext=np.zeros_like(tr)
seeds={lab[int(y*S),int(x*S)] for x,y in [(120,450),(150,560),(600,350),(300,250),(560,300),(250,660)]}
for v in set(lab[0,:])|set(lab[-1,:])|set(lab[:,0])|set(lab[:,-1])|seeds:
    if v: ext|=lab==v
ext=nd.binary_dilation(ext,iterations=K//2+1)
face=nd.binary_dilation(nd.binary_opening(tr,iterations=7)&~ext,iterations=3)
gap=tr&~ext&P&~face
# 顔に接する広いすき間（おでこ・首）は白にしない
near=nd.binary_dilation(face&P&tr,iterations=10)
dt=nd.distance_transform_edt(gap)
gap&=~(nd.binary_dilation((dt>=3)&near,iterations=5)&gap)
# 小さいかけら・切れ端を消す（顔の近くは40px未満、ほかは6px未満）
lab2,n2=nd.label(gap,structure=np.ones((3,3)))
for i,s in enumerate(nd.sum(gap,lab2,range(1,n2+1))):
    c=lab2==i+1
    if s<6 or (s<40 and (c&nd.binary_dilation(near,iterations=4)).any()): gap[c]=0
# --- 2. 1200pxで白を髪の下に敷く
m=Image.fromarray((gap*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.5)).resize((HI,HI),Image.BICUBIC)
m=np.array(m).astype(float)/255
m=np.clip((m-0.35)/0.3,0,1)  # なめらかなふち
m=np.array(Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(float)/255
wl=Image.new('RGBA',(HI,HI),(250,248,246,0));wl.putalpha(Image.fromarray((m*255).astype(np.uint8)))
g=Image.new('RGBA',(HI,HI),(0,0,0,0));g.alpha_composite(wl);g.alpha_composite(hi)
gp=os.path.join(T,'g.png');g.save(gp)
# --- 3. 光（glow.py）を1200pxで → 360pxに縮める
op_=os.path.join(T,'o.png')
env=dict(os.environ,NORESIZE='1',SC=str(1.4*HI/360),GK='1.1',CORE='255,224,165')
subprocess.run([sys.executable,os.path.join(HERE,'glow.py'),gp,op_,os.path.join(T,'p.png')],env=env,check=True)
Image.open(op_).resize((360,360),Image.LANCZOS).save(dst)
print('ok',int(gap.sum()))
