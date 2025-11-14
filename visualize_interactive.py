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
        .controls input[type="text"],
        .controls input[type="date"] {
            width: 100%;
            padding: 8px;
            margin: 10px 0;
            background: rgba(50, 50, 50, 0.8);
            border: 1px solid #555;
            border-radius: 4px;
            color: #fff;
            font-size: 14px;
        }
        .controls input[type="text"]:focus,
        .controls input[type="date"]:focus {
            outline: none;
            border-color: #4a9eff;
        }
        .controls input[type="date"]::-webkit-calendar-picker-indicator {
            filter: invert(1);
        }
        .date-range {
            margin: 15px 0;
            padding: 10px 0;
            border-top: 1px solid #444;
            border-bottom: 1px solid #444;
        }
        .date-range h4 {
            margin: 0 0 10px 0;
            font-size: 14px;
            color: #4a9eff;
        }
        .controls button {
            width: 100%;
            padding: 8px;
            margin: 5px 0;
            background: #4a9eff;
            border: none;
            border-radius: 4px;
            color: #fff;
            font-size: 14px;
            cursor: pointer;
        }
        .controls button:hover {
            background: #3a8eef;
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
        
        <input type="text" id="search-input" placeholder="Search nodes...">
        
        <div class="date-range">
            <h4>Date Range Filter</h4>
            <label style="font-size: 12px; color: #888;">Start Date</label>
            <input type="date" id="start-date">
            <label style="font-size: 12px; color: #888;">End Date</label>
            <input type="date" id="end-date">
            <button onclick="applyDateFilter()">Apply Filter</button>
            <button onclick="clearDateFilter()">Clear</button>
        </div>
        
        <label>
            <input type="checkbox" id="show-labels" checked> Show Labels
        </label>
        
        <label>
            <input type="checkbox" id="filter-rooms" checked> Show Rooms
        </label>
        
        <label>
            <input type="checkbox" id="filter-people" checked> Show People
        </label>
        
        <button onclick="exportData()">Export JSON</button>
        <button onclick="resetView()">Reset View</button>
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
        let graphData = """ + json.dumps(graph_data) + """;
        
        // Check for filtered data FIRST
        const filtered = sessionStorage.getItem('filteredGraphData');
        if (filtered) {
            graphData = JSON.parse(filtered);
        }
        
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
        
        function exportData() {
            const dataStr = JSON.stringify(graphData, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'webex_graph_data.json';
            link.click();
            URL.revokeObjectURL(url);
        }
        
        function resetView() {
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity
            );
            simulation.alpha(1).restart();
        }
        
        // Date filtering
        let originalGraphData = JSON.parse(JSON.stringify(graphData));
        
        function applyDateFilter() {
            const startDate = document.getElementById('start-date').value;
            const endDate = document.getElementById('end-date').value;
            
            if (!startDate && !endDate) {
                alert('Please select at least one date');
                return;
            }
            
            const start = startDate ? new Date(startDate) : new Date('1970-01-01');
            const end = endDate ? new Date(endDate) : new Date('2099-12-31');
            end.setHours(23, 59, 59, 999);
            
            // Filter messages by date
            const filteredNodes = {};
            
            originalGraphData.nodes.forEach(node => {
                const filteredMessages = node.messages.filter(msg => {
                    const msgDate = new Date(msg.timestamp);
                    return msgDate >= start && msgDate <= end;
                });
                
                if (filteredMessages.length > 0) {
                    filteredNodes[node.id] = {
                        ...node,
                        messages: filteredMessages,
                        count: filteredMessages.length
                    };
                }
            });
            
            // Filter and rebuild links
            const filteredLinks = [];
            const nodeIds = new Set(Object.keys(filteredNodes));
            
            originalGraphData.links.forEach(link => {
                const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
                const targetId = typeof link.target === 'object' ? link.target.id : link.target;
                
                if (nodeIds.has(sourceId) && nodeIds.has(targetId)) {
                    filteredLinks.push({
                        source: sourceId,
                        target: targetId,
                        value: link.value
                    });
                }
            });
            
            // Rebuild graph with filtered data
            const newGraphData = {
                nodes: Object.values(filteredNodes),
                links: filteredLinks
            };
            
            if (newGraphData.nodes.length === 0) {
                alert('No messages found in this date range');
                return;
            }
            
            // Reload visualization
            sessionStorage.setItem('filteredGraphData', JSON.stringify(newGraphData));
            location.reload();
        }
        
        function clearDateFilter() {
            document.getElementById('start-date').value = '';
            document.getElementById('end-date').value = '';
            sessionStorage.removeItem('filteredGraphData');
            location.reload();
        }
        
        // Toggle labels
        document.getElementById('show-labels').addEventListener('change', (e) => {
            labels.style('display', e.target.checked ? 'block' : 'none');
        });
        
        // Search functionality
        let searchTimeout;
        document.getElementById('search-input').addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = e.target.value.toLowerCase();
                
                node.style('opacity', d => {
                    if (!query) return 1;
                    return d.label.toLowerCase().includes(query) ? 1 : 0.2;
                });
                
                labels.style('opacity', d => {
                    if (!query) return 1;
                    return d.label.toLowerCase().includes(query) ? 1 : 0.2;
                });
                
                link.style('opacity', d => {
                    if (!query) return 0.6;
                    const sourceMatch = d.source.label.toLowerCase().includes(query);
                    const targetMatch = d.target.label.toLowerCase().includes(query);
                    return (sourceMatch || targetMatch) ? 0.6 : 0.1;
                });
            }, 300);
        });
        
        // Filter by type
        document.getElementById('filter-rooms').addEventListener('change', updateFilters);
        document.getElementById('filter-people').addEventListener('change', updateFilters);
        
        function updateFilters() {
            const showRooms = document.getElementById('filter-rooms').checked;
            const showPeople = document.getElementById('filter-people').checked;
            
            node.style('display', d => {
                if (d.type === 'room' && !showRooms) return 'none';
                if (d.type === 'person' && !showPeople) return 'none';
                return 'block';
            });
            
            labels.style('display', d => {
                if (d.type === 'room' && !showRooms) return 'none';
                if (d.type === 'person' && !showPeople) return 'none';
                const showLabelsChecked = document.getElementById('show-labels').checked;
                return showLabelsChecked ? 'block' : 'none';
            });
            
            link.style('display', d => {
                const sourceVisible = (d.source.type === 'room' && showRooms) || (d.source.type === 'person' && showPeople);
                const targetVisible = (d.target.type === 'room' && showRooms) || (d.target.type === 'person' && showPeople);
                return (sourceVisible && targetVisible) ? 'block' : 'none';
            });
        }
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
