from pathlib import Path
from PIL import Image,ImageDraw
import json,math
ROOT=Path(__file__).resolve().parents[2]
def sheet(files,dest,cols=2,w=960):
 h=w*9//16;bar=27;rows=math.ceil(len(files)/cols);im=Image.new('RGB',(cols*w,rows*(h+bar)),(236,242,246));d=ImageDraw.Draw(im)
 for i,f in enumerate(files):
  x=i%cols*w;y=i//cols*(h+bar);img=Image.open(f).convert('RGB').resize((w,h));im.paste(img,(x,y+bar));d.text((x+12,y+7),f.stem,fill=(29,66,91))
 dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest)
for size in ['1920x1080','2560x1440']:
 folder=ROOT/'qa/scenes'/size
 if not folder.exists():continue
 files=sorted(folder.glob('S*.png'))
 for i in range(0,len(files),4):sheet(files[i:i+4],ROOT/'qa/review'/size/f'{files[i].stem}-{files[min(i+3,len(files)-1)].stem}.png')
 for mode in ['transitions','ambient','explore']:
  folder=ROOT/'qa'/mode/size
  if not folder.exists():continue
  groups={}
  for f in sorted(folder.glob('*.png')):groups.setdefault(f.stem.split('-')[0],[]).append(f)
  for key,files in groups.items():sheet(files,ROOT/'qa/review'/size/f'{mode}-{key}.png',cols=3 if len(files)>4 else 2,w=640 if len(files)>4 else 960)
files=[ROOT/'qa/scenes/1920x1080'/f'S{i:02}.png' for i in [1,2,3,4,5,6,7,10,13,18,20,22]]
if all(f.exists() for f in files):sheet(files,ROOT/'qa/VISUAL_WALL.png',cols=3,w=640)
print('Sheets updated')

# Additional practical review views; sources remain unmodified raw browser PNGs.
for size in ['1920x1080','2560x1440']:
 files=sorted((ROOT/'qa/explore'/size).glob('*.png'))
 if files:sheet(files,ROOT/'qa/review'/size/'explore-overview.png',cols=3,w=640)
files=sorted((ROOT/'qa/extras').glob('hero-*.png'))
if files:sheet(files,ROOT/'qa/review/hero-quality.png',cols=2,w=960)
# Detail crops for the merge, keeping every raw screenshot available.
files=[ROOT/'qa/transitions/1920x1080'/f'S20-{x:04}.png' for x in [340,400,450,500,560,610]]
im=Image.new('RGB',(1600,3*520),(236,242,246));draw=ImageDraw.Draw(im)
for i,f in enumerate(files):
 if not f.exists():continue
 src=Image.open(f).convert('RGB').crop((810,260,1790,855)).resize((800,486));x=i%2*800;y=i//2*520;im.paste(src,(x,y+28));draw.text((x+12,y+8),f.stem,fill=(29,66,91))
im.save(ROOT/'qa/review/S20-merge-detail.png')
