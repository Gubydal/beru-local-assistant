# Additional source-anchored questions not used while tuning OCR/parser behavior.
DATA = [
    (
        "culture_learned",
        "La culture est principalement :",
        [
            "Acquise et transmise socialement",
            "Un programme exclusivement génétique",
            "Une propriété uniquement biologique",
        ],
        0,
        "DOC Support 2-1",
    ),
    (
        "tylor",
        "Quel auteur a publié Primitive Culture en 1871 ?",
        ["Edward Tylor", "Geert Hofstede", "Edgar Schein"],
        0,
        "DOC Support 2-2",
    ),
    (
        "thomas",
        "La méthode des standards culturels d’Alexander Thomas s’appuie notamment sur :",
        [
            "Des entretiens qualitatifs et des situations critiques",
            "Uniquement la génétique des populations",
            "La suppression de toute différence culturelle",
        ],
        0,
        "DOC Support 3-2",
    ),
    (
        "schein",
        "Le modèle de Schein distingue notamment :",
        [
            "Hypothèses fondamentales, valeurs et artefacts",
            "Uniquement les salaires et les contrats",
            "Les six dimensions nationales de Hofstede",
        ],
        0,
        "DOC Support 3-2",
    ),
    (
        "hall_space",
        "La proxémique étudiée par Edward Hall concerne :",
        [
            "L’usage culturel de l’espace et des distances",
            "Les seuls fuseaux horaires",
            "Les taux de change",
        ],
        0,
        "DOC Support 3-1",
    ),
    (
        "framework_counts",
        "Quel couple associe correctement deux modèles ?",
        [
            "Hofstede : six dimensions ; Trompenaars : sept dimensions",
            "Hofstede : sept dimensions ; Trompenaars : six dimensions",
            "Les deux modèles ont exactement deux dimensions",
        ],
        0,
        "DOC Support 3-2",
    ),
    (
        "values_practices",
        "Selon Schein, les valeurs et hypothèses d’une organisation peuvent contribuer à expliquer :",
        [
            "Les comportements et les artefacts observables",
            "Uniquement les statistiques démographiques nationales",
            "L’absence de toute culture organisationnelle",
        ],
        0,
        "DOC Support 3-2",
    ),
    (
        "org_adapts",
        "Selon la conception où l’organisation a une culture, celle-ci peut :",
        [
            "Évoluer avec les environnements interne et externe",
            "Être nécessairement immuable",
            "Ne concerner que les musées",
        ],
        0,
        "DOC Support 5-1",
    ),
    (
        "survey_scope",
        "Le document de l’enquête ENCGT indique une couverture proche de :",
        [
            "900 personnes sur trois années 2018 à 2020",
            "90 personnes pendant une semaine",
            "9 millions de personnes en 2024",
        ],
        0,
        "DOC_Résultats",
    ),
    (
        "survey_extract",
        "L’extrait d’exploitation présenté dans le document VSM13 concerne :",
        [
            "Le tiers de la population enquêtée, en 2018",
            "La totalité des habitants du Maroc",
            "Uniquement les élèves de 2026",
        ],
        0,
        "DOC_Résultats",
    ),
    (
        "altrad",
        "Dans le cas Altrad, ignorer la diversité des cultures est présenté comme :",
        [
            "Une absence de stratégie ou une forme d’aveuglement",
            "La meilleure stratégie recommandée",
            "Une obligation juridique universelle",
        ],
        0,
        "Altrad",
    ),
    (
        "globalization",
        "Quel changement favorise l’interdépendance internationale décrite dans le cours ?",
        [
            "La diminution des barrières commerciales",
            "La disparition de tous les échanges",
            "L’interdiction générale des investissements étrangers",
        ],
        0,
        "DOC Support 1-1",
    ),
    (
        "neutral_inner",
        "Une culture neutre signifie-t-elle que les personnes ne ressentent aucune émotion ?",
        [
            "Non ; il s’agit surtout de leur expression dans le cadre professionnel",
            "Oui, aucune personne n’y ressent d’émotion",
            "Oui, par définition biologique",
        ],
        0,
        "learnlight",
    ),
    (
        "human_levels",
        "Les trois niveaux de singularité de la programmation mentale distinguent :",
        [
            "Nature humaine, culture et personnalité",
            "Nationalité, salaire et taille",
            "Seulement la culture et le climat",
        ],
        0,
        "jWAJFqJLWSg",
    ),
    (
        "internal_external",
        "Chez Trompenaars, une orientation interne considère généralement que :",
        [
            "L’être humain peut contrôler son environnement dans une certaine mesure",
            "L’environnement ne peut jamais être influencé",
            "Les émotions doivent toujours être cachées",
        ],
        0,
        "learnlight",
    ),
    (
        "achievement",
        "Chez Trompenaars, le statut acquis est lié principalement :",
        [
            "Aux réalisations et performances",
            "Uniquement à la naissance et à l’origine",
            "À la distance géographique",
        ],
        0,
        "learnlight",
    ),
]


def cases():
    out = []
    for n, (id, stem, options, gold, source) in enumerate(DATA):
        # Rotate correct positions rather than putting all correct answers first.
        shift = n % len(options)
        ordered = options[shift:] + options[:shift]
        out.append(
            dict(
                id="heldout_" + id,
                stem=stem,
                options=ordered,
                gold=(gold - shift) % len(options),
                source=source,
                needle=None,
            )
        )
    return out
