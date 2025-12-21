import unicodedata
import requests
import os

base_url = "https://api.the-odds-api.com"

def get_json(path):
    url = base_url + path
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        print(url)
        return None
    
def normalize_name(name):
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.lower()
    return name

def cleanup_old_headshots(current_player_ids, folder="player_headshots"):
    # List all files in the folder
    for filename in os.listdir(folder):
        if filename.endswith(".png"):
            # Extract player_id from filename
            player_id = int(filename.replace(".png", ""))
            if player_id not in current_player_ids:
                # Delete the old headshot
                filepath = os.path.join(folder, filename)
                os.remove(filepath)
                print(f"Deleted old headshot: {filename}")
