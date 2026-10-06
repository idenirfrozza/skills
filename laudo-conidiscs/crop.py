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
