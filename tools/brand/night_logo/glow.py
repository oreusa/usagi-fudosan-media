import sys, numpy as np, colorsys
from PIL import Image, ImageFilter, ImageDraw
src,dst,prev=sys.argv[1:4]
import os
SC=float(os.environ.get('SC','1'))
im=Image.open(src).convert('RGBA'); im=im if os.environ.get('NORESIZE') else im.resize((im.width*2,im.height*2),Image.LANCZOS); W,H=im.size
S=4  # work at 4x? keep native but upscale for quality
base=Image.new('RGBA',(W,H),(0,0,0,0))
disc=Image.new('L',(W*4,H*4),0);ImageDraw.Draw(disc).ellipse((0,0,W*4-1,H*4-1),fill=255);disc=disc.resize((W,H),Image.LANCZOS)
white=Image.new("RGBA",(W,H),(186,187,190,255));white.putalpha(disc)
base.alpha_composite(white)
a=np.array(im).astype(float)
# logo pixels over white
A=np.array(im).astype(float)
mnv=A[...,:3].min(axis=2)
from collections import deque
wh=(mnv>225)&(A[...,3]>0); out=np.zeros(wh.shape,bool); q=deque()
for y in range(H):
    for x in range(W):
        if (y in (0,H-1) or x in (0,W-1)) and wh[y,x]: out[y,x]=1;q.append((y,x))
while q:
    y,x=q.popleft()
    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
        Y,X=y+dy,x+dx
        if 0<=Y<H and 0<=X<W and wh[Y,X] and not out[Y,X]: out[Y,X]=1;q.append((Y,X))
near=np.array(Image.fromarray((out*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)))>0
k=np.where(out,1.0,np.where(near,np.clip((mnv-200)/50,0,1),0.0))
A[...,3]=A[...,3]*(1-k)
lay=Image.fromarray(A.astype(np.uint8),'RGBA'); base.alpha_composite(lay)
r,g,b,al=[a[...,i]/255 for i in range(4)]
mx=np.maximum(np.maximum(r,g),b);mn=np.minimum(np.minimum(r,g),b);sat=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0)
h=np.zeros_like(r)
d=mx-mn+1e-9
h=np.where(mx==r,((g-b)/d)%6,np.where(mx==g,(b-r)/d+2,(r-g)/d+4))*60
m=((h>=26)&(h<=55)&(sat>0.22)&(al>0.3)&(mx<0.97)).astype(float)*al
M=Image.fromarray((m*255).astype(np.uint8))
M=M.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
# glow halo
for rad,col,k in ((5,(255,180,80),0.8),(1.6,(255,214,140),1.0)):
    g_=M.filter(ImageFilter.GaussianBlur(rad*SC)); ga=np.clip(np.array(g_).astype(float)*k*1.6,0,255)
    L=Image.new('RGBA',(W,H),col+(0,)); L.putalpha(Image.fromarray(ga.astype(np.uint8)))
    base.alpha_composite(L)
# bright frame on top
F=Image.new('RGBA',(W,H),(255,236,190,0));F.putalpha(M);base.alpha_composite(F)
# clip to disc + glow allowed slightly outside: keep disc clip for cleanliness
out=Image.new('RGBA',(W,H),(0,0,0,0));out.paste(base,(0,0),disc)
out.save(dst)
pv=Image.new('RGBA',(W,H),(20,26,40,255));pv.alpha_composite(out);pv.convert('RGB').resize((W*2,H*2)).save(prev)
Image.fromarray((m*255).astype(np.uint8)).save(prev.replace('.png','-mask.png'))
