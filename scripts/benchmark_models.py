import sys, json, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from beru.providers import load_env, answer
from beru.knowledge import search

load_env()
questions = [
    "Quelle dimension de Hofstede mesure l’acceptation des inégalités de pouvoir ? A. Distance hiérarchique B. Individualisme C. Indulgence D. Orientation temporelle",
    "In Hall’s framework, which communication style relies heavily on shared context? A. Low context B. High context C. Universalism D. Neutrality",
]
results = []
for provider, key, models in [
    (
        "gemini",
        "GEMINI_API_KEY",
        ["gemini-3.8-flash", "gemini-4-hydrogen", "gemini-3.5-flash-lite", "gemini-4-argon"],
    ),
    ("deepseek", "DEEPSEEK_API_KEY", ["deepseek-flash"]),
]:
    if not (os.getenv(key) or (provider == "gemini" and os.getenv("GOOGLE_API_KEY"))):
        print("Skipped", provider, ": missing API key")
        continue
    for model in models:
        for q in questions:
            try:
                results.append(
                    {
                        "provider": provider,
                        "model": model,
                        "question": q,
                        "result": answer(q, search(q), provider, model),
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "provider": provider,
                        "model": model,
                        "error_type": type(e).__name__,
                    }
                )
Path("research/model-benchmark.json").write_text(
    json.dumps(results, ensure_ascii=False, indent=2)
)
print(
    "Completed",
    len(results),
    "requests. These two smoke questions do not establish comparative accuracy.",
)
