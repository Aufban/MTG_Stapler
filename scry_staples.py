import requests
import time
import pandas as pd
from tqdm import tqdm


def get_card_info(card_name):
    time.sleep(0.2)
    uri = 'https://api.scryfall.com/cards/named?fuzzy='+card_name
    response = requests.get(uri)
    json_response = response.json()
    return json_response


scry = pd.read_json('results/scryfall_oracle.json')
scry_cols = ['name', 'color_identity', 'type_line', 'reserved' , 'prices' ]
cedh = pd.read_json('results/competitiveCards_full.json')

cedh_scry = pd.merge(cedh,scry[scry_cols], how='left', left_on='Card Name', right_on='name', indicator=True)

for idx, row in tqdm(cedh_scry[cedh_scry['_merge']=='left_only'].iterrows(), total=cedh_scry[cedh_scry['_merge']=='left_only'].shape[0]):
    card_info = get_card_info(row['Card Name'])
    cedh_scry.at[idx,'type_line'] = card_info.get('type_line')
    cedh_scry.at[idx,'name'] = card_info.get('name')
    cedh_scry.at[idx,'color_identity'] = card_info.get('color_identity')
    cedh_scry.at[idx,'prices'] = card_info.get('prices')
    cedh_scry.at[idx,'reserved'] = card_info.get('reserved')

cedh_scry.rename({
    'Card Name': 'scrapName',
    'Title':'deckNames',
    'Link': 'deckLinks',
    'Ocurrences':'occurrences',
    'name': 'cardName',
    'color_identity': 'colorIdentity',
    'type_line': 'typeLine',
    'reserved': 'reserved',
    'prices': 'prices',
    '_merge': 'mergedSource'
})
cedh_scry.to_json('results/cedh_scry.json', orient='records')
