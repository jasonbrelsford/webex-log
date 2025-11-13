# Webex Message Logger

A Python tool to download and organize Webex messages where you were involved (as sender, mentioned participant, or general participant).

## Features

- Downloads messages from all Webex rooms you have access to
- Categorizes your involvement level (sender, mentioned, participant)
- Organizes messages by date into separate text files
- Handles API pagination for complete message retrieval
- Token expiration handling with interactive renewal

## Installation

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Setup

1. Get your Webex API token from [Webex Developer Portal](https://developer.webex.com/docs/api/getting-started)
2. Create a `config.py` file with your credentials:
```python
access_token = 'YOUR_WEBEX_TOKEN_HERE'
your_email = 'your_email@example.com'
```

## Usage

Run the main script:
```bash
python webex-log.py
```

The script will:
1. Fetch all rooms you have access to
2. Download messages from each room
3. Create a `webex_messages_by_day` directory
4. Save messages organized by date (YYYY-MM-DD.txt format)

## Output Format

Each daily log file contains messages in this format:
```
[timestamp] (room_title) sender_email [involvement_level]: message_text
```

Where involvement levels are:
- `sender`: Messages you sent
- `mentioned`: Messages where you were mentioned
- `participant`: Messages from rooms you're in

## Visualization

This project includes interactive graph visualization tools. See [README_GRAPH.md](README_GRAPH.md) for details.

**Quick start:**
```bash
python visualize_interactive.py
```

Creates an interactive Neo4j-style graph showing your message network with draggable, clickable bubbles.

## Files

### Core Tools
- `webex-log.py`: Main script that downloads all messages and saves them to dated text files
- `config.py`: Configuration file for your Webex token and email (not committed to git)

### Visualization (graph-ai branch)
- `visualize_interactive.py`: Interactive HTML graph visualization
- `visualize_graph.py`: Static PNG graph visualization
- `TECH_STACK.md`: Full technical roadmap for SaaS platform
- `README_GRAPH.md`: Visualization documentation

### Configuration
- `requirements.txt`: Python dependencies
- `setup.py`: Package setup configuration
- `.gitignore`: Protects sensitive files from being committed

## Dependencies

- `requests`: HTTP API calls
- `networkx`: Network analysis (optional)
- `matplotlib`: Data visualization (optional)

## Querying Your Messages

If you're using an IDE with Amazon Q or similar AI assistant, you can query your messages naturally:

1. Reference the messages folder with `@webex_messages_by_day`
2. Ask questions like:
   - "When did I last discuss terraform in @webex_messages_by_day?"
   - "Find conversations about AWS in @webex_messages_by_day"
   - "Who did I talk to about the database upgrade in @webex_messages_by_day?"

The AI assistant can read and search through your saved messages to answer questions in natural language.

## Security Note

Keep your Webex API token secure and never commit it to version control. Consider using environment variables for token storage.