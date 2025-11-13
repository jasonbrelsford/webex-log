#!/usr/bin/env python3
"""
Webex Message Graph Visualization
Parses message files and creates an interactive network graph
"""
import os
import re
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt

def parse_message_file(filepath):
    """Parse a single message file and extract structured data"""
    messages = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            # Parse: [timestamp] (room_title) sender_email [involvement]: message_text
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
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            filepath = os.path.join(directory, filename)
            all_messages.extend(parse_message_file(filepath))
    return all_messages

def build_graph(messages):
    """Build NetworkX graph from messages"""
    G = nx.Graph()
    
    # Track statistics
    room_counts = defaultdict(int)
    person_counts = defaultdict(int)
    
    for msg in messages:
        room = msg['room']
        sender = msg['sender']
        
        # Add nodes
        G.add_node(sender, type='person')
        G.add_node(room, type='room')
        
        # Add edge between person and room
        if G.has_edge(sender, room):
            G[sender][room]['weight'] += 1
        else:
            G.add_edge(sender, room, weight=1)
        
        room_counts[room] += 1
        person_counts[sender] += 1
    
    return G, room_counts, person_counts

def visualize_graph(G, room_counts, person_counts, top_n=20):
    """Create interactive visualization of the graph"""
    
    # Filter to top N most active rooms
    top_rooms = sorted(room_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_room_names = [room for room, _ in top_rooms]
    
    # Create subgraph with only top rooms and their participants
    nodes_to_keep = set(top_room_names)
    for node in G.nodes():
        if G.nodes[node].get('type') == 'person':
            # Keep person if they're connected to a top room
            for neighbor in G.neighbors(node):
                if neighbor in top_room_names:
                    nodes_to_keep.add(node)
                    break
    
    subgraph = G.subgraph(nodes_to_keep)
    
    # Set up the plot
    plt.figure(figsize=(16, 12))
    
    # Position nodes using spring layout
    pos = nx.spring_layout(subgraph, k=2, iterations=50)
    
    # Separate nodes by type
    room_nodes = [n for n in subgraph.nodes() if subgraph.nodes[n].get('type') == 'room']
    person_nodes = [n for n in subgraph.nodes() if subgraph.nodes[n].get('type') == 'person']
    
    # Draw nodes
    nx.draw_networkx_nodes(subgraph, pos, nodelist=room_nodes, 
                          node_color='lightblue', node_size=1000, 
                          label='Rooms', alpha=0.8)
    nx.draw_networkx_nodes(subgraph, pos, nodelist=person_nodes, 
                          node_color='lightcoral', node_size=500, 
                          label='People', alpha=0.8)
    
    # Draw edges with varying thickness based on message count
    edges = subgraph.edges()
    weights = [subgraph[u][v]['weight'] for u, v in edges]
    max_weight = max(weights) if weights else 1
    edge_widths = [2 * (w / max_weight) for w in weights]
    
    nx.draw_networkx_edges(subgraph, pos, width=edge_widths, alpha=0.3)
    
    # Draw labels
    nx.draw_networkx_labels(subgraph, pos, font_size=8)
    
    plt.title(f'Webex Message Network - Top {top_n} Most Active Rooms', fontsize=16)
    plt.legend()
    plt.axis('off')
    plt.tight_layout()
    
    # Save and show
    output_file = 'webex_graph.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Graph saved to {output_file}")
    plt.show()

def print_statistics(messages, room_counts, person_counts):
    """Print summary statistics"""
    print("\n" + "="*50)
    print("Webex Message Statistics")
    print("="*50)
    print(f"Total messages: {len(messages)}")
    print(f"Unique rooms: {len(room_counts)}")
    print(f"Unique people: {len(person_counts)}")
    
    print(f"\nTop 10 Most Active Rooms:")
    for room, count in sorted(room_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {count:4d} messages - {room}")
    
    print(f"\nTop 10 Most Active People:")
    for person, count in sorted(person_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {count:4d} messages - {person}")

def main():
    print("Loading messages...")
    messages = load_all_messages()
    
    if not messages:
        print("No messages found. Run webex-log.py first to fetch messages.")
        return
    
    print(f"Loaded {len(messages)} messages")
    
    print("Building graph...")
    G, room_counts, person_counts = build_graph(messages)
    
    print_statistics(messages, room_counts, person_counts)
    
    print("\nGenerating visualization...")
    visualize_graph(G, room_counts, person_counts, top_n=20)

if __name__ == '__main__':
    main()
