import csv
import json
from datetime import datetime

def process_sponsors():
    sponsors = []
    try:
        with open('sponsors.csv', 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sponsors.append({
                    'name': row.get('Organisation Name', ''),
                    'city': row.get('Town/City', ''),
                    'type': row.get('Type & Rating', ''),
                    'route': row.get('Route', '')
                })
        
        # Save to JSON
        with open('sponsors.json', 'w', encoding='utf-8') as f:
            json.dump(sponsors, f)
        
        # Update metadata with current date
        metadata = {
            'last_updated': datetime.now().strftime('%d %B %Y')
        }
        with open('metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f)
            
        print(f"Successfully processed {len(sponsors)} sponsors.")
        print(f"Updated metadata: {metadata['last_updated']}")
        
    except Exception as e:
        print(f"Error processing sponsors: {e}")

if __name__ == "__main__":
    process_sponsors()

