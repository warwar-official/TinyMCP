import pytest
import datetime
import time

# Shared state between tests in this file
state = {"playlist_id": None, "track_uri": None}

def test_create_playlist(spotify):
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    name = f"Test Playlist {ts}"
    res = spotify._rpc_tool_execute({
        "name": "create_playlist",
        "arguments": {"name": name, "description": "Integration Test Playlist", "public": True}
    })
    assert res.get("status") == "success", f"Create failed: {res}"
    pid = res.get("data", {}).get("id")
    assert pid is not None
    state["playlist_id"] = pid

def test_add_track_to_playlist(spotify):
    pid = state["playlist_id"]
    assert pid is not None
    
    # 1. Search for a track to add
    search = spotify._rpc_tool_execute({
        "name": "search",
        "arguments": {"query": "Blinding Lights", "type": ["track"], "limit": 1}
    })
    track_uri = search["data"][0]["uri"]
    state["track_uri"] = track_uri
    
    # 2. Add to playlist
    res = spotify._rpc_tool_execute({
        "name": "add_to_playlist",
        "arguments": {"playlist_id": pid, "uris": [track_uri]}
    })
    assert res.get("status") == "success", f"Add track failed: {res}"

def test_get_playlist_details(spotify):
    pid = state["playlist_id"]
    time.sleep(2)  # Wait for eventual consistency
    res = spotify._rpc_tool_execute({
        "name": "get_playlist",
        "arguments": {"playlist_id": pid}
    })
    assert res.get("status") == "success", f"Get playlist failed: {res}"
    data = res.get("data", {})
    assert data.get("total_tracks") >= 1
    assert any(item["uri"] == state["track_uri"] for item in data.get("items", []))

def test_get_user_playlists(spotify):
    res = spotify._rpc_tool_execute({
        "name": "get_user_playlists",
        "arguments": {"limit": 10}
    })
    assert res.get("status") == "success"
    data = res.get("data", {})
    assert data.get("total") > 0
    assert any(pl["uri"].endswith(state["playlist_id"]) for pl in data.get("items", []))

def test_remove_track_from_playlist(spotify):
    pid = state["playlist_id"]
    track_uri = state["track_uri"]
    res = spotify._rpc_tool_execute({
        "name": "remove_from_playlist",
        "arguments": {"playlist_id": pid, "uris": [track_uri]}
    })
    assert res.get("status") == "success", f"Remove track failed: {res}"
    
    time.sleep(2)
    check = spotify._rpc_tool_execute({
        "name": "get_playlist",
        "arguments": {"playlist_id": pid}
    })
    assert check.get("data", {}).get("total_tracks") == 0
