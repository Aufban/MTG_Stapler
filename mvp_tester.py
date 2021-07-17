from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
from urllib.request import Request
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import numpy as np
import os

#TODO add scryfall API
#TODO add card type_line
#TODO add color_identity
