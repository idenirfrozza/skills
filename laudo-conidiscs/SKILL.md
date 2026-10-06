---
name: "laudo-conidiscs"
description: "Recria o Relatório Dimensional e Qualidade CONIDISCS escaneado trocando o manuscrito por fonte manuscrita, analisa desvios contra as tolerâncias e marca em amarelo o que está fora."
---

# Laudo CONIDISCS – Dimensional e Qualidade

Use quando chegar um PDF escaneado do formulário **"RELATÓRIO DIMENSIONAL E QUALIDADE (Quality Control Report)"** da CONIDISCS / ANDRITZ preenchido à mão, ou quando o usuário pedir para "fazer conforme instruções" no projeto Laudo Condiscs.

## Resultado esperado
- Um PDF com as **mesmas páginas, tamanhos, cores e layout** do original.
- Todo texto manuscrito é apagado e reescrito **no mesmo lugar** com fonte manuscrita, com a mesma informação.
- O fundo onde havia caneta deve manter a textura do papel, e as linhas da tabela não podem mostrar que algo foi apagado.
- As medidas fora da tolerância ficam com a célula pintada de **amarelo**: tabela de dimensões e Somatória da Montagem do Pacote.
- Nome do arquivo: `AAAAMMDDHHMM Dimensional e Qualidade.pdf`, com data e hora atuais no fuso do usuário (America/Sao_Paulo). Exemplo: `202610051019 Dimensional e Qualidade.pdf`.

## Ferramentas (já testadas)
- `pdfimages -png in.pdf img/p` extrai cada página como imagem (o PDF é uma imagem por página a 72 ppi, por isso px = pt).
- Python com `opencv` (cv2), `numpy`, `Pillow`, `pypdf`. O **PyMuPDF não instala** no ambiente, então não use.
- Fonte manuscrita: `/mnt/skills/examples/canvas-design/canvas-fonts/NothingYouCouldDo-Regular.ttf`. Google Fonts e npm ficam bloqueados.
- `img2pdf --imgsize 72dpi p0.jpg p1.jpg ... -o "<nome>.pdf"` monta o PDF. Salve as páginas em JPEG com qualidade 90 e `subsampling=0`.
- Copie o upload para o diretório de trabalho antes de mexer. O original não é alterado.

## Passo a passo
1. **Extrair e olhar.** Extraia as páginas e gere prévias reduzidas (cerca de 0,4×) para ler. Para transcrever, recorte trechos com uma grade de coordenadas, usando o helper `crop.py` (seção Helpers), em escala de 0,6× a 2×.
2. **Achar as células com precisão.** Use `lines.py` (seção Helpers) para obter as linhas horizontais e verticais da tabela. Isso se faz numa coluna x (cada página é uma foto levemente inclinada, então meça as linhas da esquerda e da direita em separado) e numa linha y. As caixas dos campos são o **interior da célula**: linha +4 px até linha −4 px.
3. **Transcrever** cada campo para um arquivo `campos_pN.py` com `F=[(x0,y0,x1,y1,'texto'), ...]`.
   - Assinaturas usam `{'sig':1}`, com a caixa acima do nome impresso.
   - Rabiscos de anulação e restos de assinatura sob o nome impresso usam `{'erase_only':1}`: o campo fica em branco.
4. **Processar** cada página com `laudo_process.py` (abaixo): `python3 laudo_process.py img/p-000.png campos_p0.py out0.png destaques_p0.json`.
5. **Conferir visualmente** cada página. Faça zoom 1:1 nas áreas onde a caneta cruzava linhas. Se sobrar traço que passou para a célula vizinha, acrescente uma caixa `erase_only` sobre ele.
6. **Analisar os desvios** (seção abaixo), gerar `destaques_pN.json` e reprocessar.
7. **Montar o PDF** com o nome no padrão, enviar ao usuário e listar:
   - leituras incertas, para conferência;
   - a tabela de valores fora da tolerância.

## Leitura do manuscrito: convenções deste formulário
- O "1" é escrito como um **"J"** com gancho, por exemplo "86J.6" = 861.6 e "J3.2/J3.9" = 13.2/13.9.
- A barra "/" também pode parecer um "1". Separe pelo contexto: a linha 04 tem dois valores, do tipo "13.2/13.9".
- Os decimais às vezes saem sem ponto ("05" = 0.5, "86J9" = 861.9). Registre a leitura escolhida e avise o usuário.
- Verificação, Resp. e Chanfro são "ok" ou "OK". Grau é 6.3 e rotação é 800.
- Assinaturas: "Juliano" (Juliano G. de Oliveira) e "Euclides Neto" (Euclides J. Solanha Neto). Data no formato "02/10/26".
- NF da rastreabilidade: um número como "7733" ou "- NF-7731", escrito igual ao original.
- Sempre liste ao usuário as leituras incertas.

## Estrutura do formulário
- Cabeçalho impresso com DESCRIÇÃO, SAP, PO e OP. Não há manuscrito no cabeçalho.
- **Tabela de dimensões**, colunas: Item | Especificação | **Dimensão [mm]** | **tolerância** | Fixo 1 | Fixo 3 | **Dimensão [mm]** | **tolerância** | Rotor Direito | Rotor Esquerdo.
  - Fixo 1 e Fixo 3 usam a **primeira** Dimensão e a tolerância ao lado dela.
  - Rotor Direito e Rotor Esquerdo usam a **segunda** Dimensão e a tolerância ao lado dela.
  - Linhas 01 a 12: OD, ID, espessura do disco, altura da barra, espaçamento, espessura da barra, ângulo, planicidade frontal, planicidade traseira, furação, chanfro principal, chanfro quebradas.
- Instrumentos de medição (ex.: P45, P2) e **Montagem do Pacote** (Dimensão, tolerância +2/−4, Somatória).
- Inspeção final: coluna Verificação dos itens 12 a 18, rastreabilidade (NF Lâmina, Chapas, Bases…), balanceamento (Grau, Rotação, Residual no Rotativo 02), Tolerância Linear (Resp.), assinaturas e data.

## Regras da análise de desvio
Leia o nominal e a tolerância **de cada página**, porque eles mudam entre laudos. Faixa permitida = [nominal − desvio_inferior, nominal + desvio_superior], com **limites inclusivos**.
- `0` em cima e `-2` embaixo → [N−2, N].
- Um único `-1`, `-2` ou `-1.0` → só para baixo: [N−1, N] ou [N−2, N]. Valor acima do nominal está fora. Avise o usuário que essa foi a interpretação.
- `±x` → [N−x, N+x].
- Planicidade (nominal "±0.5") → o valor medido deve ser ≤ 0.5.
- Nominal duplo como "3.0/6.5" com ±0.5 → compare cada valor com o nominal na mesma posição.
- Célula com dois valores medidos ("13.6/15.1") → fora se **qualquer** valor estiver fora.
- `N/A`, GABARITO, chanfro 45° com "OK" e células vazias → não analisar.
- **Montagem do Pacote**: Somatória vs Dimensão com +2/−4 → [D−4, D+2]. Exemplos: 132 → [128, 134], 140 está fora; 144 → [140, 146], 147,6 está fora; 148 → [144, 150], 150,9 está fora. Aceite vírgula como decimal.
- Para cada célula fora, adicione no `destaques_pN.json` a caixa interior dessa célula. No Rotor Esquerdo, limite x1 à borda da tabela.
- Na resposta, mostre uma tabela: Pág. | Campo | Valor | Faixa permitida, com o valor fora em negrito.

Script de checagem (adapte `S` ao que estiver impresso em cada página):
```python
# S[p]['L'|'R'][linha] = (nominal ou (n1,n2), desvio_inf, desvio_sup)
def fora(texto, nom, mi, pl):
    vals=[float(v) for v in texto.replace(',','.').split('/')]
    noms=nom if isinstance(nom,tuple) else (nom,)*len(vals)
    return [v for v,n in zip(vals,noms) if not (n-mi-1e-9 <= v <= n+pl+1e-9)]
```

## Como o processamento funciona (laudo_process.py)
1. **Fundo local** = fechamento morfológico 21×21 seguido de mediana 31. **Tinta** = pixel mais de 45 níveis abaixo do fundo.
2. **Linhas da tabela** = abertura com kernel 80×1 e 1×80. Elas ficam fora dos candidatos a manuscrito.
3. Cada campo pega os componentes conexos cujo **centróide** cai na caixa (+10 px de folga). Isso evita apagar texto impresso ao lado ("±0.5", "12.0", nome impresso). Hastes verticais finas (≤6 px de largura e ≥38 px de altura) são linhas e são ignoradas.
4. **Transbordo**: um pedaço pequeno de tinta azul (B−R > 16) junto de uma linha e a até 8 px do traço apagado também é apagado. Esse é o caso do traço que cruzou para a célula vizinha.
5. **Inpaint TELEA** (raio 6) sobre a tinta dilatada 9×9 e sobre as linhas próximas.
6. **Granulação**: ruído gaussiano com o desvio-padrão medido do papel, só na área restaurada.
7. **Reconstrução das linhas**: cada linha longa é ajustada por uma reta, e o perfil é copiado de trechos limpos da mesma linha. Nos cruzamentos usa-se o mínimo (escuro), para manter as duas linhas.
8. **Amarelo** por multiplicação (BGR 70, 238, 255), que mantém a textura e o texto.
9. **Texto**:
   - Cor = mediana do terço mais escuro da tinta original do campo.
   - Altura do dígito = min(0,72 × altura da célula, 36 px). Assinatura: 44 px, apoiada na linha.
   - Centralizado no x da tinta original e no y da célula.
   - Ponto decimal desenhado como bolinha, "/" desenhada como traço inclinado, contorno de 1 px e blur de 0,7 px.

```python
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
```

## Helpers
`lines.py`: posições das linhas da tabela.
```python
import numpy as np, cv2, sys
# uso: python3 lines.py pagina.png x1,x2 ymin ymax [y1,y2]
im=cv2.imread(sys.argv[1]); xs=[int(v) for v in sys.argv[2].split(',')]; y0,y1=int(sys.argv[3]),int(sys.argv[4])
L=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
bg=cv2.medianBlur(cv2.morphologyEx(L,cv2.MORPH_CLOSE,np.ones((21,21),np.uint8)),31).astype(int)
d8=((L.astype(int)<bg-45)*255).astype(np.uint8)
h=cv2.morphologyEx(d8,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(80,1)))
v=cv2.morphologyEx(d8,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(1,80)))
def runs(col,off):
    d=np.diff(np.concatenate([[0],(col>0).astype(int),[0]])); s=np.nonzero(d==1)[0]; e=np.nonzero(d==-1)[0]
    return [int((a+b)/2+off) for a,b in zip(s,e)]
for x in xs: print('x',x,'linhas horizontais',runs(h[y0:y1,x],y0))
if len(sys.argv)>5:
    for y in map(int,sys.argv[5].split(',')): print('y',y,'linhas verticais',runs(v[y,:],0))
```
`crop.py`: recorte com grade de coordenadas, para ler e posicionar.
```python
import sys
from PIL import Image, ImageDraw, ImageFont
# uso: python3 crop.py pagina.png x0 y0 x1 y1 escala saida.jpg
src,x0,y0,x1,y1,s,dst=sys.argv[1:8]; x0,y0,x1,y1=map(int,(x0,y0,x1,y1)); s=float(s)
im=Image.open(src).crop((x0,y0,x1,y1)).convert('RGB'); d=ImageDraw.Draw(im)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
for x in range((x0//50+1)*50,x1,50):
    d.line([(x-x0,0),(x-x0,y1-y0)],fill=(255,0,0) if x%100==0 else (255,180,180))
    if x%100==0: d.text((x-x0+2,2),str(x),fill=(255,0,0),font=f)
for y in range((y0//50+1)*50,y1,50):
    d.line([(0,y-y0),(x1-x0,y-y0)],fill=(0,160,0) if y%100==0 else (170,230,170))
    if y%100==0: d.text((2,y-y0+2),str(y),fill=(0,140,0),font=f)
im.resize((int(im.width*s),int(im.height*s))).save(dst,quality=88)
```

## Exemplo de campos (página da tabela)
```python
C={'F1':(882,1074),'F3':(1082,1274),'RD':(1550,1744),'RE':(1752,1948)}  # x interior das colunas
HL=[702,751,799,847,895,943,991,1038,1086,1134,1181,1222]               # linhas horizontais (lado Fixo)
HR=[695,744,793,841,889,938,985,1033,1081,1129,1177,1217]               # linhas horizontais (lado Rotor)
def cell(c,r,t):
    hl=HL if c in('F1','F3') else HR
    return (C[c][0],hl[r-1]+4,C[c][1],hl[r]-4,t)
F=[cell('F1',1,'862.6'), cell('F1',4,'13.2/13.9'), (1553,1918,1815,1958,'',{'erase_only':1}),
   (440,2300,740,2390,'Juliano',{'sig':1})]
```

## Cuidados
- Não apague a mancha de tinta do papel que não é escrita: ela faz parte do original.
- O texto impresso preto fica intacto porque a seleção é pelo centróide. Não aumente a folga sem conferir.
- Se o layout ou as fontes disponíveis mudarem, confira primeiro uma página antes de processar todas.
- Envie o PDF com SendUserFile e escreva a resposta em português.