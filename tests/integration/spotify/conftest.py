import pytest
import time
import os
from providers.spotify_mcp import SpotifyMCP

@pytest.fixture(scope="session")
def spotify():
    # Use real secrets from the project
    secrets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/spotify_secrets.json"))
    return SpotifyMCP(secrets_path=secrets_path)

@pytest.fixture(autouse=True)
def rate_limit_delay():
    # Add a small delay between tests to avoid rate limiting
    yield
    time.sleep(1.0)
