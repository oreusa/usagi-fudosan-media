from PIL import Image, ImageFilter, ImageDraw
import numpy as np, sys
from scipy import ndimage as nd
src,dst=sys.argv[1:3]; K=int(sys.argv[3]) if len(sys.argv)>3 else 5
im=Image.open(src).convert('RGBA'); im=im if __import__("os").environ.get("NORESIZE") else im.resize((im.width*2,im.height*2),Image.LANCZOS)
W,H=im.size; A=np.array(im).astype(float); a=A[...,3]
S=W/720
poly=[(200,420),(250,320),(330,288),(420,298),(470,336),(540,336),(585,400),(625,470),(645,525),(625,605),(565,665),(470,650),(400,630),(300,625),(225,610),(195,520)]
pm=Image.new('L',(W,H),0);ImageDraw.Draw(pm).polygon([(x*S,y*S) for x,y in poly],fill=255);P=np.array(pm)>0
tr=a<60
op=a>=60
r,g,b=A[...,0],A[...,1],A[...,2];mx=np.maximum(np.maximum(r,g),b);mn=np.minimum(np.minimum(r,g),b);dd=mx-mn+1e-9
hue=np.where(mx==r,((g-b)/dd)%6,np.where(mx==g,(b-r)/dd+2,(r-g)/dd+4))*60;sat=(mx-mn)/np.maximum(mx,1)
frame=(hue>=26)&(hue<=55)&(sat>0.22)&op
frame=nd.binary_dilation(frame,iterations=1)
#op=op&~frame
closed=nd.binary_dilation(op,iterations=K//2)
lab,n=nd.label(~closed);ext=np.zeros_like(tr)
seeds={lab[int(y*S),int(x*S)] for x,y in [(120,450),(150,560),(600,350),(300,250),(560,300),(250,660)]}
for v in set(lab[0,:])|set(lab[-1,:])|set(lab[:,0])|set(lab[:,-1])|seeds:
    if v: ext|=lab==v
ext=nd.binary_dilation(ext,iterations=K//2+1)
face=nd.binary_opening(tr,iterations=7)
face=nd.binary_dilation(face&~ext,iterations=3)
gap=tr&~ext&P&~face
lab2,n2=nd.label(gap);sz=nd.sum(gap,lab2,range(1,n2+1))
for i,s in enumerate(sz):
    if s<3: gap[lab2==i+1]=0
m=np.array(Image.fromarray((gap*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(float(__import__("os").environ.get("GB","0.6"))))).astype(float)/255
col=(250,248,246);out=A.copy();na=np.maximum(a,m*255)
for i,c in enumerate(col): out[...,i]=(A[...,i]*a/255*(1-m)+c*m)/np.maximum(na/255,1e-3)
out[...,3]=na
Image.fromarray(out.clip(0,255).astype(np.uint8),'RGBA').save(dst)
dbg=Image.new('RGB',(W,H),(255,0,255));t=Image.open(src).convert('RGBA').resize((W,H),Image.LANCZOS);dbg.paste(t,(0,0),t)
d=np.array(dbg);d[gap]=(0,255,255);d[face&P&tr]=(255,255,0);Image.fromarray(d).resize((720,720),Image.NEAREST).save('dbg.png')
print(gap.sum())
