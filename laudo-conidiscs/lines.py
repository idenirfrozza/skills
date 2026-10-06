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
