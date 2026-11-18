"""Three synthetic smoke cases, matched Flash/Hydrogen, model-call latency only."""
from pathlib import Path
import io,json,time,statistics
from PIL import Image,ImageDraw,ImageFont
from beru.providers import answer
from benchmarks.run import label

def chart():
    im=Image.new('RGB',(700,450),'white');d=ImageDraw.Draw(im)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',23)
    d.line((70,40,70,380,640,380),fill='black',width=3)
    for x,height,name in [(150,120,'Nord'),(330,280,'Sud'),(510,190,'Est')]:
        d.rectangle((x,380-height,x+85,379),fill='#2478bf')
        d.text((x,395),name,font=font,fill='black')
    b=io.BytesIO();im.save(b,format='PNG');return b.getvalue()

def main():
    out=Path('research/hydrogen-smoke');out.mkdir(parents=True,exist_ok=True)
    img=chart();(out/'chart.png').write_bytes(img)
    cases=[
        ('definition','Quelle dimension décrit l’acceptation des inégalités de pouvoir ? A. Individualisme B. Distance hiérarchique C. Indulgence',1,[{'source':'synthetic-study-note','text':'La distance hiérarchique décrit dans quelle mesure les membres les moins puissants acceptent une répartition inégale du pouvoir.'}],None),
        ('negation','Selon cette note, quel comportement NE correspond PAS à un feedback négatif indirect ? A. Atténuer la critique B. Critiquer en privé C. Critiquer brutalement devant le groupe',2,[{'source':'synthetic-study-note','text':'Le feedback négatif indirect est privé, diplomatique et atténué. Une critique brutale devant le groupe relève du feedback négatif direct.'}],None),
        ('visual-bars','Sur le graphique fourni, quelle région a la barre la plus haute ? A. Nord B. Sud C. Est',1,[],img),
    ]
    rows=[]
    with (out/'results.jsonl').open('w') as f:
        for name,q,gold,evidence,image in cases:
            for model in ['gemini-3.8-flash','gemini-4-hydrogen']:
                t=time.monotonic();row={'model':model,'case':name,'gold':gold,'visual':image is not None}
                try:
                    result=answer(q,evidence,model=model,image=image)
                    row.update(result=result,correct=label(result['answer'])==gold)
                except Exception as e:row.update(error=type(e).__name__,correct=False)
                row['seconds']=time.monotonic()-t;rows.append(row)
                f.write(json.dumps(row,ensure_ascii=False)+'\n');f.flush()
                print(model,name,row['correct'],round(row['seconds'],2),flush=True)
    stats={m:{'correct':sum(r['correct'] for r in rows if r['model']==m),'total':sum(r['model']==m for r in rows),'median_seconds':statistics.median(r['seconds'] for r in rows if r['model']==m),'max_seconds':max(r['seconds'] for r in rows if r['model']==m)} for m in ['gemini-3.8-flash','gemini-4-hydrogen']}
    (out/'summary.json').write_text(json.dumps(stats,indent=2))
    (out/'REPORT.md').write_text('# Hydrogen smoke test\n\nThree synthetic cases per model: definition, negation, and reading the tallest bar from an image. Model API call latency only; excludes capture, OCR and retrieval. One run per case is insufficient to establish a robust accuracy or speed winner.\n\n'+json.dumps(stats,indent=2)+'\n')
if __name__=='__main__':main()
