import os
import csv
import sys
from supabase import create_client, Client

# Batch size for inserts
BATCH_SIZE = 1000

def sync_to_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_KEY environment variables must be set.")
        sys.exit(1)

    supabase: Client = create_client(url, key)

    print("Reading sponsors.csv...")
    sponsors = []
    try:
        with open('sponsors.csv', 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Map CSV columns to Database columns
                sponsors.append({
                    'name': row.get('Organisation Name', '').strip(),
                    'city': row.get('Town/City', '').strip(),
                    'type': row.get('Type & Rating', '').strip(),
                    'route': row.get('Route', '').strip()
                })
    except FileNotFoundError:
        print("Error: sponsors.csv not found.")
        sys.exit(1)

    total = len(sponsors)
    print(f"Found {total} sponsors. Starting upload...")

    # Clear existing data? 
    # Option A: Truncate and replace (Simpler for full sync)
    # Option B: Upsert (Slower, handles IDs)
    # Let's go with Truncate (Delete all) for now to ensure clean state, 
    # or just insert. Since we don't have unique IDs in CSV, full refresh is safest.
    
    # Note: Supabase-py doesn't have a direct truncate, we delete all.
    # But deleting 100k rows might be slow.
    # Let's try to just insert and assume we want fresh data. 
    #Ideally we should use a temp table and swap, but let's keep it simple: Delete All -> Insert.
    
    print("Clearing existing data...")
    # Delete where id > 0 (all rows)
    try:
        supabase.table("sponsors").delete().neq("id", 0).execute()
    except Exception as e:
        print(f"Warning during delete: {e}")

    print("Uploading in batches...")
    for i in range(0, total, BATCH_SIZE):
        batch = sponsors[i:i + BATCH_SIZE]
        try:
            supabase.table("sponsors").insert(batch).execute()
            print(f"Uploaded {min(i + BATCH_SIZE, total)}/{total}")
        except Exception as e:
            print(f"Error uploading batch {i}: {e}")

    print("Sync complete!")

if __name__ == "__main__":
    sync_to_supabase()
