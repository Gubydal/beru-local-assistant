"""Reconstructed photograph wording; no official answer key, therefore unscored."""

import json, pathlib, time
from benchmarks.hard_audit import task
from beru import semantic

PROBES = [
    dict(
        id="photo_hofstede_comparison",
        stem="Le modèle de G. Hofstede permet de comparer :",
        options=[
            "...Les sociétés entre elles sur une même période",
            "...Une société à elle-même sur plusieurs périodes",
            "...Les deux",
        ],
        gold=None,
        source="DOC Support 3-2",
        anchor="national cultures",
    ),
    dict(
        id="photo_school_mental_map",
        stem="En relation avec le modèle de programmation mentale de G. Hofstede, l’Éducation scolaire fait partie de la « Carte du Monde » qui permet à chaque individu de percevoir le monde",
        options=["OUI", "NON"],
        gold=None,
        source="jWAJFqJLWSg",
        anchor="learned",
    ),
    dict(
        id="photo_implicit_rules",
        stem="Dans une société, lorsque le respect des règles est chose naturelle et ne nécessite pas automatiquement de mettre des moyens de contrainte, alors on est en situation culturelle de :",
        options=["...LOW CONTEXT", "...HIGH CONTEXT"],
        gold=None,
        source="DOC Support 3-2",
        anchor="Implicit context",
    ),
]
def main():
    semantic.start()
    until = time.monotonic() + 20
    while not semantic._instance.ready and time.monotonic() < until:
        time.sleep(0.05)
    with pathlib.Path("research/hard-audit/photo-probes.jsonl").open("w") as f:
        for c in PROBES:
            for variant in ["question_only", "jpeg"]:
                r = task((c, variant, 1))
                r.pop("correct", None)
                r["scored"] = False
                r["reason"] = (
                    "No instructor answer key; selected radio button is not ground truth."
                )
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                f.flush()
                print(
                    c["id"],
                    variant,
                    r.get("result", {}).get("answer"),
                    r.get("error"),
                    flush=True,
                )
    semantic.stop()

if __name__=="__main__":main()
