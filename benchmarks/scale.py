import tempfile, pathlib, time, json
from unittest.mock import patch
from beru import knowledge

with (
    tempfile.TemporaryDirectory() as folder,
    patch.object(knowledge, "DB", pathlib.Path(folder) / "scale.sqlite"),
):
    c = knowledge.connect()
    rows = [
        (
            "course-" + str(i % 1000) + ".md",
            "Page " + str(i % 50),
            "Culture management organisation valeurs " + str(i),
        )
        for i in range(50000)
    ]
    c.executemany("INSERT INTO passages VALUES (?,?,?)", rows)
    c.execute(
        "INSERT INTO passages VALUES (?,?,?)",
        (
            "hofstede.md",
            "Page 1",
            "La distance hiérarchique mesure les inégalités du pouvoir.",
        ),
    )
    c.commit()
    c.close()
    times = []
    for _ in range(20):
        t = time.monotonic()
        r = knowledge.keyword_search("distance hierarchique pouvoir")
        times.append(time.monotonic() - t)
        assert r[0]["source"] == "hofstede.md"
    result = {
        "synthetic_passages": 50001,
        "queries": 20,
        "median_seconds": sorted(times)[10],
        "max_seconds": max(times),
    }
    pathlib.Path("research/benchmark/scale.json").write_text(
        json.dumps(result, indent=2)
    )
    print(result)
