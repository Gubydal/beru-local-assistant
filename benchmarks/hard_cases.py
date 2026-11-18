"""Frozen source-anchored hard cases. Gold is not inferred from selected radio buttons."""

ORG = "DOC Support 5-1"
YEMEN = "DOC Support 6-2"
MOROCCO = "9QdyxU7tseo"
MODELS = "DOC Support 3-2"
# id, question, choices (first is correct before deterministic rotation), source, evidence anchor
DATA = [
    (
        "yemen_role",
        "Dans le cas de formation au Yémen, quel changement de rôle a permis de surmonter la difficulté sans exclure Fanny ?",
        [
            "Le consultant enseigne et Fanny pose les questions à la place des participants",
            "Fanny quitte définitivement toute la formation",
            "Les participants doivent abandonner leurs prières",
            "Le consultant supprime les exercices pratiques",
        ],
        YEMEN,
        "Ce serait elle qui poserait les questions",
    ),
    (
        "yemen_apparent",
        "Les participants au Yémen semblent attentifs mais appliquent peu les exercices. Quelle lecture est appuyée par le cas ?",
        [
            "Explorer les valeurs, la fierté et les obstacles à avouer une incompréhension",
            "Conclure que leur attention prouve une compréhension complète",
            "Attribuer une incapacité intellectuelle à toute une population",
            "Conclure que le budget ne peut jamais être enseigné au Yémen",
        ],
        YEMEN,
        "révéler ce qu’ils ne savaient pas",
    ),
    (
        "yemen_value",
        "Dans le récit, pourquoi multiplier les rappels à la rentabilité ne suffisait-il pas à résoudre le problème ?",
        [
            "Les priorités attribuées à la prière et à la fierté différaient de celles des formateurs",
            "Les participants jugeaient tous la rentabilité plus importante que la prière",
            "Le document prouve une absence de toute hiérarchie de valeurs",
            "Les pauses étaient décrites comme un simple problème informatique",
        ],
        YEMEN,
        "Leur rang de valeurs",
    ),
    (
        "yemen_hypothesis",
        "Quel élément doit rester une hypothèse d’interprétation du cas plutôt qu’une loi générale ?",
        [
            "La difficulté possible d’avouer une incompréhension devant une jeune Européenne",
            "La durée prévue de deux semaines",
            "La présence de Fanny au stage",
            "L’intitulé contrôle du budget et des coûts",
        ],
        YEMEN,
        "Peut-être",
    ),
    (
        "yemen_reframe",
        "Le moment de recul des formateurs correspond surtout à :",
        [
            "Se détendre puis discuter sans stress des difficultés culturelles",
            "Renforcer immédiatement la contrainte pendant la prière",
            "Prouver que tous les participants ont tort par nature",
            "Supprimer tout questionnement sur leurs propres attentes",
        ],
        YEMEN,
        "conversation sans stress",
    ),
    (
        "yemen_success",
        "Quel résultat concret indique le succès de l’adaptation au Yémen ?",
        [
            "Ce qui est enseigné est ensuite mis en pratique",
            "La disparition annoncée de toute différence culturelle",
            "Le remplacement intégral des participants",
            "La fin de toute participation de Fanny",
        ],
        YEMEN,
        "mis en pratique",
    ),
    (
        "yemen_no_blame",
        "Quelle conclusion ne découle PAS du cas du Yémen ?",
        [
            "Tous les hommes d’une société refusent nécessairement d’apprendre auprès d’une femme",
            "Une adaptation des rôles peut faciliter les questions",
            "Une incompréhension peut rester masquée par une attitude attentive",
            "Des priorités de valeurs peuvent différer",
        ],
        YEMEN,
        "Peut-être",
    ),
    (
        "yemen_duration",
        "Quelle combinaison est conforme au contexte exact de la formation au Yémen ?",
        [
            "Deux semaines, contrôle du budget et des coûts",
            "Deux mois, marketing numérique",
            "Deux jours, négociation commerciale",
            "Deux ans, programmation informatique",
        ],
        YEMEN,
        "deux semaines",
    ),
    (
        "family_vs_tower",
        "Une entreprise centralisée autour d’un dirigeant, personnalisée et peu bureaucratique correspond selon Trompenaars à :",
        ["Family", "Eiffel Tower", "Guided Missile", "Incubator"],
        ORG,
        "No many rules",
    ),
    (
        "tower_vs_family",
        "Une entreprise très centralisée où l’autorité vient surtout de la fonction et des procédures correspond à :",
        ["Eiffel Tower", "Family", "Guided Missile", "Incubator"],
        ORG,
        "functional position",
    ),
    (
        "missile_vs_incubator",
        "Deux organisations sont décentralisées. Celle qui est formalisée, orientée projet et résultats correspond à :",
        ["Guided Missile", "Incubator", "Family", "Eiffel Tower"],
        ORG,
        "High degree of formalization",
    ),
    (
        "incubator_person",
        "Une structure peu centralisée et peu formalisée attribue les tâches selon les préférences des membres. C’est :",
        ["Incubator", "Guided Missile", "Eiffel Tower", "Family"],
        ORG,
        "member’s preferences",
    ),
    (
        "family_axis",
        "Quelle combinaison appartient à la culture Family dans ce support ?",
        [
            "Centralisation élevée et formalisation faible",
            "Centralisation faible et formalisation élevée",
            "Centralisation et formalisation élevées",
            "Centralisation et formalisation faibles",
        ],
        ORG,
        "Low degree of formalization",
    ),
    (
        "org_not_country",
        "Quelle distinction évite une confusion de niveau d’analyse ?",
        [
            "Les quatre types Family/Tower/Missile/Incubator décrivent des cultures organisationnelles",
            "Les quatre types sont quatre scores nationaux de Hofstede",
            "Les types sont des diagnostics médicaux individuels",
            "Family est le nom de la sixième dimension de Hofstede",
        ],
        ORG,
        "organizational cultures",
    ),
    (
        "clan",
        "Chez Cameron–Quinn, un facilitateur favorisant participation, communication et développement, avec flexibilité et focus interne, relève de :",
        ["Clan", "Adhocracy", "Market", "Hierarchy"],
        ORG,
        "Clan culture",
    ),
    (
        "adhocracy",
        "Quel quadrant combine flexibilité et focalisation externe chez Cameron–Quinn ?",
        ["Adhocracy", "Clan", "Hierarchy", "Market"],
        ORG,
        "external focus and differentiation + flexibility",
    ),
    (
        "hierarchy",
        "Un coordinateur recherche stabilité, cohérence, efficacité et focus interne. Quel type Cameron–Quinn convient ?",
        ["Hierarchy", "Market", "Clan", "Adhocracy"],
        ORG,
        "coordinator",
    ),
    (
        "market",
        "Une culture tournée vers l’extérieur mais attachée à la stabilité, aux objectifs et à la part de marché correspond à :",
        ["Market", "Adhocracy", "Clan", "Hierarchy"],
        ORG,
        "market share",
    ),
    (
        "distinct_axes",
        "Quelle paire d’axes appartient à Cameron–Quinn et non aux axes du modèle organisationnel de Trompenaars ?",
        [
            "Flexibilité/stabilité et focus interne/externe",
            "Centralisation/formalisation uniquement",
            "Individualisme/distance hiérarchique",
            "Masculinité/indulgence",
        ],
        ORG,
        "vertical axis",
    ),
    (
        "rituals",
        "Selon le tableau des composants du support, les histoires, mythes et rituels sont :",
        [
            "Des artefacts internes immatériels",
            "Des normes externes matérielles",
            "Des artefacts externes matériels",
            "Exclusivement des structures juridiques",
        ],
        ORG,
        "stories and myths",
    ),
    (
        "csr",
        "Dans le tableau précis de la page 3, code d’éthique, développement durable et RSE sont classés parmi :",
        [
            "Normes et valeurs : facteurs externes matériels",
            "Artefacts : facteurs internes immatériels",
            "Artefacts : facteurs externes immatériels",
            "Normes et valeurs : facteurs internes matériels",
        ],
        ORG,
        "corporate social responsibility",
    ),
    (
        "information_flows",
        "Selon ce même tableau, style de management et flux d’information relèvent de :",
        [
            "Normes et valeurs internes immatérielles",
            "Artefacts externes matériels",
            "Normes et valeurs externes matérielles",
            "Artefacts internes matériels",
        ],
        ORG,
        "information flows",
    ),
    (
        "ouchi_z",
        "Le tableau d’Ouchi associe contrôle clanique, emploi long, responsabilité individuelle et décision de groupe à :",
        ["Type Z", "Type J", "Type A", "Culture Process"],
        ORG,
        "Type Z",
    ),
    (
        "deal_feedback",
        "Dans l’annexe Deal–Kennedy, le risque très élevé et le retour lent caractérisent :",
        [
            "Bet-your-company",
            "Tough-guy / Macho",
            "Work-hard / Play-hard",
            "Clan de Cameron–Quinn",
        ],
        ORG,
        "very high risk",
    ),
    (
        "handy_role",
        "Quel rapprochement est correct dans l’annexe de Handy ?",
        [
            "Role — Apollo — règles, stabilité et prévisibilité",
            "Task — Zeus — responsabilité génétique",
            "Existential — Apollo — bureaucratie stricte",
            "Club — Dionysus — règles impersonnelles",
        ],
        ORG,
        "Role (Apollo)",
    ),
    (
        "is_has",
        "Quelle opposition est explicitement présentée au début du support Organizational Culture ?",
        [
            "Une culture que l’organisation est versus une culture qu’elle a et peut faire évoluer",
            "Une culture uniquement biologique versus uniquement climatique",
            "Une culture nationale versus une absence totale de culture dans les entreprises",
            "Une culture exclusivement matérielle versus exclusivement juridique",
        ],
        ORG,
        "Culture is something",
    ),
    (
        "performance",
        "À marchés et ressources comparables, le support souligne notamment l’effet de la culture sur :",
        [
            "La performance et la viabilité à long terme ainsi que le moral et l’engagement",
            "La garantie absolue de profits identiques pour toutes les entreprises",
            "L’impossibilité de toute incertitude",
            "La disparition mécanique des différences nationales",
        ],
        ORG,
        "long-term viability",
    ),
    (
        "morocco_chain",
        "Dans le témoignage marocain, comment des retards successifs peuvent-ils être entretenus ?",
        [
            "Par des arrangements tolérant les reports entre partenaires habituels",
            "Par une règle prouvant que tout retard est biologiquement nécessaire",
            "Par l’absence de tout client national",
            "Par une ponctualité parfaite explicitement décrite",
        ],
        MOROCCO,
        "chaîne",
    ),
    (
        "morocco_multinational",
        "Pourquoi l’arrivée d’un client multinational rend-elle le décalage temporel plus problématique dans ce récit ?",
        [
            "Ses attentes de respect des délais et de qualité entrent en tension avec les reports habituels",
            "Le client affirme que les délais n’ont jamais aucune importance",
            "Le client interdit tout produit fini",
            "Le récit explique que la multinationale supprime toute exigence de qualité",
        ],
        MOROCCO,
        "respect des",
    ),
    (
        "morocco_adaptation",
        "Quel changement le témoin dit-il devoir opérer ?",
        [
            "Adapter son propre schéma cognitif et son management aux pratiques rencontrées",
            "Démontrer que sa première lecture de la situation ne doit jamais être révisée",
            "Supprimer toute relation de confiance",
            "Établir un diagnostic valable pour chaque Marocain sans exception",
        ],
        MOROCCO,
        "schéma",
    ),
    (
        "morocco_assisted",
        "Que désigne l’expression autonomie assistée dans le témoignage ?",
        [
            "Une autonomie accompagnée d’un suivi régulier du travail et des délais",
            "L’absence complète de suivi du travail",
            "L’obligation juridique de ne jamais déléguer",
            "L’incapacité innée de tous les employés du pays",
        ],
        MOROCCO,
        "autonomie assistée",
    ),
    (
        "morocco_yes",
        "Dans ce récit, le fait qu’un employé dise oui à une directive garantit-il son exécution ?",
        [
            "Non, le témoin décrit précisément un décalage possible entre accord verbal et réalisation",
            "Oui, le oui est présenté comme une preuve universelle d’exécution",
            "Oui, car la vidéo établit une loi statistique nationale",
            "La vidéo ne parle jamais de directives",
        ],
        MOROCCO,
        "oui ça veut dire non",
    ),
    (
        "morocco_scope",
        "Quelle portée donner aux affirmations générales du témoin sur les entreprises marocaines ?",
        [
            "Les situer comme un témoignage contextualisé, sans les transformer en loi sur tous les individus",
            "Les traiter comme un recensement représentatif de toutes les entreprises",
            "Les appliquer sans exception à chaque travailleur marocain",
            "Les considérer comme une mesure génétique de la productivité",
        ],
        MOROCCO,
        "l’entreprise où je travaille",
    ),
    (
        "high_context",
        "Dans la matrice de Hall du support, lire entre les lignes et décoder un message culturellement implicite relève de :",
        ["High context", "Low context", "Guided Missile", "Market"],
        MODELS,
        "read between the lines",
    ),
    (
        "low_context",
        "Quelle formulation correspond au low context dans la matrice du cours ?",
        [
            "Messages verbaux explicites, allant droit au but",
            "Message nécessairement caché dans tous les gestes",
            "Absence de toute communication verbale",
            "Centralisation et formalisation élevées",
        ],
        MODELS,
        "straight to the point",
    ),
    (
        "mono_poly",
        "Quelle combinaison est polychrone dans la matrice de Hall ?",
        [
            "Plusieurs activités à la fois, priorité aux relations, échéances non vitales",
            "Une seule tâche à la fois avec forte priorité à l’horaire",
            "Une absence de relations avec les proches",
            "Une définition des cultures par leur PIB",
        ],
        MODELS,
        "deadlines are not vital",
    ),
    (
        "space",
        "Dans la colonne espace de la matrice de Hall, une territorialité élevée est associée à :",
        [
            "Une bulle d’espace plus grande",
            "Une absence nécessaire de toute frontière nationale",
            "Une hiérarchie professionnelle élevée par définition",
            "Un besoin d’espace personnel toujours nul",
        ],
        MODELS,
        "higher territoriality",
    ),
    (
        "axes_independent",
        "La matrice de Hall place temps, contexte et espace en colonnes. Quelle conclusion est la plus prudente ?",
        [
            "Distinguer les trois dimensions plutôt que déduire automatiquement toutes les caractéristiques d’un individu d’une seule case",
            "Déduire sans exception la ponctualité de la seule nationalité",
            "Assimiler high context et forte distance hiérarchique comme deux synonymes",
            "Assimiler monochronie et culture Market comme un seul concept",
        ],
        MODELS,
        "separate dimensions",
    ),
    (
        "hofstede_history",
        "Quel énoncé respecte l’évolution du modèle de Hofstede telle que décrite dans le support ?",
        [
            "Quatre dimensions initiales, puis deux dimensions ajoutées",
            "Six dimensions déjà toutes présentes dans le modèle initial",
            "Sept dimensions identiques à Trompenaars dès l’origine",
            "Le modèle a toujours été limité à deux dimensions",
        ],
        MODELS,
        "04 key dimensions",
    ),
    (
        "learned_not_genetic",
        "Dans la programmation mentale de Hofstede, l’apprentissage culturel se distingue de la nature humaine car :",
        [
            "La culture est apprise et partagée par un groupe, la nature humaine est universelle et héritée",
            "La culture est exclusivement héritée génétiquement",
            "La personnalité est intégralement identique pour une nation entière",
            "Les trois niveaux sont interchangeables",
        ],
        "jWAJFqJLWSg",
        "culture is not inherited",
    ),
]


def cases():
    out = []
    for i, (id, stem, options, source, anchor) in enumerate(DATA):
        shift = (i * 3 + 1) % len(options)
        choices = options[shift:] + options[:shift]
        out.append(
            dict(
                id=id,
                stem=stem,
                options=choices,
                gold=(-shift) % len(options),
                source=source,
                anchor=anchor,
                needle=anchor,
            )
        )
    return out
