# DaVinci Resolve MCP Server

A Model Context Protocol (MCP) server for interacting with DaVinci Resolve and Fusion. This server allows AI assistants like Claude to directly interact with and control DaVinci Resolve through the Model Context Protocol.

## Features

- Two-way communication: Connect Claude AI to DaVinci Resolve through the MCP protocol
- Project management: Create, open, and manage DaVinci Resolve projects
- Timeline manipulation: Create, modify, and navigate timelines
- Media management: Import, organize, and manage media in the Media Pool
- Fusion integration: Create and modify Fusion compositions
- Scene inspection: Get detailed information about the current DaVinci Resolve project
- Code execution: Run arbitrary Python code in DaVinci Resolve from Claude

## Installation

### Prerequisites

- DaVinci Resolve Studio (version 17 or higher recommended)
- Python 3.8 or higher
- Claude Desktop (for AI integration)

### Setup

1. Clone this repository:
   ```
   git clone https://github.com/apvlv/davinci-resolve-mcp.git
   cd davinci-resolve-mcp
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install the MCP server in Claude Desktop:
   ```
   mcp install src/resolve_mcp/server.py
   ```

   Alternatively, you can install with the editable flag for development:
   ```
   mcp install src/resolve_mcp/server.py --with-editable .
   ```

## Usage

### With Claude Desktop

1. Start DaVinci Resolve
2. In Claude Desktop, connect to the "DaVinci Resolve MCP" server
3. You can now interact with DaVinci Resolve through Claude

### With 5ire

[5ire](https://5ire.app/) is an open-source cross-platform desktop AI assistant and MCP client that's compatible with this server.

1. Install 5ire from [GitHub](https://github.com/nanbingxyz/5ire) or using Homebrew on macOS:
   ```
   brew tap brewforge/extras
   brew install --cask 5ire
   ```
2. Start DaVinci Resolve
3. In 5ire, add the DaVinci Resolve MCP server
4. Connect to the server using your preferred AI model (OpenAI, Claude, etc.)
5. You can now interact with DaVinci Resolve through 5ire

## Available Commands

### Resources (Information Retrieval)

- `project://current` - Get information about the current project
- `project://timelines` - Get a list of timelines in the current project
- `timeline://current` - Get information about the current timeline
- `mediapool://folders` - Get a list of folders in the media pool
- `mediapool://current` - Get information about the current media pool folder
- `storage://volumes` - Get a list of mounted volumes in the media storage
- `system://status` - Get the current status of the DaVinci Resolve connection

### Project Management

- `create_project(name)` - Create a new DaVinci Resolve project
- `load_project(name)` - Load an existing DaVinci Resolve project
- `save_project()` - Save the current DaVinci Resolve project

### Timeline Management

- `create_timeline(name)` - Create a new timeline in the current project
- `set_current_timeline(index)` - Set the current timeline by index (1-based)

### Media Management

- `import_media(file_paths)` - Import media files into the current media pool folder
- `create_folder(name)` - Create a new folder in the current media pool folder
- `create_timeline_from_clips(name, clip_indices)` - Create a new timeline from clips in the current media pool folder

### Fusion Integration

- `add_fusion_comp_to_clip(timeline_index, track_type, track_index, item_index)` - Add a Fusion composition to a clip in the timeline
- `create_fusion_node(node_type, parameters)` - Create a specific Fusion node in the current composition
- `create_fusion_node_chain(node_chain)` - Create a chain of connected Fusion nodes in the current composition

### Page Navigation

- `open_page(page_name)` - Open a specific page in DaVinci Resolve (media, edit, fusion, color, fairlight, deliver)

### Advanced Operations

- `execute_python(code)` - Execute arbitrary Python code in DaVinci Resolve
- `execute_lua(script)` - Execute a Lua script in DaVinci Resolve's Fusion

## Examples

- "Create a new project named 'My Documentary'"
- "Import all video files from the Downloads folder"
- "Create a new timeline with the selected clips"
- "Apply a Fusion effect to the selected clip"
- "Get information about the current project"
- "Switch to the Color page"
- "Save the current project"
- "Create a folder named 'Raw Footage' in the media pool"
- "Create a Blur node in the current Fusion composition"
- "Create a Text node with the content 'Hello World'"
- "Create a chain of nodes: MediaIn -> Blur -> ColorCorrector -> MediaOut"

## Technical Details

The server uses the Model Context Protocol to communicate between Claude and DaVinci Resolve. It leverages DaVinci Resolve's Python API to control the application.

## License

MIT
