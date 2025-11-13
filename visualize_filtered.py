#!/usr/bin/env python3
"""
Generate filtered graph visualization with date range support
"""
import sys
from datetime import datetime
from visualize_interactive import load_all_messages, build_graph_data, generate_html
import webbrowser
import os

def filter_messages_by_date(messages, start_date=None, end_date=None):
    """Filter messages by date range"""
    filtered = []
    
    for msg in messages:
        try:
            msg_date = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
            
            if start_date and msg_date < start_date:
                continue
            if end_date and msg_date > end_date:
                continue
                
            filtered.append(msg)
        except:
            continue
    
    return filtered

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate filtered Webex message graph')
    parser.add_argument('--start', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', help='End date (YYYY-MM-DD)')
    parser.add_argument('--last-days', type=int, help='Show last N days')
    parser.add_argument('--output', default='webex_graph_filtered.html', help='Output filename')
    
    args = parser.parse_args()
    
    print("Loading messages...")
    messages = load_all_messages()
    
    if not messages:
        print("No messages found. Run webex-log.py first.")
        return
    
    # Parse date filters
    start_date = None
    end_date = None
    
    if args.last_days:
        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.last_days)
        print(f"Filtering to last {args.last_days} days...")
    else:
        if args.start:
            start_date = datetime.fromisoformat(args.start)
            print(f"Start date: {start_date.date()}")
        if args.end:
            end_date = datetime.fromisoformat(args.end)
            print(f"End date: {end_date.date()}")
    
    # Filter messages
    if start_date or end_date:
        original_count = len(messages)
        messages = filter_messages_by_date(messages, start_date, end_date)
        print(f"Filtered from {original_count} to {len(messages)} messages")
    
    if not messages:
        print("No messages in date range.")
        return
    
    print("Building graph...")
    graph_data = build_graph_data(messages)
    
    print(f"Graph: {len(graph_data['nodes'])} nodes, {len(graph_data['links'])} links")
    print(f"Generating {args.output}...")
    
    html = generate_html(graph_data)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✓ Filtered graph saved to {args.output}")
    
    webbrowser.open(f'file://{os.path.abspath(args.output)}')

if __name__ == '__main__':
    main()
