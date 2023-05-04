from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import pandas as pd
import time



def get_html(url, driver_path=r"C:\Users\tungl\Downloads\chromedriver_win32\chromedriver"):
    '''Get the html of a webpage. You need to have a Chrome driver
       installed in order to execute this function.

    Args:
        url: url of the website (str)
        driver_path: driver path of the Chrome Driver (str)

    Return:
        html: HTML of the rendered website (str)
    '''

    # Create a headless webdriver instance and interact with the website
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(driver_path, options=options)
    driver.get(url)

    # Give some time for the browser to render and load the data
    time.sleep(5)

    # Getting the HTML of this page
    html = driver.page_source

    # Close the webdriver
    driver.quit()

    return html


def parse_table(html):
    '''Parse the HTML to extract tables.

    Arg:
        html: HTML of the rendered website (str)
    Return:
        tables: a list of parsed table HTML (list)
    '''

    # using BeautifulSoup to parse the HTML and find all the tables
    soup = BeautifulSoup(html, "html.parser")
    for sup in soup.select('sup'):
        sup.extract()

    return soup



