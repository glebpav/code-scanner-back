import os

import pytest
import requests


@pytest.fixture(scope="session")
def base_url():
    return os.getenv("TEST_BASE_URL", "http://127.0.0.1:8080")


@pytest.fixture(scope="session")
def session():
    s = requests.Session()
    yield s
    s.close()