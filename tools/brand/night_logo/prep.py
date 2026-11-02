# 600pxの元ロゴ(links/assets/logo.png)を360pxに縮め、顔の半透明(ざらつき)を消して透明にする
import sys, numpy as np
from PIL import Image, ImageFilter
src,dst=sys.argv[1:3]
im=Image.open(src).convert('RGBA').resize((360,360),Image.LANCZOS)
A=np.array(im).astype(float); a=A[...,3]
b=np.array(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.BoxBlur(3))).astype(float)
A[(a<150)&(b<150)&(a>0),3]=0
Image.fromarray(A.astype(np.uint8)).save(dst)
