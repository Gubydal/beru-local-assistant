import json
from unittest.mock import Mock, patch
import pytest
from beru.providers import answer, read_image


def mock_response(data):
    r = Mock()
    r.json.return_value = data
    return r


def test_deepseek_serialization_with_image_and_response_validation():
    r = mock_response(
        {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {"answer": "• a. Oui", "citations": [1], "uncertain": False}
                        )
                    }
                }
            ]
        }
    )
    with (
        patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test"}),
        patch("beru.providers.load_env"),
        patch("beru.providers.requests.post", return_value=r) as post,
    ):
        result = answer(
            "Question", [{"text": "source"}], provider="deepseek", image=b"png"
        )
        assert result["answer"] == "a. Oui"
        body = post.call_args.kwargs["json"]
        assert body["messages"][0]["role"] == "system"
        assert body["messages"][1]["content"][1]["type"] == "image_url"


@pytest.mark.parametrize("provider", ["gemini", "deepseek"])
def test_visual_extraction_validates_complete_choices(provider):
    data = {
        "stem": "Quelle fonction rassemble une collectivité ?",
        "options": {"a": "Sociale", "b": "Psychique"},
        "complete": True,
    }
    payload = (
        {"candidates": [{"content": {"parts": [{"text": json.dumps(data)}]}}]}
        if provider == "gemini"
        else {"choices": [{"message": {"content": json.dumps(data)}}]}
    )
    with (
        patch.dict(
            "os.environ", {"GEMINI_API_KEY": "test", "DEEPSEEK_API_KEY": "test"}
        ),
        patch("beru.providers.load_env"),
        patch("beru.providers.requests.post", return_value=mock_response(payload)),
    ):
        q = read_image(b"png", provider)
        assert q.options["a"] == "Sociale"
        assert q.confidence == 0


@pytest.mark.parametrize(
    "data",
    [
        {"complete": False},
        {"complete": True, "stem": "Question", "options": []},
        {"complete": True, "stem": "Question", "options": {"a": "Only one"}},
    ],
)
def test_visual_recovery_rejects_incomplete_payload(data):
    payload = {"candidates": [{"content": {"parts": [{"text": json.dumps(data)}]}}]}
    with (
        patch.dict("os.environ", {"GEMINI_API_KEY": "test"}),
        patch("beru.providers.load_env"),
        patch("beru.providers.requests.post", return_value=mock_response(payload)),
    ):
        with pytest.raises(ValueError):
            read_image(b"png")


def test_markdown_json_fence_is_normalized():
    payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": '```json\n{"answer":"a. Oui","uncertain":true,"citations":[]}\n```'
                        }
                    ]
                }
            }
        ]
    }
    with (
        patch.dict("os.environ", {"GEMINI_API_KEY": "test"}),
        patch("beru.providers.load_env"),
        patch("beru.providers.requests.post", return_value=mock_response(payload)),
    ):
        assert answer("Question", [])["answer"] == "a. Oui"
