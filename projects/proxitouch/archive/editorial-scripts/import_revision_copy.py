"""Import approved formal copy, not its animation/development instructions."""
from pathlib import Path
import re,json
root=Path(__file__).resolve().parents[2]
text=(root/'revision-spec/01_FINAL_SCENE_PLAN_AND_COPY.md').read_text()
copy={}
for m in re.finditer(r'^## (\d{2})\uff5c(.+)$',text,re.M):
 end=re.search(r'^## \d{2}\uff5c|^# PART ',text[m.end():],re.M)
 chunk=text[m.end():m.end()+end.start()] if end else text[m.end():]
 body=chunk.split('###')[0].strip().rstrip('-').strip()
 for label in ['\u5c0f\u5b57\u8bf4\u660e\uff1a','\u5c0f\u6807\u6ce8\uff1a','\u6700\u540e\u53ea\u7559\u4e00\u53e5\uff1a']:body=body.replace(label,'')
 copy['S'+m[1]]={'title':m[2],'body':body,'source':'01_FINAL_SCENE_PLAN_AND_COPY.md','page':int(m[1])}
copy['S00']={'title':'ProxiTouch','body':'**\u63a5\u8fd1\u2014\u89e6\u78b0\u2014\u538b\u529b\u8fde\u7eed\u611f\u77e5**\n\n\u4ece\u7a7a\u95f4\u573a\u5230\u63a5\u89e6\u754c\u9762','source':'01_FINAL_SCENE_PLAN_AND_COPY.md','page':0}
# R3 changes only the ending. Preserve the scoped override on reimport.
override=root/'revision-spec/R3_COPY_OVERRIDES.json'
if override.exists():
 for sid,value in json.loads(override.read_text()).items():
  if sid!='S22':raise ValueError('R3 permits only the S22 copy override')
  copy[sid]=value
(root/'source/src/scenes/copy.ts').write_text('// Approved R2 copy with the explicit R3 S22 override.\nexport const COPY:Record<string,{title:string;body:string;source:string;page:number}>='+json.dumps(copy,ensure_ascii=False,indent=2)+';\n')
assert len(copy)==23
print('Imported cover + 22 approved pages')
