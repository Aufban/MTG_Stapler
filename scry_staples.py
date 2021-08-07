import requests
import time
import pandas as pd
import re
from tqdm import tqdm


def get_card_info(card_name):
    """Queries ScryFall to get // cards"""
    time.sleep(0.2)
    uri = 'https://api.scryfall.com/cards/named?fuzzy='+card_name
    response = requests.get(uri)
    json_response = response.json()
    return json_response


scry = pd.read_json('results/scryfall_oracle.json')
scry = scry[scry['multiverse_ids'].str.len() != 0]

def second_group(m):
    """Function to catch the first capture group in regex"""
    return m.group(1)


scry_cols = ['name', 'color_identity', 'type_line', 'reserved' , 'prices', 'mana_cost']

cedh = pd.read_json('results/competitiveCards_full.json')

cedh_scry = pd.merge(cedh,scry[scry_cols], how='left', left_on='Card Name', right_on='name', indicator=True)

for idx, row in tqdm(cedh_scry[cedh_scry['_merge']=='left_only'].iterrows(), total=cedh_scry[cedh_scry['_merge']=='left_only'].shape[0]):
    card_info = get_card_info(row['Card Name'])
    cedh_scry.at[idx,'type_line'] = card_info.get('type_line')
    cedh_scry.at[idx,'name'] = card_info.get('name')
    cedh_scry.at[idx,'color_identity'] = card_info.get('color_identity')
    cedh_scry.at[idx,'prices'] = card_info.get('prices')
    cedh_scry.at[idx,'reserved'] = card_info.get('reserved')
    cedh_scry.at[idx,'mana_cost'] = card_info.get('mana_cost')

def type_cleaner(x):
    if '//' in x:
        x = x.split('//')[0]
    if '—' in x:
        x = x.split('—')[0]
    if 'Creature' in x:
        return 'Creature'
    elif 'Land' in x:
        return 'Land'
    elif 'Planeswalker' in x:
        return 'Planeswalker'
    elif 'Artifact' in x:
        return 'Artifact'
    elif 'Enchantment' in x:
        return 'Enchantment'
    elif 'Instant' in x:
        return 'Instant'
    elif 'Sorcery' in  x:
        return 'Sorcery'
    else:
        return 'Unknown'

cedh_scry['type'] = cedh_scry['type_line'].apply(type_cleaner)
cedh_scry['color_identity'] = cedh_scry['color_identity'].apply(lambda x: ''.join([str(i) for i in x]))
cedh_scry['color_identity'].replace('', 'C', inplace=True)

#FIXME: Correct for legalities in commander
cedh_scry.rename(columns={
    'Card Name': 'scrapName',
    'Title':'deckNames',
    'Link': 'deckLinks',
    'Ocurrences':'occurrences',
    'name': 'cardName',
    'color_identity': 'colorIdentity',
    'type_line': 'typeLine',
    'reserved': 'reserved',
    'prices': 'prices',
    'mana_cost': 'manaCost',
    'type':'type',
    '_merge': 'mergedSource'
}, inplace=True)

cedh_scry.to_json('results/cedh_scry.json', orient='records')
