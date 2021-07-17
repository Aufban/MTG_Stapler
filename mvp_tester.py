import requests
import time
import pandas as pd
from tqdm import tqdm

def get_card_info(card_name):
    time.sleep(0.1)
    uri = 'https://api.scryfall.com/cards/named?exact='+card_name
    response = requests.get(uri)
    json_response = response.json()
    return json_response

df = pd.read_json('results/competitiveCards_full.json')
df['Type'] = 'Not Found'
df['Color Identity'] = 'Not Found'
df['USD'] = 'Not Found'
for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
    card_info = get_card_info(row['Card Name'])
    df.at[idx,'Type'] = card_info.get('type_line')
    df.at[idx,'Color Identity'] = card_info.get('color_identity')
    df.at[idx,'USD'] = card_info.get('prices').get('usd')
df.to_json('results/competitiveCards_full_scry.json', orient='records')
