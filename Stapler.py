from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,TimeoutException
import pandas as pd
import re
import os
from tqdm import tqdm

cedh_database =  'https://cedh-decklist-database.com'
#Getting list of decklists
client = uReq(cedh_database) # opening connection
page_html = client.read() # content to variable
client.close() # closes connection
page_soup = soup(page_html, 'html.parser') # html parsing
containers = page_soup.findAll("div",{"class": "ddb-section"})
htmls = []
for c in containers:
    if c.get_text().strip() == 'COMPETITIVE':
        x = c.parent.parent.find("ul", {"class": "ddb-decklists"})
        lis = x.findAll('li')
        for li in lis:
            htmls.append(li.a["href"])

#cleaning moxfield primer lists
def second_group(m):
    return m.group(1)
htmls = list(map(lambda x: re.sub(r'(.*)/$|(.*)/primer$',second_group,x ), htmls))

# Scrapper of decklists
cards = [] # initializes list of all cards
chromedriver_path=os.path.join(os.getcwd(), "chromedriver.exe")
options = Options()
options.headless = True
options.add_experimental_option('excludeSwitches', ['enable-logging']) #remove logging message
driver = webdriver.Chrome(executable_path=chromedriver_path, options= options)
for decklist in tqdm(htmls):
    if 'moxfield' in decklist:
        driver.get(decklist)
        try:
            myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'viewMode')))
        except TimeoutException:
            print ("Loading took too much time!",decklist)
            continue
        view_mode = driver.find_element_by_id('viewMode')
        mode = view_mode.get_attribute('value')
        page_source = driver.page_source
        page_soup = soup(page_source, 'html.parser')
        title = page_soup.find("span", {"class": "deckheader-name"}).get_text()
        deck_info = {'Link': decklist, 'Title':title }
        if mode == 'table':
            containers = page_soup.findAll("tr",{"class": "table-deck-row"})
            deck_cards = []
            #TODO: Find only decklist cards
            for c in containers:
                c_name = {'Card Name': c.a.get_text()}
                deck_cards.append(c_name)
            deck_info['Cards'] = deck_cards
            cards.append(deck_info)
        elif mode == 'visual':
            containers = page_soup.findAll("div",{"class": "decklist-card-phantomsearch"})
            deck_cards = []
            #TODO: Find only decklist cards
            for c in containers:
                c_name = {'Card Name': c.get_text()}
                deck_cards.append(c_name)
            deck_info['Cards'] = deck_cards
            cards.append(deck_info)
        elif mode == 'stacks':
            containers = page_soup.findAll("div",{"class": "img-card-stack"})
            deck_cards = []
            #TODO: Find only decklist cards
            for c in containers:
                c_name = {'Card Name': c.img['alt']}
                deck_cards.append(c_name)
            deck_info['Cards'] = deck_cards
            cards.append(deck_info)
driver.close()
#dataframe with all cards
df = pd.json_normalize(cards,
    record_path='Cards', meta=['Link', 'Title'])
df = df.drop_duplicates()
#convert dataframe of decklists with cards to a dataframe of cards with decklists
df_1 = df.groupby('Card Name')['Title'].apply(list).reset_index()
df_2 = df.groupby('Card Name')['Link'].apply(list).reset_index()
df_12 = pd.merge(df_1, df_2, on='Card Name', how='inner')

card_vc = df['Card Name'].value_counts()
card_vc = card_vc.reset_index()
card_vc.rename( columns={'index' :'Card Name', 'Card Name':'Occurrences'}, inplace=True )#columns names

full_cards = pd.merge(df_12,card_vc, on = 'Card Name')

#Exports
# card_vc.to_json('results/competitiveCards.json', orient='records')
# card_vc.to_csv('results/competitive_cards.csv')
full_cards.to_json('results/competitiveCards_full.json', orient='records')

