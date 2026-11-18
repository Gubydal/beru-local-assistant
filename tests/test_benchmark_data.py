import re
from benchmarks.cases import dataset
from benchmarks.heldout_cases import cases


def test_generated_gold_labels_are_in_range():
    for c in dataset() + cases():
        assert c["gold"] is None or 0 <= c["gold"] < len(c["options"])


def test_both_option_does_not_refer_to_itself_after_shuffle():
    for c in dataset():
        for i, o in enumerate(c["options"]):
            match = re.search(r"Both ([A-F]) and ([A-F])", o)
            if match:
                assert chr(65 + i) not in match.groups()


def test_gold_meaning_survives_option_permutation():
    original = {c["id"]: c for c in dataset() if not c["id"].endswith("_reordered")}
    for c in dataset():
        if c["id"].endswith("_reordered"):
            first = original[c["id"].removesuffix("_reordered")]
            before = first["options"][first["gold"]]
            after = c["options"][c["gold"]]
            assert before == after or (
                before == "Both A and B" and after == "Both C and B"
            )


def test_noise_fixture_is_reproducible():
    from benchmarks.render import render

    c = dataset()[0]
    assert render(c, "noise").tobytes() == render(c, "noise").tobytes()
