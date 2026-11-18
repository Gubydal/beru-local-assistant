from unittest.mock import patch
import pytest
from beru.engine import Engine
from beru.question import from_text
from PIL import Image

Q = from_text("Quelle fonction rassemble une collectivité ?\na. Sociale\nb. Psychique")


@pytest.mark.parametrize(
    "answer", ["c. Inexistante", "Je pense que oui", "", "Bla bla"]
)
def test_out_of_range_or_missing_answer_rejected(answer):
    with (
        patch("beru.engine.read", return_value=Q),
        patch("beru.engine.search", return_value=[]),
        patch("beru.engine.answer", return_value={"answer": answer}),
    ):
        with pytest.raises(ValueError):
            Engine().solve(Image.new("RGB", (50, 50)))


def test_cache_scoped_to_model_and_manual_bypass():
    engine = Engine()
    with (
        patch("beru.engine.read", return_value=Q),
        patch("beru.engine.search", return_value=[]),
        patch(
            "beru.engine.answer",
            return_value={"answer": "a. Sociale", "uncertain": False},
        ) as mock,
    ):
        img = Image.new("RGB", (50, 50))
        engine.solve(img, model="one")
        assert engine.solve(img, model="one")["cached"]
        engine.solve(img, model="two")
        engine.solve(img, model="two", use_cache=False)
        assert mock.call_count == 3


def test_incomplete_capture_never_calls_provider():
    with (
        patch("beru.engine.read", side_effect=ValueError("Incomplete")),
        patch("beru.engine.answer") as mock,
    ):
        with pytest.raises(ValueError):
            Engine().solve(Image.new("RGB", (50, 50)))
        mock.assert_not_called()


def test_manual_refresh_replaces_old_cached_answer():
    engine = Engine()
    image = Image.new("RGB", (50, 50))
    with (
        patch("beru.engine.read", return_value=Q),
        patch("beru.engine.search", return_value=[]),
        patch(
            "beru.engine.answer",
            side_effect=[
                {"answer": "a. Old", "uncertain": True},
                {"answer": "b. New", "uncertain": False},
            ],
        ) as mocked,
    ):
        engine.solve(image)
        engine.solve(image, refresh=True)
        r = engine.solve(image)
        assert mocked.call_count == 2 and r["answer"] == "b. New" and r["cached"]


def test_visual_recovery_only_when_explicitly_enabled():
    engine = Engine()
    img = Image.new("RGB", (50, 50))
    with (
        patch("beru.engine.read", side_effect=ValueError("unreadable")),
        patch("beru.engine.read_image", return_value=Q) as visual,
        patch("beru.engine.search", return_value=[]),
        patch(
            "beru.engine.answer",
            return_value={"answer": "a. Correct", "uncertain": False},
        ),
    ):
        with pytest.raises(ValueError):
            engine.solve(img, visual=False)
        visual.assert_not_called()
        r = engine.solve(img, visual=True)
        assert r["vision_fallback"]


def test_explicit_abstention_is_not_displayed_as_a_choice():
    from beru.question import Abstention

    with (
        patch("beru.engine.read", return_value=Q),
        patch("beru.engine.search", return_value=[]),
        patch("beru.engine.answer", return_value={"answer": "NONE", "uncertain": True}),
    ):
        with pytest.raises(Abstention):
            Engine().solve(Image.new("RGB", (50, 50)))
