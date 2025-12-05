import requests
from bs4 import BeautifulSoup
import csv
import json
import os

# Constants
GOV_URL = "https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers"
CSV_FILENAME = "sponsors.csv"
JSON_FILENAME = "sponsors.json"

def download_sponsors():
    print("Fetching GOV.UK page...")
    try:
        response = requests.get(GOV_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the CSV link
        # Look for a link that ends with .csv
        csv_link = None
        for a in soup.find_all('a', href=True):
            if a['href'].lower().endswith('.csv'):
                csv_link = a['href']
                break
        
        if not csv_link:
            print("Error: Could not find CSV link on the page.")
            return False
            
        print(f"Found CSV link: {csv_link}")
        
        # Download the CSV
        print("Downloading CSV...")
        csv_response = requests.get(csv_link)
        csv_response.raise_for_status()
        
        with open(CSV_FILENAME, 'wb') as f:
            f.write(csv_response.content)
            
        print(f"Saved to {CSV_FILENAME}")
        return True
        
    except Exception as e:
        print(f"Error downloading sponsors: {e}")
        return False

def process_sponsors():
    print("Processing CSV to JSON...")
    sponsors = []
    try:
        if not os.path.exists(CSV_FILENAME):
            print(f"Error: {CSV_FILENAME} not found.")
            return False

        with open(CSV_FILENAME, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sponsors.append({
                    'name': row.get('Organisation Name', ''),
                    'city': row.get('Town/City', ''),
                    'type': row.get('Type & Rating', ''),
                    'route': row.get('Route', '')
                })
        
        # Save to JSON
        with open(JSON_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(sponsors, f)
            
        print(f"Successfully processed {len(sponsors)} sponsors to {JSON_FILENAME}.")

        # Save Metadata
        from datetime import datetime
        metadata = {
            "last_updated": datetime.now().strftime("%d %B %Y")
        }
        with open("metadata.json", "w", encoding='utf-8') as f:
            json.dump(metadata, f)
        print(f"Updated metadata.json with date: {metadata['last_updated']}")

        return True
        
    except Exception as e:
        print(f"Error processing sponsors: {e}")
        return False

if __name__ == "__main__":
    if download_sponsors():
        process_sponsors()
