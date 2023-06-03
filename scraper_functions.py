from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# for reading pdfs
import camelot
# import ghostscript
import tkinter
import pandas as pd

import time
import os


def get_html(url, driver_path=r"C:\Users\tungl\Downloads\chromedriver_win32\chromedriver"):
    """Get the html of a webpage. You need to have a Chrome driver
       installed in order to execute this function.

    Args:
        url: url of the website (str)
        driver_path: driver path of the Chrome Driver (str)

    Return:
        html: HTML of the rendered website (str)
    """

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
    """Parse the HTML to extract tables.
    HTML processing occurs here including: removing superscripts

    Arg:
        html: HTML of the rendered website (str)
    Return:
        tables: a list of parsed table HTML (list)
    """

    # using BeautifulSoup to parse the HTML and find all the tables
    soup = BeautifulSoup(html, "html.parser")

    # remove superscripts in html
    for sup in soup.select('sup'):
        sup.extract()

    return soup


# read pdfs
def read_pdf(pdf_file, page_numbers):
    tables = camelot.read_pdf(os.path.join('pdfs', pdf_file), pages=",".join(str(x) for x in page_numbers))
    print("Total tables extracted:", tables.n)
    all_tables = pd.DataFrame()
    for table in tables:
        table = table.df.replace('\n', ' ', regex=True)
        all_tables = pd.concat([all_tables, table])

    all_tables.columns = all_tables.iloc[0]
    all_tables = all_tables[1:]

    return all_tables


def url_text_to_table(url, section_name, separator):
    '''Parse the html to and find all the bullet point parking requiremnets
    Args:
        url: url of the webpage
        section_name: the section name that contains the bullet point requirements
        separator: separator of use and parking 
    Return:
        pandas DataFrame
    '''
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("div", text = section_name)
    section = title.find_parent("li")
    
    # finding the smallest content
    raw_contents = section.find_all('p', class_ = lambda value: value and value.startswith("content"))
    uniq_names = set(' '.join(content['class']) for content in raw_contents)
    uniq_ints = []
    for name in uniq_names:
        uniq_ints.append(int(name[-1]))
    wanted_class = f"content{max(uniq_ints)}"
    wanted_contents = section.find_all('p', class_ = wanted_class)
    requirement_dicts = []
    for requirement in wanted_contents:
        # need to find a way to separate properly
        # might run into the problem of "Single-family dwelling—Two spaces."
        info = requirement.text.replace("\n", "").split(separator,1)
        requirement_dicts.append({"Use": info[0], 
                                  "Number of Spaces": info[1]})
    
    return pd.DataFrame(requirement_dicts)
