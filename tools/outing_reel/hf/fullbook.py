# 周りなし：本を初めから画面いっぱい（1080x1920）にする。python3 fullbook.py index.html
import sys,re
p=sys.argv[1];h=open(p).read()
if '/* fullbook */' in h: sys.exit('already')
css='''
/* fullbook */
#book{left:0 !important;top:0 !important;width:1080px !important;height:1920px !important}
#halo{display:none !important}
#burst{left:0 !important;top:0 !important;width:1080px !important;height:1920px !important}
.cap{left:88px !important;right:auto !important;bottom:209px !important;transform-origin:0 100%;scale:1.36}
.info{padding:170px 64px 64px !important}
.info .ph{left:64px !important;right:64px !important;bottom:150px !important;height:820px !important}
#tab{right:70px !important;top:0 !important}
#h0{top:170px !important}
#ph{left:92px !important;top:470px !important;width:480px !important;height:960px !important}
#h1{right:52px !important;top:700px !important;width:380px !important}
#endb{top:1560px !important}
'''
h=h.replace('</style>',css+'</style>',1)
n0=len(h)
h=re.sub(r'tl\.fromTo\("#stage",\{scale:\.97\},\{scale:1\.02,[^;]*\);','',h)
h=re.sub(r'tl\.to\("#stage",\{scale:1\.36[^;]*\);','',h)
h=re.sub(r'tl\.to\("#stage",\{scale:1,x:0,y:0[^;]*\);','',h)
print('removed',n0-len(h)-0)
open(p,'w').write(h)
