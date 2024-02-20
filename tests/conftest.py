import pytest
import os
from lemlist import Client


@pytest.fixture
def client():
    api_key = os.getenv("LEMLIST_API_KEY", "")
    return Client(api_key=api_key)
