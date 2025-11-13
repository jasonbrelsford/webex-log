#!/usr/bin/env python3
"""
Interactive Neo4j-style graph visualization for Webex messages
Generates an HTML file with draggable, clickable bubbles
"""
import os
import re
import json
from collections import defaultdict

def parse_message_file(filepath):
    """Parse a single message file and extract structured data"""
    messages = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'\[(.*?)\] \((.*?)\) (.*?) \[(.*?)\]: (.*)', line)
            if match:
                timestamp, room, sender, involvement, text = match.groups()
                messages.append({
                    'timestamp': timestamp,
                    'room': room,
                    'sender': sender,
                    'involvement': involvement,
                    'text': text
                })
    return messages

def load_all_messages(directory='webex_messages_by_day'):
    """Load all messages from the directory"""
    all_messages = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.txt'):
            filepath = os.path.join(directory, filename)
            all_messages.extend(parse_message_file(filepath))
    return all_messages

def build_graph_data(messages):
    """Build graph data structure for D3.js"""
    nodes = {}
    links = []
    room_messages = defaultdict(list)
    person_messages = defaultdict(list)
    
    for msg in messages:
        room = msg['room']
        sender = msg['sender']
        
        # Add room node
        if room not in nodes:
            nodes[room] = {
                'id': room,
                'label': room,
                'type': 'room',
                'count': 0,
                'messages': []
            }
        nodes[room]['count'] += 1
        nodes[room]['messages'].append(msg)
        
        # Add person node
        if sender not in nodes:
            nodes[sender] = {
                'id': sender,
                'label': sender,
                'type': 'person',
                'count': 0,
                'messages': []
            }
        nodes[sender]['count'] += 1
        nodes[sender]['messages'].append(msg)
        
        # Add link
        link_id = f"{sender}-{room}"
        link_exists = False
        for link in links:
            if link['source'] == sender and link['target'] == room:
                link['value'] += 1
                link_exists = True
                break
        
        if not link_exists:
            links.append({
                'source': sender,
                'target': room,
                'value': 1
            })
    
    return {
        'nodes': list(nodes.values()),
        'links': links
    }

def generate_html(graph_data):
    """Generate interactive HTML with D3.js force-directed graph"""
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Webex Message Network</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #1a1a1a;
            color: #fff;
            overflow: hidden;
        }
        #graph {
            width: 100vw;
            height: 100vh;
        }
        #info-panel {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(30, 30, 30, 0.95);
            border: 1px solid #444;
            border-radius: 8px;
            padding: 20px;
            max-width: 400px;
            max-height: 80vh;
            overflow-y: auto;
            display: none;
        }
        #info-panel.visible {
            display: block;
        }
        #info-panel h2 {
            margin: 0 0 10px 0;
            font-size: 18px;
            color: #4a9eff;
        }
        #info-panel .stat {
            margin: 5px 0;
            font-size: 14px;
        }
        #info-panel .messages {
            margin-top: 15px;
            max-height: 300px;
            overflow-y: auto;
        }
        #info-panel .message {
            background: rgba(50, 50, 50, 0.5);
            padding: 8px;
            margin: 5px 0;
            border-radius: 4px;
            font-size: 12px;
        }
        #info-panel .close {
            position: absolute;
            top: 10px;
            right: 10px;
            cursor: pointer;
            font-size: 20px;
            color: #888;
        }
        #info-panel .close:hover {
            color: #fff;
        }
        .controls {
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(30, 30, 30, 0.95);
            border: 1px solid #444;
            border-radius: 8px;
            padding: 15px;
        }
        .controls h3 {
            margin: 0 0 10px 0;
            font-size: 16px;
        }
        .controls label {
            display: block;
            margin: 10px 0;
            font-size: 14px;
        }
        .legend {
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: rgba(30, 30, 30, 0.95);
            border: 1px solid #444;
            border-radius: 8px;
            padding: 15px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin: 5px 0;
            font-size: 14px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div id="graph"></div>
    
    <div class="controls">
        <h3>Webex Message Network</h3>
        <label>
            <input type="checkbox" id="show-labels" checked> Show Labels
        </label>
    </div>
    
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background: #4a9eff;"></div>
            <span>Rooms</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #ff6b6b;"></div>
            <span>People</span>
        </div>
    </div>
    
    <div id="info-panel">
        <span class="close" onclick="closePanel()">×</span>
        <div id="info-content"></div>
    </div>

    <script>
        const graphData = """ + json.dumps(graph_data) + """;
        
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        const svg = d3.select("#graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        
        const g = svg.append("g");
        
        // Zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 10])
            .on("zoom", (event) => {
                g.attr("transform", event.transform);
            });
        
        svg.call(zoom);
        
        // Force simulation
        const simulation = d3.forceSimulation(graphData.nodes)
            .force("link", d3.forceLink(graphData.links)
                .id(d => d.id)
                .distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(d => Math.sqrt(d.count) * 3 + 10));
        
        // Links
        const link = g.append("g")
            .selectAll("line")
            .data(graphData.links)
            .join("line")
            .attr("stroke", "#555")
            .attr("stroke-opacity", 0.6)
            .attr("stroke-width", d => Math.sqrt(d.value));
        
        // Nodes
        const node = g.append("g")
            .selectAll("circle")
            .data(graphData.nodes)
            .join("circle")
            .attr("r", d => Math.sqrt(d.count) * 3 + 5)
            .attr("fill", d => d.type === 'room' ? '#4a9eff' : '#ff6b6b')
            .attr("stroke", "#fff")
            .attr("stroke-width", 2)
            .style("cursor", "pointer")
            .call(drag(simulation))
            .on("click", showNodeInfo)
            .on("mouseover", function() {
                d3.select(this).attr("stroke-width", 4);
            })
            .on("mouseout", function() {
                d3.select(this).attr("stroke-width", 2);
            });
        
        // Labels
        const labels = g.append("g")
            .selectAll("text")
            .data(graphData.nodes)
            .join("text")
            .text(d => d.label)
            .attr("font-size", 10)
            .attr("fill", "#fff")
            .attr("text-anchor", "middle")
            .attr("dy", d => Math.sqrt(d.count) * 3 + 20)
            .style("pointer-events", "none");
        
        // Update positions
        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
            
            labels
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        });
        
        // Drag behavior
        function drag(simulation) {
            function dragstarted(event) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            }
            
            function dragged(event) {
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            }
            
            function dragended(event) {
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }
            
            return d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended);
        }
        
        // Show node info
        function showNodeInfo(event, d) {
            const panel = document.getElementById('info-panel');
            const content = document.getElementById('info-content');
            
            let html = `<h2>${d.label}</h2>`;
            html += `<div class="stat">Type: ${d.type}</div>`;
            html += `<div class="stat">Messages: ${d.count}</div>`;
            
            if (d.messages.length > 0) {
                html += `<div class="messages">`;
                html += `<h3>Recent Messages (${Math.min(10, d.messages.length)})</h3>`;
                d.messages.slice(0, 10).forEach(msg => {
                    html += `<div class="message">`;
                    html += `<div><strong>${msg.sender}</strong></div>`;
                    html += `<div>${msg.text.substring(0, 100)}${msg.text.length > 100 ? '...' : ''}</div>`;
                    html += `<div style="color: #888; font-size: 10px;">${msg.timestamp}</div>`;
                    html += `</div>`;
                });
                html += `</div>`;
            }
            
            content.innerHTML = html;
            panel.classList.add('visible');
        }
        
        function closePanel() {
            document.getElementById('info-panel').classList.remove('visible');
        }
        
        // Toggle labels
        document.getElementById('show-labels').addEventListener('change', (e) => {
            labels.style('display', e.target.checked ? 'block' : 'none');
        });
    </script>
</body>
</html>"""
    return html

def main():
    print("Loading messages...")
    messages = load_all_messages()
    
    if not messages:
        print("No messages found. Run webex-log.py first.")
        return
    
    print(f"Loaded {len(messages)} messages")
    print("Building graph data...")
    
    graph_data = build_graph_data(messages)
    
    print(f"Graph contains {len(graph_data['nodes'])} nodes and {len(graph_data['links'])} links")
    print("Generating interactive visualization...")
    
    html = generate_html(graph_data)
    
    output_file = 'webex_graph_interactive.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✓ Interactive graph saved to {output_file}")
    print(f"  Open it in your browser to explore!")
    
    # Try to open in browser
    import webbrowser
    webbrowser.open(f'file://{os.path.abspath(output_file)}')

if __name__ == '__main__':
    main()
