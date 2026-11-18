"""Live OCR/retrieval/answer check of six table-based practice scenarios."""
import json
from pathlib import Path
from benchmarks.hard_audit import task
if __name__=='__main__':
    rows=json.loads(Path('practice/questions-deep.json').read_text())[:6]
    with Path('research/hard-audit/coi-results.jsonl').open('w') as f:
        for row in rows:
            case=dict(row,anchor=row['needle'])
            result=task((case,'question_only',1))
            f.write(json.dumps(result,ensure_ascii=False)+'\n');f.flush()
            print(result['id'],result['correct'],round(result['total_seconds'],2),flush=True)
