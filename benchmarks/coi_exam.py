"""Ten-indicator COI exam validation. Frozen gold; screenshots; production Engine; no answer cache."""
import io,json,time,statistics
from pathlib import Path
from PIL import Image
from benchmarks.render import render
from benchmarks.run import label
from beru.engine import Engine

# One source-checked scenario per indicator. Gold fixed before any live call.
DATA=[
('environment','Selon le COI, choisir entre contrôler son environnement, rechercher l’harmonie ou subir les contraintes relève de quel indicateur ?','Environnement',['Structure','Action','Pouvoir']),
('time','Selon le COI, préférer une activité à la fois, un calendrier fixe et une orientation vers le futur relève de quel indicateur ?','Temps',['Action','Pensée','Structure']),
('action','Selon le COI, la préférence entre « être » et « faire » appartient à quel indicateur ?','Action',['Temps','Compétitivité','Pensée']),
('communication','Selon le COI, les préférences contexte implicite/explicite, expression directe/indirecte et style formel/informel appartiennent à :','Communication',['Individualisme','Pouvoir','Environnement']),
('space','Selon le COI, délimiter son espace physique et psychologique et préférer un espace public ou privé relève de :','Espace',['Environnement','Structure','Individualisme']),
('power','Selon le COI, préférer des relations hiérarchiques ou égalitaires correspond à quel indicateur ?','Pouvoir',['Structure','Compétitivité','Individualisme']),
('individualism','Selon le COI, définir son identité comme individuelle ou collective et considérer universalisme/particularisme relève de :','Individualisme',['Compétitivité','Environnement','Pouvoir']),
('competitiveness','Selon le COI, être motivé par la compétition plutôt que la coopération relève de quel indicateur ?','Compétitivité',['Individualisme','Action','Pouvoir']),
('structure','Selon le COI, aborder le changement, le risque, l’ambiguïté et l’incertitude, avec une préférence pour ordre ou flexibilité, relève de :','Structure',['Environnement','Temps','Pensée']),
('thinking','Selon le COI, les modes de raisonnement déductif/inductif et linéaire/systématique appartiennent à quel indicateur ?','Pensée',['Structure','Action','Communication']),
]

def cases():
    rows=[]
    for i,(id,stem,right,others) in enumerate(DATA):
        opts=[right]+others;shift=i%4;opts=opts[shift:]+opts[:shift]
        rows.append(dict(id=id,stem=stem,options=opts,gold=opts.index(right),indicator=right))
    return rows


def coi_evidence(e):
    return ('DOC Support 3-2' in e['source'] or 'MIC Complet.study_guide' in e['source']) and ('COI' in e['text'] or 'Cultural Orientations' in e['text'] or ('Page 35' in e['section']))


def main():
    out=Path('research/coi-exam')/time.strftime('%Y%m%d-%H%M%S');out.mkdir(parents=True)
    (out/'frozen-cases.json').write_text(json.dumps(cases(),ensure_ascii=False,indent=2))
    results=[];runs=[]
    with (out/'results.jsonl').open('w') as f:
        for model in ['gemini-3.8-flash','gemini-4-hydrogen']:
            for variant in ['clean','shuffled-selected-jpeg']:
                started=time.monotonic();batch=[]
                for c in cases():
                    c=dict(c)
                    if variant!='clean':c.update(options=list(reversed(c['options'])),gold=3-c['gold'])
                    im=render(c,'question_only' if variant=='clean' else 'selected_wrong')
                    if variant!='clean':
                        b=io.BytesIO();im.save(b,format='JPEG',quality=35);b.seek(0);im=Image.open(b).convert('RGB')
                    r=dict(model=model,variant=variant,id=c['id'],indicator=c['indicator'],gold=c['gold'])
                    t=time.monotonic()
                    try:
                        result=Engine().solve(im,model=model,use_cache=False)
                        cited=[result['evidence'][i-1] for i in result.get('citations',[])]
                        r.update(result=result,correct=label(result['answer'])==c['gold'],coi_retrieved=any(coi_evidence(e) for e in result['evidence']),coi_cited=any(coi_evidence(e) for e in cited))
                    except Exception as e:r.update(correct=False,error=type(e).__name__,message=str(e)[:200])
                    r['seconds']=time.monotonic()-t;results.append(r);batch.append(r)
                    f.write(json.dumps(r,ensure_ascii=False)+'\n');f.flush()
                    print(model,variant,c['id'],r['correct'],round(r['seconds'],2),flush=True)
                runs.append(dict(model=model,variant=variant,correct=sum(r['correct'] for r in batch),count=len(batch),wall_seconds=time.monotonic()-started))
    summary={}
    for model in ['gemini-3.8-flash','gemini-4-hydrogen']:
        rows=[r for r in results if r['model']==model];ts=sorted(r['seconds'] for r in rows)
        summary[model]=dict(correct=sum(r['correct'] for r in rows),attempted=len(rows),errors=sum('error' in r for r in rows),uncertain=sum(r.get('result',{}).get('uncertain',False) for r in rows),coi_retrieved=sum(r.get('coi_retrieved',False) for r in rows),coi_cited=sum(r.get('coi_cited',False) for r in rows),median_seconds=statistics.median(ts),p95_seconds=ts[min(len(ts)-1,int(.95*len(ts)))],max_seconds=max(ts),over_15=sum(t>15 for t in ts),over_18=sum(t>18 for t in ts))
    payload=dict(models=summary,runs=runs,design='10 unique source-derived COI indicator questions, two screenshot variants per model. Gold fixed before calls; no answer cache. This is a purposive regression test, not unseen exam accuracy. Query-embedding caches may be warm on later runs, and models run sequentially, so timing comparisons are descriptive rather than controlled. Timings exclude human reading/selection/navigation and native screen capture.')
    (out/'summary.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2))
    lines=['# COI exam-format validation','',payload['design'],'','| Model | Correct | COI cited | Median | Max | >18s |','|---|---:|---:|---:|---:|---:|']
    for m,s in summary.items():lines.append(f"| {m} | {s['correct']}/{s['attempted']} | {s['coi_cited']}/{s['attempted']} | {s['median_seconds']:.2f}s | {s['max_seconds']:.2f}s | {s['over_18']} |")
    lines+=['','## Ten-question run durations','']
    for r in runs:lines.append(f"- {r['model']} / {r['variant']}: {r['correct']}/10, {r['wall_seconds']:.2f}s of a 180-second budget (automation only).")
    lines+=['','Coverage: environment, time, action, communication, space, power, individualism, competitiveness, structure and thinking. The second variant reverses all option orders, selects an incorrect radio button and applies JPEG compression. Text-only OCR/retrieval answering; no screenshot sent to model. Passing this set cannot guarantee real-exam answers or network availability.']
    (out/'REPORT.md').write_text('\n'.join(lines)+'\n');Path('research/coi-exam/LATEST').write_text(str(out)+'\n')
    print(json.dumps(payload,indent=2),flush=True)
if __name__=='__main__':main()
