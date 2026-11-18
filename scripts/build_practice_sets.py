"""Build two source-anchored practice tests; keep generated questions outside RAG."""
import json
from pathlib import Path
from benchmarks.hard_cases import cases as hard_cases
from benchmarks.managerial_audit import cases as managerial_cases
ROOT=Path(__file__).resolve().parents[1]
COI='DOC Support 3-2'
PHOTO='''

## COI — tableau des compétences, transcription de la photo fournie par l’utilisateur

Provenance : photographie de la diapositive « Ch. 3 - Various approaches of the culture (Society, Organization) », « The Main Models », « h. The Cultural Orientations Indicator (COI) », Management interculturel, Prof. Omar Belkheiri, ENCG Tanger, semestre 7. Tableau lu visuellement dans la photo fournie ; ces définitions ne sont pas attribuées à une page du PDF.

| Compétence | Traduction | Opérationnalisation |
|---|---|---|
| Cultural Due Diligence | Diagnostic culturel préalable | Identifier et évaluer les différences culturelles susceptibles d’influencer une interaction professionnelle afin d’anticiper leurs conséquences. |
| Style Switching | Adaptabilité comportementale interculturelle | Savoir modifier son style de communication, de management ou de comportement en fonction des exigences culturelles de la situation. |
| Cultural Dialogue | Dialogue interculturel | Engager un échange explicite sur les différences culturelles afin de mieux les comprendre, de résoudre les malentendus et de construire des solutions communes. |
| Cultural Mentoring | Accompagnement interculturel | Aider les autres à prendre conscience des différences culturelles et à développer leur capacité à évoluer dans des environnements multiculturels. |

Distinction de lecture du tableau : diagnostiquer et anticiper = due diligence ; adapter son propre style = style switching ; échanger explicitement et construire ensemble = dialogue ; accompagner le développement d’autrui = mentoring. Plusieurs compétences peuvent intervenir dans un même cas ; choisir l’action décrite par la question.
'''
p=ROOT/'knowledge/documents/DOC Support 3-2.md'
if 'transcription de la photo fournie' not in p.read_text(): p.write_text(p.read_text()+PHOTO)
# stem, right, distractor1, distractor2, source, evidence anchor
EASY=[
('Quelle compétence COI désigne le diagnostic culturel préalable ?', 'Cultural Due Diligence','Style Switching','Cultural Mentoring',COI,'Identifier et évaluer'),
('Modifier son propre style de communication selon la situation culturelle correspond à :','Style Switching','Cultural Dialogue','Cultural Due Diligence',COI,'Savoir modifier son style'),
('Engager un échange explicite pour résoudre les malentendus correspond à :','Cultural Dialogue','Cultural Mentoring','Style Switching',COI,'Engager un échange explicite'),
('Aider les autres à développer leurs capacités interculturelles correspond à :','Cultural Mentoring','Cultural Due Diligence','Style Switching',COI,'Aider les autres'),
('Dans le support, combien de dimensions le COI synthétise-t-il ?', 'Dix','Six','Sept',COI,'10 dimensional model'),
('La culture Clan de Cameron et Quinn combine :','Orientation interne et flexibilité','Orientation externe et stabilité','Orientation interne et stabilité','DOC Support 5-1','internal focus and integration + flexibility'),
('La culture Adhocracy de Cameron et Quinn privilégie :','Innovation et créativité','Règles fixes et contrôle uniquement','Stabilité interne avant tout','DOC Support 5-1','innovation'),
('La culture Hierarchy de Cameron et Quinn combine :','Orientation interne et stabilité/contrôle','Orientation externe et flexibilité','Orientation externe et stabilité','DOC Support 5-1','Hierarchy culture'),
('La culture Market de Cameron et Quinn combine :','Orientation externe et stabilité/contrôle','Orientation interne et flexibilité','Orientation interne et stabilité','DOC Support 5-1','Market culture'),
('Dans le support organisationnel, Family, Eiffel Tower, Guided Missile et Incubator relèvent de :','Trompenaars','Cameron et Quinn','Hofstede','DOC Support 5-1','Trompenaars'),
('Une communication low-context transmet surtout des messages :','Explicites, précis et clairs','Toujours sous-entendus','Uniquement non verbaux','DOC Support 6-1','precise, simple, and clear'),
('La communication high-context fait notamment appel à :','La lecture entre les lignes','La suppression de tout contexte','La répétition littérale obligatoire','DOC Support 6-1','read between the lines'),
('Un feedback négatif indirect est donné :','En privé, avec atténuations','Toujours publiquement et brutalement','Sans aucune formule positive','DOC Support 6-1','Criticism is given only in private'),
('Une décision consensuelle, selon le support, repose sur :','Un accord unanime du groupe','Le seul choix du chef','Un tirage au sort','DOC Support 6-1','unanimous agreement'),
('La confiance task-based s’appuie surtout sur :','Le travail fiable et régulier','Les repas partagés uniquement','Le statut familial uniquement','DOC Support 6-1','good work consistently'),
('La confiance relationship-based se construit notamment par :','Du temps personnel partagé et des relations durables','La seule ponctualité technique','Une décision individuelle du chef','DOC Support 6-1','sharing meals'),
('Le linear-time privilégie :','Une tâche après l’autre et le respect du calendrier','Les interruptions et tâches simultanées','L’abandon de toute échéance','DOC Support 6-1','One thing at a time'),
('Le flexible-time accepte davantage :','Les interruptions et plusieurs tâches à la fois','Une séquence rigide sans interruption','La priorité absolue du calendrier','DOC Support 6-1','interruptions accepted'),
('La formation du cas yéménite portait sur :','Le contrôle du budget et des coûts','La conception de logiciels','La publicité numérique','DOC Support 6-2','contrôle du budget et des coûts'),
('Quelle était la durée prévue de la formation au Yémen ?', 'Deux semaines','Deux jours','Six mois','DOC Support 6-2','deux semaines'),
('Quelle adaptation Fanny propose-t-elle ?', 'Poser elle-même les questions pendant que le consultant enseigne','Supprimer les exercices','Interdire les pauses de prière','DOC Support 6-2','Ce serait elle qui poserait les questions'),
('Après cette adaptation, le cas rapporte :','Une mise en pratique de l’enseignement et un succès','L’arrêt immédiat de la formation','L’exclusion de tous les participants','DOC Support 6-2','Le cours est devenu un succès'),
('Dans le témoignage vidéo marocain, quelle difficulté revient régulièrement ?', 'Le dépassement des délais','Un excès systématique de livraisons en avance','Une absence de clients étrangers','9QdyxU7tseo','les délais sont'),
('Quelle expression le témoin emploie-t-il pour décrire le besoin de suivi ?', 'Autonomie assistée','Autonomie sans aucun suivi','Suppression de toute autonomie','9QdyxU7tseo','autonomie assistée'),
]

def make(rows,prefix):
    out=[]
    for i,(stem,a,b,c,source,anchor) in enumerate(rows):
        opts=[a,b,c];shift=i%3;opts=opts[shift:]+opts[:shift]
        out.append(dict(id=f'{prefix}-{i+1:02}',stem=stem,options=opts,gold=opts.index(a),source=source,needle=anchor,explanation=f'Le passage de référence indique : « {anchor} ». La réponse attendue est : {a}.'))
    return out
coi_hard=[
('Avant une négociation, une responsable identifie les différences culturelles et évalue leurs conséquences possibles. Quelle compétence domine ?', 'Cultural Due Diligence','Cultural Mentoring','Style Switching',COI,'afin d’anticiper leurs conséquences'),
('Après un diagnostic, un responsable change sa manière de donner du feedback. Quelle action relève précisément du Style Switching ?', 'Modifier son propre comportement','Évaluer les différences avant la rencontre','Former un collègue à l’interculturel',COI,'Savoir modifier son style'),
('Deux équipes exposent explicitement leurs attentes différentes et élaborent une solution commune. Quelle compétence domine ?', 'Cultural Dialogue','Cultural Due Diligence','Cultural Mentoring',COI,'construire des solutions communes'),
('Une tutrice accompagne progressivement un collègue pour qu’il développe ses capacités en milieu multiculturel. Quelle compétence domine ?', 'Cultural Mentoring','Style Switching','Cultural Due Diligence',COI,'développer leur capacité'),
('Quelle proposition NE décrit PAS le diagnostic culturel préalable du tableau COI ?', 'Changer son style sans identifier ni évaluer les différences','Anticiper les conséquences culturelles','Évaluer les différences affectant une interaction professionnelle',COI,'Identifier et évaluer'),
('Quel enchaînement associe correctement les actions et compétences COI ?', 'Anticiper : due diligence ; adapter son style : switching ; échanger : dialogue ; accompagner autrui : mentoring','Anticiper : mentoring ; adapter son style : dialogue ; échanger : switching ; accompagner : due diligence','Les quatre compétences signifient seulement changer son comportement',COI,'diagnostiquer et anticiper'),
]
easy=make(EASY,'fundamentals')
hard=make(coi_hard,'coi-deep')
# Existing source-checked difficult questions, all four priority resources represented.
priority={'DOC Support 5-1','DOC Support 6-2','9QdyxU7tseo'}
for source,count in [('DOC Support 5-1',6),('DOC Support 6-2',4),('9QdyxU7tseo',4)]:
    for q in [q for q in hard_cases() if q['source']==source][:count]:
        q=dict(q);q['needle']=q.pop('anchor');q['explanation']='Élément de référence : « '+q['needle']+' ». '+q['options'][q['gold']];hard.append(q)
for q in managerial_cases()[:8]:
    q=dict(q);q['needle']=q.pop('anchor');q['explanation']='Élément de référence : « '+q['needle']+' ». '+q['options'][q['gold']];hard.append(q)
for filename,data in [('questions-fundamentals.json',easy),('questions-deep.json',hard)]:
    (ROOT/'practice'/filename).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(f'Added tests: {len(easy)} fundamentals, {len(hard)} deep scenarios')
