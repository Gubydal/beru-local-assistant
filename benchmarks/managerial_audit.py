"""Source-checked managerial scenarios; gold fixed before live evaluation."""
import json
from pathlib import Path
from benchmarks.hard_audit import task
from benchmarks.hard_cases import cases as old_cases
DATA = [
('Un dirigeant japonais est hiérarchique. Quelle décision reste compatible avec le graphique du support ?', 'Une décision consensuelle', 'Une décision nécessairement autoritaire', 'Une décision toujours individuelle', 'Japan lies toward hierarchical leadership'),
('La France communique avec davantage de contexte que les États-Unis. Son feedback négatif est-il forcément plus indirect selon le support ?', 'Non, la France est plus proche du feedback négatif direct', 'Oui, les deux échelles sont identiques', 'Oui, toute communication implicite interdit les critiques franches', 'France is closer to direct negative feedback'),
('Un rapport développe une théorie avant de présenter les faits puis la conclusion. Quelle approche ?', 'Principles-first', 'Applications-first', 'Task-based trust', 'Principles-first develops theory'),
('Un rapport commence par des recommandations en puces puis ajoute les concepts nécessaires. Quelle approche ?', 'Applications-first', 'Principles-first', 'Hierarchical', 'executive summary or bullet points'),
('Quel comportement NE correspond PAS au feedback négatif indirect du support ?', 'Critiquer publiquement avec des qualificatifs absolus', 'Critiquer en privé', 'Adoucir la critique avec des messages positifs', 'indirect negative feedback is private'),
('Un chef agit en facilitateur parmi ses égaux et accepte de sauter les lignes hiérarchiques. Quel style ?', 'Egalitarian', 'Hierarchical', 'Top-down', 'facilitator among equals'),
('Les collaborateurs discutent mais le directeur décide seul. Selon la définition, la décision est :', 'Top-down', 'Consensual', 'Unanime', 'made by an individual'),
('Une équipe vote à la majorité malgré deux opposants. Est-ce une décision consensuelle au sens strict du support ?', 'Non, le support exige un accord unanime', 'Oui, toute majorité est unanime', 'Oui, toute réunion est consensuelle', 'unanimous group agreement'),
('Un partenaire gagne votre confiance grâce à sa fiabilité et son bon travail régulier. Quel mécanisme ?', 'Task-based trust', 'Relationship-based trust', 'Avoids confrontation', 'consistent good work and reliability'),
('La confiance se développe lentement grâce aux repas partagés et aux relations personnelles. Quel mécanisme ?', 'Relationship-based trust', 'Task-based trust', 'Linear-time', 'grows slowly through shared meals'),
('Un débat ouvert est jugé utile et compatible avec une bonne relation. Quelle orientation ?', 'Confrontational', 'Avoids confrontation', 'Indirect negative feedback nécessairement', 'open debate as positive'),
('Un manager accepte interruptions et tâches simultanées pour saisir les occasions. Quelle orientation temporelle ?', 'Flexible-time', 'Linear-time', 'Principles-first', 'accepts interruptions'),
]
def cases():
    out=[]
    for i,(stem,a,b,c,anchor) in enumerate(DATA):
        options=[a,b,c];shift=i%3;options=options[shift:]+options[:shift]
        out.append(dict(id=f'managerial-{i+1:02}',stem=stem,options=options,gold=options.index(a),source='DOC Support 6-1',anchor=anchor))
    return out
if __name__=='__main__':
    jobs=[(c,'question_only',1) for c in cases()]+[(c,'jpeg',2) for c in cases()[::2]]+[(c,'question_only',4) for c in old_cases()[::5]]
    with Path('research/hard-audit/managerial-results.jsonl').open('w') as f:
        for i,j in enumerate(jobs):
            r=task(j);f.write(json.dumps(r,ensure_ascii=False)+'\n');f.flush()
            print(i+1,len(jobs),r['id'],r['correct'],round(r['total_seconds'],2),flush=True)
