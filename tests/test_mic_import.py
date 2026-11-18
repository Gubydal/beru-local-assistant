"""Private PDF fixtures remain local; reusable safety policy is tested without them."""
from pathlib import Path
import json
from unittest.mock import patch,Mock
import pytest
from beru.providers import answer
ROOT=Path(__file__).resolve().parents[1]


def test_answer_policy_distinguishes_originals_from_uncertain_annotations():
    response=Mock()
    response.json.return_value={'candidates':[{'content':{'parts':[{'text':json.dumps({'answer':'B. Low context','citations':[1],'uncertain':False})}]}}]}
    with patch.dict('os.environ',{'GEMINI_API_KEY':'test'}),patch('beru.providers.load_env'),patch('beru.providers.requests.post',return_value=response) as post:
        answer('Question',[{'source':'course','text':'Explicit messages are low context.'}])
        policy=post.call_args.kwargs['json']['systemInstruction']['parts'][0]['text']
        assert 'Prefer original course handouts over secondary compilations' in policy
        assert 'student annotation or uncertain answer key is not proof' in policy


def private_bank():
    p=ROOT/'research/mic-import/question-bank.json'
    if not p.exists():pytest.skip('Private source PDF import is not distributed')
    return json.loads(p.read_text())


def test_pdf_import_accounts_for_every_question_page_without_guessing_keys():
    data=private_bank()
    covered={q['page'] for q in data['questions']}|{p for q in data['pending'] for p in q['pages']}
    assert covered==set(range(1,27))
    assert len(data['questions'])==20
    assert 'student annotations' in data['annotation_provenance']
    assert {q['page'] for q in data['questions']}.isdisjoint({1,7,10,11,25,26})
    by_page={q['page']:q for q in data['questions']}
    for n in [18,23]:
        assert by_page[n]['gold']==1
        assert by_page[n]['observed_annotation']=='A'
        assert by_page[n]['validation_status']=='conflict_resolved_from_course'
    assert all(q['answer_source'] and q['explanation'] for q in data['questions'])


def test_reviewed_compilation_preserves_pages_and_explicit_corrections():
    private_bank()
    text=(ROOT/'knowledge/documents/MIC Complet.study_guide.md').read_text()
    import re
    assert [int(n) for n in re.findall(r'^## Page (\d+)$',text,re.M)]==list(range(1,53))
    assert 'Principles-first commence par développer la théorie' in text
    assert 'Applications-first commence par un fait' in text
    assert 'valeurs numériques exactes' in text
    qa=(ROOT/'knowledge/documents/Questions MIC.reviewed.md').read_text()
    assert '+212' not in qa and '766-413913' not in qa
    assert 'A (?)' not in qa
    assert '## Page 18 — réponse recoupée' in qa



def test_priority_table_has_all_eight_cells_and_every_item_in_practice():
    private_bank()
    cells=json.loads((ROOT/'research/mic-import/page41-cells.json').read_text())
    questions=json.loads((ROOT/'practice/questions-table41.json').read_text())
    assert len(cells)==8 and sum(len(c[3]) for c in cells)==37
    assert len(questions)==45
    singles=[q for q in questions if 'item' in q]
    assert {q['item'] for q in singles}=={item for c in cells for item in c[3]}
    lookup={q['item']:q['options'][q['gold']] for q in singles}
    assert lookup['Normes informelles']=='Normes et valeurs / Intérieur / Matériels'
    assert lookup['Code d’éthique']=='Normes et valeurs / Extérieur / Matériels'
    assert lookup['Logo']=='Artéfacts / Extérieur / Matériels'
    assert lookup['Image']=='Artéfacts / Extérieur / Immatériels'
    assert lookup['Flux d’information']=='Normes et valeurs / Intérieur / Immatériels'
    assert lookup['Langage utilisé']=='Artéfacts / Intérieur / Immatériels'
    table=(ROOT/'knowledge/documents/MIC Complet.study_guide.md').read_text()
    assert all(item in table for c in cells for item in c[3])
