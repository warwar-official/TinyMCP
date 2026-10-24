import pytest

def test_get_lyrics(spotify):
    res = spotify._rpc_tool_execute({
        "name": "get_lyrics",
        "arguments": {"artist": "The Beatles", "track_name": "Yesterday"}
    })
    assert res.get("status") == "success", f"Lyrics failed: {res}"
    lyrics = res.get("data", {}).get("lyrics", "")
    assert len(lyrics) > 100
    assert "Yesterday" in lyrics
