"""Remove manuscrito de uma página escaneada e reescreve com fonte manuscrita.
Uso: python3 laudo_process.py <pagina.png> <campos.py> <saida.png> [destaques.json]
campos.py define F = [(x0,y0,x1,y1,'texto'[,opts]), ...]  (caixa = interior da célula)
  opts: {'sig':1} assinatura (tamanho fixo, apoiada na linha) | {'erase_only':1} só apagar
destaques.json = [[x0,y0,x1,y1], ...] células a pintar de amarelo (multiplicação)."""
import numpy as np, cv2, sys, json, runpy, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SRC,FIELDS,OUT=sys.argv[1:4]; HL=sys.argv[4] if len(sys.argv)>4 else None
F=runpy.run_path(FIELDS)['F']
FONT=os.environ.get('HAND_FONT','/mnt/skills/examples/canvas-design/canvas-fonts/NothingYouCouldDo-Regular.ttf')
im=cv2.imread(SRC); H,W=im.shape[:2]
L=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
bg=cv2.medianBlur(cv2.morphologyEx(L,cv2.MORPH_CLOSE,np.ones((21,21),np.uint8)),31).astype(int)
dark=L.astype(int)<bg-45
d8=dark.astype(np.uint8)*255
h=cv2.morphologyEx(d8,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(80,1)))
v=cv2.morphologyEx(d8,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(1,80)))
lines=(h|v)>0
cand=(dark&~lines).astype(np.uint8)
n,lab,st,cen=cv2.connectedComponentsWithStats(cand,connectivity=8)
erase=np.zeros((H,W),np.uint8); erase_ns=np.zeros((H,W),np.uint8); places=[]; PAD=10
for f in F:
    x0,y0,x1,y1,txt=f[:5]; o=f[5] if len(f)>5 else {}
    ids=[i for i in range(1,n) if x0-PAD<=cen[i][0]<=x1+PAD and y0-PAD/2<=cen[i][1]<=y1+PAD/2
         and st[i][4]>=6 and not (st[i][2]<=6 and st[i][3]>=38)]
    m=np.isin(lab,ids) if ids else np.zeros((H,W),bool)
    ys,xs=np.nonzero(m)
    if len(xs)<20: print('SEM TINTA',txt,f[:4]); continue
    col=np.median(im[m][np.argsort(L[m])[:max(5,len(xs)//3)]],0)
    erase|=m.astype(np.uint8)
    if not o.get('sig'): erase_ns|=m.astype(np.uint8)
    bb=(np.percentile(xs,2),np.percentile(ys,2),np.percentile(xs,98),np.percentile(ys,98))
    if not o.get('erase_only'): places.append((txt,bb,col,o,(x0,y0,x1,y1)))
# pedaços de traço que atravessaram uma linha da tabela (tinta azul, perto de linha)
grow=cv2.dilate(erase_ns*255,np.ones((17,17),np.uint8))>0
nearline=cv2.dilate(lines.astype(np.uint8),np.ones((9,9),np.uint8))>0
BR=im[:,:,0].astype(int)-im[:,:,2].astype(int)
sel=set(np.unique(lab[erase>0]).tolist())
for i in range(1,n):
    if i in sel or st[i][4]<6 or st[i][4]>600 or st[i][3]>70: continue
    x,y,w,hh,_=st[i]; cm=lab[y:y+hh,x:x+w]==i
    if grow[y:y+hh,x:x+w][cm].any() and nearline[y:y+hh,x:x+w][cm].any() and BR[y:y+hh,x:x+w][cm].mean()>16:
        erase|=(lab==i).astype(np.uint8)
# máscara: tinta + halo + linhas próximas (as linhas são reconstruídas depois)
near=cv2.dilate(erase*255,np.ones((31,31),np.uint8))>0
emask=cv2.dilate(erase*255,np.ones((9,9),np.uint8))
emask[(cv2.dilate(lines.astype(np.uint8),np.ones((5,5),np.uint8))>0)&near]=255
near=cv2.dilate(emask,np.ones((5,5),np.uint8))>0
out=cv2.inpaint(im,emask,6,cv2.INPAINT_TELEA)
# granulação do papel
rng=np.random.default_rng(0)
hp=im.astype(np.float32)-cv2.GaussianBlur(im,(0,0),3).astype(np.float32)
sd=float(np.std(hp[(~dark)&(emask==0)][::50]))
noise=cv2.GaussianBlur(rng.normal(0,sd*0.9,(H,W,3)).astype(np.float32),(0,0),0.7)*1.4
mm=cv2.GaussianBlur(emask.astype(np.float32)/255,(0,0),1.5)[...,None]
out=np.clip(out.astype(np.float32)+noise*mm,0,255).astype(np.uint8)
def repair(out,src,lm,near,emask,perp):
    """Reconstrói linhas horizontais copiando o perfil de trechos limpos da mesma linha."""
    n_,lb,st_,_=cv2.connectedComponentsWithStats(lm.astype(np.uint8),connectivity=8)
    Hh,Ww=lm.shape; HB=8
    for i in range(1,n_):
        x,y,w,hh,_=st_[i]
        if w<150: continue
        xs=np.arange(x,x+w); sub=lb[y:y+hh,x:x+w]==i
        cnt=sub.sum(0); ok=(cnt>0)&(cnt<=np.median(cnt[cnt>0])+1)
        if ok.sum()<20: continue
        ctr=(sub*np.arange(y,y+hh)[:,None]).sum(0)/np.maximum(cnt,1)
        yc=np.polyval(np.polyfit(xs[ok],ctr[ok],1),xs)
        rng_=lambda c:(max(0,int(c)-HB-4),int(c)+HB+5)
        need=np.array([near[max(0,int(c)-HB):int(c)+HB+1,xx].any() for xx,c in zip(xs,yc)])
        if not need.any(): continue
        clean=~np.array([emask[slice(*rng_(c)),xx].any() or perp[slice(*rng_(c)),max(0,xx-12):xx+13].any() for xx,c in zip(xs,yc)])
        cross=np.array([perp[slice(*rng_(c)),max(0,xx-3):xx+4].any() for xx,c in zip(xs,yc)])
        ci=np.nonzero(clean)[0]
        if len(ci)==0: continue
        for j in np.nonzero(need)[0]:
            k=ci[np.argmin(np.abs(ci-j))]; off=(j%23)-11
            k2=ci[np.argmin(np.abs(ci-(k+off*(1 if k<j else -1))))]
            xa,xb=xs[j],xs[k2]; ca,cb=int(round(yc[j])),int(round(yc[k2]))
            for o_ in range(-HB,HB+1):
                ya,yb=ca+o_,cb+o_
                if 0<=ya<Hh and 0<=yb<Hh:
                    if cross[j]: out[ya,xa]=np.minimum(out[ya,xa],src[yb,xb])
                    else:
                        wg=1.0 if abs(o_)<HB-2 else 0.5
                        out[ya,xa]=(wg*src[yb,xb]+(1-wg)*out[ya,xa]).astype(np.uint8)
    return out
out=repair(out,im,h>0,near,emask,v>0)
T=lambda a:np.ascontiguousarray(a.transpose(1,0,2) if a.ndim==3 else a.T)
out=T(repair(T(out),T(im),T(v>0),T(near),T(emask),T(h>0)))
if HL and os.path.exists(HL):
    mul=np.array([70,238,255],np.float32)/255   # amarelo (BGR) por multiplicação
    for x0,y0,x1,y1 in json.load(open(HL)):
        x0-=2;x1+=2;y0-=1;y1+=1
        out[y0:y1,x0:x1]=np.clip(out[y0:y1,x0:x1].astype(np.float32)*mul,0,255).astype(np.uint8)
# texto manuscrito
pil=Image.fromarray(cv2.cvtColor(out,cv2.COLOR_BGR2RGB)).convert('RGBA')
def runs(t):
    r=[];cur=''
    for ch in t:
        if ch in '/.':
            if cur: r.append((cur,0)); cur=''
            r.append((ch,1 if ch=='/' else 2))
        else: cur+=ch
    if cur: r.append((cur,0))
    return r
def glyph_h(size):
    b=ImageFont.truetype(FONT,size).getbbox('8'); return b[3]-b[1]
def measure(t,size):
    f=ImageFont.truetype(FONT,size); w=0
    for s,k in runs(t):
        w+= size*0.16 if k==2 else (glyph_h(size)*0.45+size*0.14 if k==1 else f.getlength(s))
    return w
DIG=glyph_h(100)/100
for txt,(bx0,by0,bx1,by1),col,o,(X0,Y0,X1,Y1) in places:
    ch,cw=Y1-Y0,X1-X0; sig=o.get('sig')
    dh=o.get('h',44 if sig else min(0.72*ch,36)); size=int(dh/DIG)
    while measure(txt,size)>cw*0.97 and size>20: size-=1
    tw=measure(txt,size); cx=(bx0+bx1)/2
    x=cx-tw/2 if sig else min(max(cx-tw/2,X0+2),X1-2-tw)
    cy=Y1-dh/2-12 if sig else (Y0+Y1)/2-3
    layer=Image.new('RGBA',pil.size,(0,0,0,0)); d=ImageDraw.Draw(layer)
    f=ImageFont.truetype(FONT,size); c=tuple(int(t) for t in col[::-1])+(240,)
    a=f.getbbox('8'); ytop=cy-(a[1]+a[3])/2; gh=a[3]-a[1]; sw=max(2,int(size*0.045))
    for s,k in runs(txt):
        if k==2:   # ponto decimal visível
            r=max(2.8,size*0.048); px=x+size*0.07; py=ytop+a[3]-r*1.1
            d.ellipse([px-r,py-r,px+r,py+r],fill=c); x+=size*0.16
        elif k==1: # barra inclinada (a "/" da fonte parece um "1")
            x0_=x+size*0.06; d.line([(x0_,cy+gh*0.55),(x0_+gh*0.45,cy-gh*0.55)],fill=c,width=sw)
            x+=gh*0.45+size*0.14
        else:
            d.text((x,ytop),s,font=f,fill=c,stroke_width=1 if size>=26 else 0,stroke_fill=c); x+=f.getlength(s)
    pil=Image.alpha_composite(pil,layer.filter(ImageFilter.GaussianBlur(0.7)))
pil.convert('RGB').save(OUT); print('ok',len(places),'campos')
