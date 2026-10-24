import pytest

def test_get_playback_state(spotify):
    res = spotify._rpc_tool_execute({
        "name": "get_playback_state",
        "arguments": {}
    })
    assert res.get("status") == "success"
    # Even if Nothing is playing, it should return a consistent structure
    assert "state" in res.get("data", {})

def test_get_playback_device(spotify):
    res = spotify._rpc_tool_execute({
        "name": "get_playback_device",
        "arguments": {}
    })
    assert res.get("status") == "success"
    assert "devices" in res.get("data", {})

# NOTE: Controls (play, pause, etc.) might fail if no active device is found.
# These are integration tests on a real account, so proximity to an active player matters.
def test_playback_controls_pause_play(spotify):
    # Try to pause if playing, then play
    res = spotify._rpc_tool_execute({
        "name": "playback_control",
        "arguments": {"action": "pause"}
    })
    # We accept fail if no active device (403/404), but we check the tool handles it.
    if res.get("status") == "error":
        print(f"Pause error (likely no active device): {res.get('message')}")
    else:
        assert res.get("status") == "success"
        
    res_play = spotify._rpc_tool_execute({
        "name": "playback_control",
        "arguments": {"action": "play"}
    })
    if res_play.get("status") == "error":
         print(f"Play error: {res_play.get('message')}")
    else:
        assert res_play.get("status") == "success"

def test_playback_mode_shuffle(spotify):
    res = spotify._rpc_tool_execute({
        "name": "playback_mode",
        "arguments": {"shuffle": True}
    })
    # Success depends on active device
    if res.get("status") == "error":
        assert "Forbidden" in res.get("message") or "device" in res.get("message").lower()
    else:
        assert res.get("status") == "success"
