import requests
import os
import sys
import urllib3
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("="*50)
print("Webex Message Logger")
print("="*50)

# Test config import
print("\n[1/5] Loading configuration...")
try:
    from config import access_token, your_email
    print(f"  ✓ Token loaded (length: {len(access_token)})")
    print(f"  ✓ Email: {your_email}")
except ImportError as e:
    print(f"  ✗ Error: config.py not found")
    print(f"  Create config.py with access_token and your_email")
    sys.exit(1)
except Exception as e:
    print(f"  ✗ Error loading config: {e}")
    sys.exit(1)

headers = {
    'Authorization': f'Bearer {access_token}'
}

# Test API connection
print("\n[2/5] Testing Webex API connection...")
test_url = 'https://webexapis.com/v1/people/me'
try:
    test_response = requests.get(test_url, headers=headers, timeout=10, verify=False)
    if test_response.status_code == 200:
        user_data = test_response.json()
        print(f"  ✓ Connected as: {user_data.get('displayName', 'Unknown')}")
    elif test_response.status_code == 401:
        print(f"  ✗ Authentication failed - token may be expired")
        sys.exit(1)
    else:
        print(f"  ✗ API returned status {test_response.status_code}")
        sys.exit(1)
except requests.exceptions.Timeout:
    print(f"  ✗ Connection timeout")
    sys.exit(1)
except Exception as e:
    print(f"  ✗ Connection error: {e}")
    sys.exit(1)

# Step 1: Get all rooms you're in
print("\n[3/5] Fetching rooms...")
room_url = 'https://webexapis.com/v1/rooms'
try:
    rooms_response = requests.get(room_url, headers=headers, verify=False)
    rooms_response.raise_for_status()
    rooms = rooms_response.json().get('items', [])
    print(f"  ✓ Found {len(rooms)} rooms")
except Exception as e:
    print(f"  ✗ Error fetching rooms: {e}")
    sys.exit(1)

# Step 2: Loop through each room and collect all messages
print("\n[4/5] Downloading messages...")
all_messages = []

for idx, room in enumerate(rooms, 1):
    room_id = room['id']
    room_title = room.get('title', 'No Title')
    print(f"  [{idx}/{len(rooms)}] {room_title}", end='', flush=True)
    url = 'https://webexapis.com/v1/messages'
    params = {
        'roomId': room_id,
        'max': 200
    }
    room_msg_count = 0

    while url:
        response = requests.get(url, headers=headers, params=params, verify=False)
        response.raise_for_status()
        messages = response.json().get('items', [])
        room_msg_count += len(messages)

        for msg in messages:
            msg['roomTitle'] = room_title
            sender = msg.get('personEmail', '')
            mentioned = your_email in msg.get('mentionedPeople', [])
            if sender == your_email:
                msg['involvement'] = 'sender'
            elif mentioned:
                msg['involvement'] = 'mentioned'
            else:
                msg['involvement'] = 'participant'
            all_messages.append(msg)

        # Handle pagination
        link_header = response.headers.get('Link', '')
        next_url = None
        for link in link_header.split(','):
            if 'rel="next"' in link:
                next_url = link[link.find('<') + 1:link.find('>')]
                break
        url = next_url
        params = {}  # Clear for pagination
    
    print(f" - {room_msg_count} messages")

# Step 3: Group messages by date
print(f"\n[5/5] Saving {len(all_messages)} messages...")
messages_by_day = {}
for message in all_messages:
    if 'created' in message:
        date = message['created'][:10]  # YYYY-MM-DD
        if date not in messages_by_day:
            messages_by_day[date] = []
        messages_by_day[date].append(message)

# Step 4: Save to per-day files
output_dir = 'webex_messages_by_day'
os.makedirs(output_dir, exist_ok=True)

for date, messages in messages_by_day.items():
    file_path = os.path.join(output_dir, f'{date}.txt')
    with open(file_path, 'w', encoding='utf-8') as f:
        for msg in messages:
            created = msg.get('created', 'UNKNOWN_TIME')
            text = msg.get('text', '[No text]')
            sender = msg.get('personEmail', 'UNKNOWN_SENDER')
            room_title = msg.get('roomTitle', 'UNKNOWN_ROOM')
            involvement = msg.get('involvement', 'participant')
            f.write(f"[{created}] ({room_title}) {sender} [{involvement}]: {text}\n")

print(f"  ✓ Created {len(messages_by_day)} daily log files in {output_dir}/")
print(f"\n{'='*50}")
print(f"✓ Complete! {len(all_messages)} messages saved.")
print(f"{'='*50}")

