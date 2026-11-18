from unittest.mock import patch,Mock
import json
import pytest
from PIL import Image
from beru.question import parse_written,from_text
from beru.engine import Engine
from beru.providers import answer,read_image


def test_written_extraction_keeps_prompt_and_rejects_unreadable():
    q=parse_written([{'text':'Question 4'},{'text':'Définissez l’indicateur Action du COI en une phrase.','confidence':.9,'box':[.1,.2,.7,.1]},{'text':'Réponse :'}])
    assert q.options=={} and q.text=='Définissez l’indicateur Action du COI en une phrase.' and q.box
    with pytest.raises(ValueError):parse_written([{'text':'Définissez le COI.','confidence':.1}])
    with pytest.raises(ValueError):from_text(q.text)


def test_written_answer_and_mcq_use_separate_cache_entries():
    engine=Engine();im=Image.new('RGB',(50,50));q=parse_written([{'text':'Définissez l’indicateur Action du COI.'}])
    mcq=from_text('Définissez l’indicateur Action du COI.\na. Être ou faire\nb. Espace')
    with patch('beru.engine.read',side_effect=[q,mcq,q]),patch('beru.engine.search',return_value=[]) as search,patch('beru.engine.answer',side_effect=[{'answer':'Action concerne être ou faire.'},{'answer':'a. Être ou faire'}]) as provider:
        written=engine.solve(im,mode='written',topic='coi')
        assert written['answer']=='Action concerne être ou faire.'
        assert provider.call_args.kwargs['mode']=='written'
        assert search.call_args.args[0].startswith('COI Cultural Orientations Indicator:')
        assert engine.solve(im)['question_mode']=='mcq'
        assert engine.solve(im,mode='written',topic='coi')['cached']
        assert provider.call_count==2


def test_written_policy_requests_plain_language_and_validates_citations():
    response=Mock();response.json.return_value={'candidates':[{'content':{'parts':[{'text':json.dumps({'answer':'Le COI comporte dix indicateurs.','citations':[1],'uncertain':False})}]}}]}
    with patch.dict('os.environ',{'GEMINI_API_KEY':'test'}),patch('beru.providers.load_env'),patch('beru.providers.requests.post',return_value=response) as post:
        result=answer('Combien d’indicateurs ?', [{'text':'Dix'}],mode='written')
        assert result['answer']=='Le COI comporte dix indicateurs.'
        assert 'written-response question' in post.call_args.kwargs['json']['systemInstruction']['parts'][0]['text']


def test_visual_written_recovery_requires_complete_prompt():
    response=Mock();response.json.return_value={'candidates':[{'content':{'parts':[{'text':json.dumps({'stem':'Décrivez les dix indicateurs du COI.','complete':False})}]}}]}
    with patch.dict('os.environ',{'GEMINI_API_KEY':'test'}),patch('beru.providers.load_env'),patch('beru.providers.requests.post',return_value=response):
        with pytest.raises(ValueError):read_image(b'png',mode='written')


def test_written_ui_copy_excludes_evidence_and_uncertainty_label(qtbot):
    from beru.app import App
    from PySide6.QtWidgets import QApplication
    w=App();w.timer.stop();qtbot.addWidget(w)
    w.question_type.setCurrentIndex(1)
    assert w.question_type.currentData()=='written' and w.coi_focus.isChecked()
    w.result={'answer':'Action : être ou faire.','uncertain':True,'explanation':'Source explanation','citations':[],'evidence':[]}
    w.render();w.copy_button.click()
    assert QApplication.clipboard().text()=='Action : être ou faire.'
    w.question_type.setCurrentIndex(0)
    assert w.result is None and not w.copy_button.isEnabled()
