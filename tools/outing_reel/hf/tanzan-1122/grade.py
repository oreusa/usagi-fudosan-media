# 絵の層に色の仕上げ（影は深い葡萄色・明るい所は金・S字・彩度を少し落とす）。b 層だけ光のにじみ
import sys, numpy as np
from PIL import Image, ImageFilter
for f in sys.argv[1:]:
    im=Image.open(f).convert('RGBA');A=np.asarray(im).astype(np.float32)/255;a=A[...,:3];al=A[...,3:]
    L=a.mean(2,keepdims=True);s=a*a*(3-2*a);a=a*.45+s*.55
    sh=np.clip(1-L*2,0,1);a=a*(1-sh*.35)+np.array([.16,.04,.08])*sh*.35
    a=a*(1-.18*(1-sh))+np.array([1,.86,.62])*.18*(1-sh)*L
    g=a.mean(2,keepdims=True);a=g+(a-g)*.85
    if f.endswith('-b.png'):
        b=np.clip((a-.62)/.38,0,1);bb=np.asarray(Image.fromarray((b.mean(2)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(28))).astype(np.float32)[...,None]/255
        a=1-(1-a)*(1-bb*.55*np.array([1,.85,.6]))
    Image.fromarray((np.clip(np.concatenate([a,al],2),0,1)*255).astype(np.uint8)).save(f)
