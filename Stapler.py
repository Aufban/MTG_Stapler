from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
from urllib.request import Request
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import numpy as np
import os
import re

myurl =  'https://cedh-decklist-database.com'
cards = [] # initializes list of all cards

#Getting list of decklists
client = uReq(myurl) # opening connection 
page_html = client.read() # content to variable
client.close() # closes connection 
page_soup = soup(page_html, 'html.parser') # html parsing 
containers = page_soup.findAll("div",{"class": "ddb-section"})
htmls = []
for c in containers:
    if c.get_text().strip() == 'COMPETITIVE':
        x = c.parent.parent.find("ul", {"class": "ddb-decklists"})
        htmls.append(x.a["href"])

#TODO: Change to regular expression
#cleaning moxfield primer lists
htmls = list(map(lambda x: x.split('/primer')[0],htmls))

# Scrapper of decklists
chromedriver_path=os.path.join(os.getcwd(), "chromedriver.exe")
options = Options()
options.set_headless(headless=True)
for decklist in htmls:
    if 'moxfield' in decklist: # checks if its a moxfield deck
        driver = webdriver.Chrome(chromedriver_path, options= options)
        driver.get(decklist)
        time.sleep(3) #if you want to wait 3 seconds for the page to load
        page_source = driver.page_source
        driver.close()
        page_soup = soup(page_source, 'html.parser')
        containers = page_soup.findAll("tr",{"class": "table-deck-row"})
        for c in containers:
            cards.append( c.a.get_text())
        cards = cards[:len(cards)-8]

card_data = pd.DataFrame({'Card Name': cards}) # creates a data frame of all cards
card_vc = pd.DataFrame(card_data.value_counts())
card_vc.rename( columns={0 :'Occurrences'}, inplace=True ) # sets coorrect column names
card_vc = card_vc.reset_index()
card_vc.to_json('results/competitiveCards.json', orient='records')
card_vc.to_csv('results/competitive_cards.csv')

