import os
import math
import requests
import json
from PIL import Image

sport_dir = "/path/to/logo/directory"

with open("/path/to/ncaa.json", "r") as f:
    ncaa = json.load(f)
    
for team, id in ncaa.items():	
	# Set the URL for the JSON file for the current league
	url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams/{id}"
    
	# Fetch the JSON data
	response = requests.get(url)
	data = response.json()
    
	abbreviation = data['team']['abbreviation']
	logo_url = data['team']['logos'][0]['href']
    
	print(f"Downloading logo for {abbreviation} from ncaa...")
    
	img_path_png = os.path.join(sport_dir, f"{abbreviation}.png")
	response = requests.get(logo_url, stream=True)
    
	with open(img_path_png, 'wb') as file:
		for chunk in response.iter_content(chunk_size=1024):
			file.write(chunk)
            