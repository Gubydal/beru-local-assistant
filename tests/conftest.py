import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest


@pytest.fixture(autouse=True)
def no_cloud_retrieval_spend_in_unit_tests(monkeypatch):
    monkeypatch.setenv("BERU_CLOUD_RETRIEVAL", "0")
