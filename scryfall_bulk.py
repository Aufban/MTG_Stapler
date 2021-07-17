import requests
import time
import pandas as pd
from tqdm import tqdm
uri = 'https://api.scryfall.com/bulk-data/oracle-cards'
response = requests.get(uri).json()

download_uri = response.get('download_uri')
response_download = requests.get(download_uri, allow_redirects=True)
data = response_download.content
with open('results/scryfall_oracle.json', 'wb') as f:
    f.write(data)
