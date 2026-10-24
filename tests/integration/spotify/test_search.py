import pytest

def test_search_track(spotify):
    res = spotify._rpc_tool_execute({
        "name": "search",
        "arguments": {"query": "Daft Punk", "type": ["track"], "limit": 3}
    })
    assert res.get("status") == "success", f"Search failed: {res}"
    data = res.get("data", [])
    assert len(data) > 0
    assert data[0]["type"] == "track"
    assert "Daft Punk" in str(data[0].get("artist", ""))

def test_search_artist(spotify):
    res = spotify._rpc_tool_execute({
        "name": "search",
        "arguments": {"query": "The Weeknd", "type": ["artist"], "limit": 1}
    })
    assert res.get("status") == "success"
    data = res.get("data", [])
    assert len(data) > 0
    assert data[0]["type"] == "artist"
