"""Photo-led candidate stills with deterministic GutKitchen overlays.

The source plates are existing approved brand assets. Each candidate uses
different crops, framing, component systems and shot beats. New provider slots
can later replace these sources without changing brand logic.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import math

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / 'brands/gutkitchen/media/pilot'
OUT = ROOT / 'brands/gutkitchen/creative-engine-v2/candidates'
W, H = 1080, 1920
INK=(28,42,33); CREAM=(255,247,233); TOMATO=(216,75,54); CHEESE=(255,209,102); SKY=(203,232,231); LAV=(221,216,255); GREEN=(49,92,59); WHITE=(255,253,248)

def font(size: int, bold: bool=True):
    for name in ('Arial Bold.ttf' if bold else 'Arial.ttf','/System/Library/Fonts/Supplemental/Arial Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Arial.ttf'):
        try: return ImageFont.truetype(name,size)
        except OSError: pass
    return ImageFont.load_default()

def fit_crop(im: Image.Image, box: tuple[int,int,int,int], zoom: float=1.0, dx: float=0, dy: float=0) -> Image.Image:
    x1,y1,x2,y2=box; tw,th=x2-x1,y2-y1
    scale=max(tw/im.width,th/im.height)*zoom
    nw,nh=int(im.width*scale),int(im.height*scale)
    im=im.resize((nw,nh),Image.Resampling.LANCZOS)
    cx,cy=nw/2+dx*nw, nh/2+dy*nh
    l=max(0,min(nw-tw,int(cx-tw/2))); t=max(0,min(nh-th,int(cy-th/2)))
    return im.crop((l,t,l+tw,t+th))

def rounded(draw: ImageDraw.ImageDraw, box, fill, radius=24, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def shadow_text(draw, xy, value, size, fill=WHITE, anchor='la', stroke=INK, stroke_width=5):
    draw.text(xy,value,font=font(size),fill=fill,anchor=anchor,stroke_width=stroke_width,stroke_fill=stroke)

def badge(draw, x, y, protein='~40g', fibre='15g+', dark=False):
    w,h=420,132; bg=INK if dark else CREAM; fg=CREAM if dark else INK
    rounded(draw,(x,y,x+w,y+h),bg,26)
    rounded(draw,(x+16,y+16,x+192,y+112),CHEESE,18); rounded(draw,(x+214,y+16,x+390,y+112),(244,227,178),18)
    draw.text((x+104,y+42),protein,font=font(34),fill=INK,anchor='mm'); draw.text((x+104,y+82),'PROTEIN',font=font(18),fill=INK,anchor='mm')
    draw.text((x+302,y+42),fibre,font=font(34),fill=INK,anchor='mm'); draw.text((x+302,y+82),'FIBRE',font=font(18),fill=INK,anchor='mm')
    draw.text((x+210,y+124),'label estimate · check your pack',font=font(15),fill=fg,anchor='mm')

def counter(draw, x, y, value, width=820, dark=True, label=None, label_size=27):
    label=label or f'TRACK THE NUMBER MOST PEOPLE IGNORE  ·  {value:.2f}g FIBRE'
    shadow_text(draw,(x,y),label,label_size,CREAM if dark else INK,stroke_width=4)
    draw.rounded_rectangle((x,y+52,x+width,y+82),radius=15,fill=(255,255,255,80) if dark else (28,42,33,45))
    pct=max(.04,min(value/20,1)); draw.rounded_rectangle((x,y+52,x+int(width*pct),y+82),radius=15,fill=CHEESE)
    draw.text((x,y+112),'0g',font=font(18),fill=CREAM if dark else INK); draw.text((x+width,y+112),'20g',font=font(18),fill=CREAM if dark else INK,anchor='ra')

def panel_text(draw, title, subtitle, bg=CREAM, accent=TOMATO):
    rounded(draw,(48,286,1032,590),bg,34); draw.text((88,342),title,font=font(62),fill=INK)
    draw.text((88,426),subtitle,font=font(28),fill=(94,105,95)); draw.rectangle((88,500,330,512),fill=accent)

def ingredient_chips(draw, items, active):
    y=1275
    for i,item in enumerate(items):
        yy=y+i*82; fill=CHEESE if i==active else (255,255,255)
        rounded(draw,(70,yy,760,yy+58),fill,18,INK if i==active else (255,255,255),2)
        draw.ellipse((88,yy+14,122,yy+48),fill=TOMATO if i==active else (244,227,178))
        draw.text((144,yy+29),item,font=font(27),fill=INK,anchor='lm')

def footer(draw, label='REAL NUMBERS. NORMAL INGREDIENTS.'):
    draw.rectangle((0,1760,W,H),fill=INK); draw.text((52,1804),label,font=font(22),fill=CREAM)
    draw.text((52,1850),'GUTKITCHEN',font=font(36),fill=CHEESE); draw.text((W-52,1850),'SAVE THIS FOR YOUR NEXT SHOP',font=font(21),fill=CREAM,anchor='ra')

def grade(im: Image.Image, saturation=1.08, contrast=1.06, brightness=1.0):
    im = ImageEnhance.Color(im).enhance(saturation)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    return ImageEnhance.Brightness(im).enhance(brightness)

def base_photo(name, zoom=1, dx=0, dy=0):
    im=Image.open(PILOT/name).convert('RGB'); return grade(fit_crop(im,(0,0,W,H),zoom,dx,dy))

def render(treatment, index):
    if treatment=='new-a': return render_a(index)
    if treatment=='new-b': return render_b(index)
    return render_c(index)

def render_a(i):
    sources=['hero.png','hero.png','ingredients.png','ingredients.png','pan.png','pan.png','hero.png','hero.png','ingredients.png','hero.png']
    titles=['THE 40g / 15g+ BOWL','THE SPOON TEST.','START WITH ONE TIN.','ADD TOMATO + GREENS.','SIMMER THE BUILD.','THE PROTEIN FINISH.','WATCH THE COUNTER.','THE LABEL DOES THE MATH.','SAVE THE LIST.','ONE BOWL. DONE.']
    im=base_photo(sources[i],1.08 + .025*(i%4),.018*(i-4),.018*(i%3))
    d=ImageDraw.Draw(im,'RGBA')
    d.rectangle((0,0,W,238),fill=(28,42,33,225)); d.text((52,48),'GUTKITCHEN  /  RECIPE BUILD',font=font(25),fill=TOMATO)
    shadow_text(d,(52,112),titles[i],64,CREAM,stroke_width=6); d.text((52,192),'normal supermarket ingredients · exact weights',font=font(25),fill=CREAM)
    badge(d,48,300); counter(d,70,1080,[15.69,15.69,15.04,15.25,15.52,15.69,15.69,15.69,15.69,15.69][i])
    if i in (2,3,4,5,8): ingredient_chips(d,['235g DRAINED CANNELLINI','150g PASSATA + 50g SPINACH','100g LIGHTER MOZZARELLA'],max(0,min(2,i-3)))
    else:
        rounded(d,(70,1280,1010,1535),(255,247,233,238),28); d.text((105,1335),'THE MATH',font=font(26),fill=TOMATO)
        d.text((105,1395),'40.025g protein',font=font(56),fill=INK); d.text((105,1470),'15.69g fibre lower bound · one bowl',font=font(30),fill=INK)
    footer(d)
    return im

def render_b(i):
    sources=['hero.png','hero.png','ingredients.png','ingredients.png','hero.png','ingredients.png','hero.png','ingredients.png','hero.png','hero.png']
    titles=['IF 30g FIBRE SOUNDS IMPOSSIBLE','THE PHOTO PROOF.','ONE TIN DOES THE HEAVY LIFTING.','THE FIX IS NOT A SUPPLEMENT.','WATCH 15.04 → 15.69.','FOUR ITEMS. ONE BOWL.','THE LABEL DOES THE MATH.','BUILD THE BASKET.','THE PAYOFF.','SAVE THE 30g DAY.']
    im=Image.new('RGB',(W,H),SKY); d=ImageDraw.Draw(im,'RGBA')
    d.rectangle((0,0,W,270),fill=INK); d.text((52,42),'GUTKITCHEN  /  FIBRE CALCULATOR',font=font(25),fill=CHEESE)
    shadow_text(d,(52,112),titles[i],56,CREAM,stroke_width=6)
    rounded(d,(48,310,1032,1570),INK,36)
    photo=base_photo(sources[i],1.23 + .02*(i%3),.012*(i-4),.025)
    photo=photo.resize((500,889),Image.Resampling.LANCZOS); im.paste(photo,(82,378))
    d=ImageDraw.Draw(im,'RGBA'); d.rounded_rectangle((82,378,582,1267),radius=24,outline=CHEESE,width=5)
    values=[15.69,15.69,15.04,15.25,15.69,15.69,15.69,15.69,15.69,15.69][i]
    d.text((625,415),'FIBRE COUNTER',font=font(27),fill=CREAM); d.text((625,525),f'{values:.2f}g',font=font(104),fill=CHEESE)
    d.text((625,655),'PER BOWL',font=font(27),fill=CREAM); d.text((625,705),'LOWER BOUND',font=font(27),fill=CREAM)
    counter(d,625,805,values,340,label=f'FIBRE {values:.2f}g · LOWER BOUND',label_size=21); rounded(d,(625,980,985,1165),(255,247,233,235),22)
    d.text((655,1025),'THE BOWL',font=font(22),fill=TOMATO); d.text((655,1075),'beans + tomato +',font=font(29),fill=INK); d.text((655,1120),'greens + mozzarella',font=font(29),fill=INK)
    rounded(d,(82,1325,985,1510),(255,209,102,235),24); d.text((112,1370),'4 ITEMS. NORMAL SHOPPING.',font=font(31),fill=INK)
    d.text((112,1432),'cannellini · passata · spinach · lighter mozzarella',font=font(23),fill=INK)
    footer(d,'THE NUMBER IS THE HOOK.')
    return im

def render_c(i):
    sources=['hero.png','ingredients.png','ingredients.png','ingredients.png','pan.png','pan.png','hero.png','hero.png','ingredients.png','hero.png']
    titles=['PIZZA FLAVOUR. BEAN MATHS.','CRUNCH THE LABEL.','START WITH THE TIN.','BUILD THE COLOUR.','LET IT SIMMER.','MELT THE FINISH.','THE SPOON PAYOFF.','THE NUMBERS HOLD.','SHOP IT.','SAVE IT.']
    blocks=[('40g PROTEIN','one bowl. ordinary ingredients.'),('15.69g FIBRE','label-based lower bound'),('235g CANNELLINI','one tin does the heavy lifting.'),('150g + 50g','passata + spinach'),('SIMMER','ordinary pan. real texture.'),('100g MOZZARELLA','the protein finish'),('THE SPOON TEST.','cheese pull. beans in focus.'),('40.025g PROTEIN','15.69g fibre lower bound'),('SAVE THE LIST.','four items. one useful bowl.'),('SAVE THIS.','for your next shop.')]
    im=base_photo(sources[i],1.22 + .035*(i%4),.018*(i-4),.024*(i%3)); d=ImageDraw.Draw(im,'RGBA')
    d.rectangle((0,0,W,250),fill=(221,216,255,238)); d.text((52,40),'GUTKITCHEN  /  FOOD FIRST',font=font(25),fill=TOMATO)
    shadow_text(d,(52,105),titles[i],60,INK,stroke_width=0)
    badge(d,48,300,dark=True)
    title,sub=blocks[i]; rounded(d,(70,1325,1010,1575),(255,253,248,238),26); d.text((105,1375),title,font=font(58),fill=INK); d.text((105,1465),sub,font=font(29),fill=(94,105,95))
    footer(d,'TACTILE. NUMERIC. SAVEABLE.')
    return im

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for treatment in ('new-a','new-b','new-c'):
        for i in range(10):
            render(treatment,i).save(OUT/f'{treatment}-frame-{i+1:02d}.jpg',quality=88,subsampling=1,optimize=True)
            (OUT/f'{treatment}-frame-{i+1:02d}.svg').unlink(missing_ok=True)
            (OUT/f'{treatment}-frame-{i+1:02d}.png').unlink(missing_ok=True)
    print('OK 30 photo-led candidate stills')
if __name__=='__main__': main()
