"""Assemble actual browser captures for visual inspection. Does not render scenes."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,os
ROOT=Path(__file__).resolve().parents[2]
font=ImageFont.load_default(size=18)
def sheet(entries,path,cols=2,thumb=(900,506)):
 rows=(len(entries)+cols-1)//cols;w,h=thumb;im=Image.new('RGB',(w*cols,(h+30)*rows),'#edf3f7');draw=ImageDraw.Draw(im)
 for i,(name,file) in enumerate(entries):
  x=(i%cols)*w;y=(i//cols)*(h+30);draw.text((x+16,y+6),name,font=font,fill='#24465c');im.paste(Image.open(file).convert('RGB').resize(thumb,Image.Resampling.LANCZOS),(x,y+30))
 path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
for size in ['1920x1080','2560x1440']:
 folder=ROOT/'qa/captures'/size
 for part,count in [('F',22),('D',24)]:
  for start in range(0,count,4):
   names=[part+str(i).zfill(2) for i in range(start,min(start+4,count))]
   if all((folder/(n+'.png')).exists() for n in names):sheet([(n+' / '+size,folder/(n+'.png')) for n in names],ROOT/'qa/review-sheets'/size/(names[0]+'-'+names[-1]+'.png'))
wall=['F01','F08','F10','F14','F19','D05','D12','D16','D23']
if all((ROOT/'qa/captures/1920x1080'/(n+'.png')).exists() for n in wall):
 sheet([(n,ROOT/'qa/captures/1920x1080'/(n+'.png')) for n in wall],ROOT/'qa/VISUAL_WALL.png',3,(960,540))
# User-owned recovered frames are included only as explicit comparison evidence.
recovered=Path(os.environ.get('PT_RECOVERED_DIR',str(ROOT/'references/recovered')))
if recovered.exists():
 for name in ['F01','F08','F14','F19','D05','D23']:
  sheet([('RECOVERED / '+name,recovered/('v1-'+name+'.png')),('REBUILT / '+name,ROOT/'qa/captures/1920x1080'/(name+'.png'))],ROOT/'qa/baseline-comparison'/(name+'.png'),2,(960,540))
print('Generated review sheets from existing browser screenshots.')
