# Webex Message Graph Visualization

Interactive Neo4j-style graph visualization for exploring your Webex message history.

## Overview

This visualization tool creates an interactive, force-directed graph showing:
- **Rooms** (blue bubbles) - Webex spaces/channels
- **People** (red bubbles) - Message participants
- **Connections** - Message relationships

Bubble size represents message volume. Click any bubble to see details and recent messages.

## Prerequisites

1. First, fetch your messages using the main tool:
```bash
python webex-log.py
```

This creates the `webex_messages_by_day/` directory with your message data.

## Usage

### Interactive HTML Visualization (Recommended)

Generate an interactive graph you can explore in your browser:

```bash
python visualize_interactive.py
```

This creates `webex_graph_interactive.html` and opens it automatically.

**Features:**
- 🖱️ **Drag nodes** - Click and drag any bubble to reposition
- 🔍 **Click for details** - Click bubbles to see messages and stats
- 🔎 **Zoom & Pan** - Scroll to zoom, drag background to pan
- 🎨 **Color-coded** - Blue = Rooms, Red = People
- 📊 **Size-based** - Larger bubbles = more messages
- 🏷️ **Toggle labels** - Show/hide node labels

### Static PNG Visualization

Generate a static image for reports or documentation:

```bash
python visualize_graph.py
```

This creates `webex_graph.png` showing the top 20 most active rooms.

## Dependencies

```bash
pip install networkx matplotlib
```

Already included in `requirements.txt`.

## Data Source

Both visualization tools read from `webex_messages_by_day/*.txt` files created by `webex-log.py`.

The message format:
```
[timestamp] (room_title) sender_email [involvement]: message_text
```

## Future Enhancements

See [TECH_STACK.md](TECH_STACK.md) for the full roadmap including:
- Web-based multi-user platform
- AI-powered message search
- Neo4j database integration
- Subscription-based SaaS model

## Tips

- Run `webex-log.py` regularly to keep your graph data fresh
- The interactive visualization works best with 20-100 rooms
- For large datasets (>1000 messages), the initial layout may take a few seconds
- Use zoom to focus on specific areas of interest
