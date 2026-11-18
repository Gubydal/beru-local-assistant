import pytest
from beru.question import from_text, parse


@pytest.mark.parametrize(
    "text",
    [
        "",
        "Only the question is shown?",
        "Question text is long enough\na. One",
        "Question text is long enough\nb. One\nc. Two",
        "Question text is long enough\na. One\nc. Two",
        "Question text is long enough\na. One\na. Two",
        "a. One\nb. Two",
    ],
)
def test_incomplete_or_ambiguous_capture_rejected(text):
    with pytest.raises(ValueError):
        from_text(text)


@pytest.mark.parametrize("marker", ["• ", "○ ", "© ", "O ", "o ", "", "° "])
def test_radio_marks_do_not_change_choices(marker):
    q = from_text(
        f"Quelle fonction rassemble une collectivité ?\n{marker}a. Sociale\n{marker}b. Psychique"
    )
    assert list(q.options) == ["a", "b"]


def test_timer_navigation_and_selection_do_not_change_cache_identity():
    a = from_text(
        "moodle ENCGT\nQuestion 1\nQuelle fonction rassemble une collectivité ?\n• a. Sociale\n○ b. Psychique\nTemps restant 00:10\nPage suivante"
    )
    b = from_text(
        "moodle ENCGT\nQuestion 2\nQuelle fonction rassemble une collectivité ?\n○ a. Sociale\n• b. Psychique\nTemps restant 00:09\nPage suivante"
    )
    assert a.fingerprint == b.fingerprint


def test_negation_and_option_order_change_identity():
    a = from_text("Quelle affirmation est correcte ?\na. Oui\nb. Non")
    b = from_text("Quelle affirmation est incorrecte ?\na. Oui\nb. Non")
    c = from_text("Quelle affirmation est correcte ?\na. Non\nb. Oui")
    assert len({a.fingerprint, b.fingerprint, c.fingerprint}) == 3


def test_low_confidence_rejected():
    with pytest.raises(ValueError, match="confidence"):
        parse(
            [
                {
                    "text": "Quelle fonction rassemble une collectivité ?",
                    "confidence": 0.9,
                },
                {"text": "a. Sociale", "confidence": 0.1},
                {"text": "b. Psychique", "confidence": 0.9},
            ]
        )


def test_radio_label_with_ocr_dropped_period():
    q = from_text(
        "What does high context communication rely on?\n• a Shared context\n• b. Explicit words only"
    )
    assert q.options["a"] == "Shared context"


def test_missing_label_is_not_inferred_from_arbitrary_sentence():
    with pytest.raises(ValueError):
        from_text("A society has shared meanings and traditions\nb. Second\nc. Third")


@pytest.mark.parametrize(
    "first", ["• а Eiffel Tower", "•а. Eiffel Tower", "• Α. Eiffel Tower"]
)
def test_ocr_confusable_option_glyphs_are_normalized_only_in_marker(first):
    q = from_text(
        "Quelle culture est centralisée et formalisée ?\n" + first + "\n• b. Family"
    )
    assert q.options["a"] == "Eiffel Tower"


def test_radio_circle_can_merge_with_option_label():
    q = from_text(
        "L’éducation scolaire relève-t-elle de l’apprentissage ?\n• a OUI\nOb. NON"
    )
    assert q.options == {"a": "OUI", "b": "NON"}
