"""Live written-answer OCR/retrieval checks. Keyword checks supplement manual review."""
from pathlib import Path
import json,time,re,unicodedata
from PIL import Image,ImageDraw,ImageFont
from beru.engine import Engine

def norm(s):
    return unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()

def main():
    folder=Path('research/written-smoke')/time.strftime('%Y%m%d-%H%M%S');folder.mkdir(parents=True)
    cases=[
        ('structure','Selon le COI, définissez Structure en une ou deux phrases.',lambda a: all(t in norm(a) for t in ['chang','risq','incert'])),
        ('action-time','Selon le COI, distinguez Action et Temps en deux phrases.',lambda a: all(t in norm(a) for t in ['action','temps']) and ('etre' in norm(a) or 'faire' in norm(a) or 'interaction' in norm(a))),
        ('ten-indicators','Citez les dix indicateurs du COI, sans les confondre avec les quatre compétences.',lambda a: all(any(t in norm(a) for t in group) for group in [('environ',),('temps','time'),('action',),('communic',),('espace','space'),('pouvoir','power','puissance'),('individual',),('competitiv',),('structure',),('pensee','thinking','reflexion')])),
    ]
    results=[]
    for model in ['gemini-3.8-flash','gemini-4-hydrogen']:
        for id,prompt,check in cases:
            im=Image.new('RGB',(1200,220),'#dcebed');d=ImageDraw.Draw(im);font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',24)
            import textwrap
            for j,line in enumerate(textwrap.wrap(prompt,85)):d.text((30,30+j*35),line,font=font,fill='#202020')
            t=time.monotonic()
            r=Engine().solve(im,model=model,mode='written',topic='coi',use_cache=False)
            row=dict(model=model,id=id,answer=r['answer'],uncertain=r['uncertain'],seconds=time.monotonic()-t,keyword_check=check(r['answer']),result=r)
            results.append(row);(folder/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
            print(json.dumps({k:v for k,v in row.items() if k!='result'},ensure_ascii=False),flush=True)
    print('Results:',folder,flush=True)
if __name__=='__main__':main()
