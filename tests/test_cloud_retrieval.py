import numpy as np
import pytest, requests
from unittest.mock import patch, Mock
from beru import cloud_retrieval as cloud


@pytest.fixture
def index_state(monkeypatch):
    monkeypatch.setenv("BERU_CLOUD_RETRIEVAL", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "test")
    monkeypatch.setattr(cloud, "_cache", {})
    return {
        "ids": np.array([7, 9]),
        "vectors": np.array([[1, 0], [0, 1]], dtype=np.float32),
        "stamp": (1, 1),
    }


def test_cloud_embedding_query_uses_local_ids_and_cache(index_state):
    response = Mock()
    response.json.return_value = {"embedding": {"values": [0, 1]}}
    with (
        patch.object(cloud, "_index", return_value=index_state),
        patch("beru.providers.load_env"),
        patch.object(cloud.requests, "post", return_value=response) as post,
    ):
        assert cloud.search("Culture")[0]["id"] == 9
        assert cloud.search("Culture")[0]["id"] == 9
        assert post.call_count == 1
        assert post.call_args.kwargs["json"]["taskType"] == "RETRIEVAL_QUERY"
        assert post.call_args.kwargs["timeout"] == (0.5, 2)


def test_cloud_timeout_returns_empty_for_local_fallback(index_state):
    with (
        patch.object(cloud, "_index", return_value=index_state),
        patch("beru.providers.load_env"),
        patch.object(cloud.requests, "post", side_effect=requests.Timeout),
    ):
        assert cloud.search("Culture") == []


@pytest.mark.parametrize("values", [[float("nan"), 0], [1, 2, 3], []])
def test_invalid_embedding_never_maps_to_evidence(index_state, values):
    response = Mock()
    response.json.return_value = {"embedding": {"values": values}}
    with (
        patch.object(cloud, "_index", return_value=index_state),
        patch("beru.providers.load_env"),
        patch.object(cloud.requests, "post", return_value=response),
    ):
        assert cloud.search("Culture") == []


def test_cloud_switch_disables_all_network_calls(monkeypatch):
    monkeypatch.setenv("BERU_CLOUD_RETRIEVAL", "0")
    with patch.object(cloud.requests, "post") as post:
        assert cloud.search("Culture") == []
        post.assert_not_called()
