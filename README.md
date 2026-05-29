# TinyMCP Server

A standalone, lightweight, local Model Context Protocol (MCP) server designed to connect with LM Studio and other custom agent environments. It exposes an array of modular tools through standard MCP communication using `stdio`.

## Built-In Providers

TinyMCP comes pre-packaged with several helpful providers:

1. **Spotify** (`spotify`)
   - Complete playback control (play, pause, next, previous).
   - Playlist management (create, add, remove, get).
   - Audio metadata and lyrics searching.
   - Search for tracks, albums, or artists.
2. **YouTube** (`youtube`)
   - Video, channel, and playlist search interactions.
   - Retrieval of video/channel metadata.
   - Extract automated YouTube transcripts.
3. **Web Tools** (`web`)
   - Web Search (via Brave API).
   - Web Fetch (retrieves and parses basic text/tables from URLs).
   - Weather Forecast (powered by Open-Meteo).

## Installation

1. Create a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

TinyMCP requires API keys to interact with external services. Create a `.env` file in the root directory and define the required secrets:

```env
# Spotify Configuration
SPOTIFY_ACCESS_TOKEN=your_token
SPOTIFY_REFRESH_TOKEN=your_refresh_token
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret

# Third-party APIs
YOUTUBE_API_KEY=your_key
BRAVE_API_KEY=your_key

DEBUG=True
```
*(Note: If configuring Spotify for the first time, you will need to perform an initial OAuth grant flow and insert your access/refresh token into the `.env`. TinyMCP will automatically refresh the token and update the `.env` file going forward).*

## Running the Server

Because TinyMCP adheres to the Model Context Protocol, it inherently operates over standard input/output streams (`stdio`). 

To run it independently or register it with an MCP client (such as LM Studio, Claude Desktop, or an Inspector GUI):
```bash
python server.py
```

### Setup with LM Studio
When setting up in LM Studio, configure the tool to use `python` as the command, and `/path/to/TinyMCP/server.py` as the arguments/script to launch. Make sure I/O is routed over `stdio`.

## Project Structure

- `server.py` - Core entry point. Initializes the server and dynamically registers tools.
- `config.json` - Map defining which Python classes implement which MCP namespaces, along with standard JSON schemas for all available tools.
- `providers/` - Extensible Python classes that enact the backend logic for tools (e.g., `web_tools_mcp.py`, `spotify_mcp.py`).

## Testing

Integration tests for the core tools are provided using `pytest`.

To run tests locally:
```bash
PYTHONPATH=. .venv/bin/pytest tests/
```

## Adding New Tools

If you would like to integrate a new API or set of tools, read out the **Extensibility** principles found in `AGENTS.MD`. Simply plug a new class into `providers/`, and list its endpoints inside `config.json`.
