from database_functions import *
from scraper_functions import *
import pandas as pd
import os
import sys
import re


def start_interface():
    """Command line interface for scraping and/or inserting data into parking code database
    Requires user input.
    After typing state and region:  searches for existing .csv
                                    searches for pdf
                                    asks for url to scrape

    URL scrape: scrapes the whole page
                will ask user to identify table number (there will most likely be multiple tables in the html page)
    Uses functions from scraper_functions.py

    Insert into Database:   requires database.ini (holds database credentials)
    Uses functions from database_functions.py

    Returns: None

    """

    print("\n\n\nScraping Parking Requirements | Creating .csv | Inserting into Database\n")
    state = input("Enter state (ex. NY, CA): ")
    region = input("Enter region: ")

    parking_table = []
    filename = f"{region.replace(' ', '_')}_{state}"

    # check if csv file exists for the region, state
    csv_path = os.path.isfile(os.path.join('input_csv', f'{filename}.csv'))
    if csv_path:
        print("Opening .csv")
        parking_table = pd.read_csv(csv_path)
        print(f"Found {filename}.csv")
        if input("Take a look? [y/n]\n>> ") == "y":
            print(parking_table)

        if input("Use this table? [y/n]\n>> ") == "n":
            parking_table = []

    # check if pdf exists for the region, state
    pdf_path = os.path.isfile(os.path.join('pdfs', f'{filename}.pdf'))
    if pdf_path:
        print(f"Found {filename}.pdf")
        user_pages = input("Which pages are the tables located in? (separate by commas no space)\nPages: ")

        parking_table = read_pdf(pdf_path, user_pages.split(','))

        if input("Take a look? [y/n]\n>> ") == "y":
            print(parking_table)
    else:
        print("\nNo pdf found in files.")

    # if csv or pdf doesn't find parking table, run web scraping
    if len(parking_table) == 0:
        print("\n\n[Scrape from site]")
        url = input("Url to scrape: ")

        print("Retrieving HTML...")
        html = get_html(url)
        print("Reading HTML...")
        html_tables = str(parse_table(html)).encode('UTF-8')

        # using read_html to remove superscripts
        tables = pd.read_html(html_tables)  # require lxml & html5lib

        for i, t in enumerate(tables):
            print(f"{i}: {t.columns}")
        table_num = int(input("Which table has the parking requirement? "))

        parking_table = tables[table_num]

    print(f"{parking_table}\nn: {parking_table.shape}\nColumn/Header names: {parking_table.columns}\n")

    print("Parking table loaded.")

    print("""
    Automatic processing will:
        - keep the two leftmost column as 'Use' and 'Number of Spaces'
        - remove any rows with NaN, empty strings, or the same entry (like categories that are one big row)
        - remove duplicates (human error in the original tables)
        - prompt to create csv
        - prompt to insert into database
        """)
    if input("Automatically process the table? [y/n]\n>>") == "y":
        process_automatic(parking_table, filename, region, state)
    else:
        processing_interface_manual(parking_table, filename, region, state)


def process_automatic(parking_table, filename, region, state):
    """Automatically processes parking dataframe based on the most common, "average" raw parking table
    This includes, assuming the two left-most columns are "Use" and "Number of Parking Spaces"
    Removes any rows with NaN, empty strings, or the same entry (like categories that are one big row)
    Removes duplicates
    Will prompt before creating csv and inserting into database
    Funnels into manual processing interface

    Args:
        parking_table: DataFrame of extract parking table only
        filename: {region}_{state}
        region: region without underscores like in filename
        state: state without underscores like in filename

    Returns: None

    """
    parking_table = rename_headers_to_index(parking_table)
    use, spaces = "0", "1"
    parking_table = parking_table[[use, spaces]].replace(r'^s*$', float('NaN'), regex=True).dropna(axis=0)

    # removes rows that have the same name as headers
    parking_table = parking_table[parking_table[use] != use]
    parking_table = parking_table[parking_table[spaces] != spaces]
    parking_table.columns = ["Use", "Number of Spaces"]
    parking_table = parking_table.drop_duplicates(subset="Use")

    print(f"{parking_table}\nn: {parking_table.shape}\nColumn/Header names: {parking_table.columns}\n")

    if input("Create .csv? [y/n]\n>>") == 'y':
        parking_table.to_csv(os.path.join('input_csv', f'{filename}.csv'), index=False)

        if input("Insert into database? [y/n]\n>>") == "y":
            insert_df(parking_table, state, region)
        else:
            sys.exit("Exiting program.")
    else:
        processing_interface_manual(parking_table, filename, region, state)


def processing_interface_manual(parking_table, filename, region, state):
    """Manual data processing interface
    Options include:    1. Rename headers into index
                        2. Remove extra columns and removes categories (also renames columns)
                        3. Remove duplicates (human error in the parking tables)
                        4. Save as .csv

    Main difference to automatic processing is:
            in option 2, user can select which column to select as use and parking spaces
            (in automatic processing, the two left-most is assumed)

    Args:
        parking_table: DataFrame of extract parking table only
        filename: {region}_{state}
        region: region without underscores like in filename
        state: state without underscores like in filename

    Returns: None

    """
    user = ""
    while user != "insert":
        print(f"{parking_table}\nn: {parking_table.shape}\nColumn/Header names: {parking_table.columns}\n")
        user = input(
            """Processing steps:
                1. Rename headers to their indexes
                2. Remove extra columns and removes categories (also renames columns)
                3. Remove duplicates (human error in the parking tables)
                4. Save as .csv
                Enter "insert" to start insertion.
                Enter "exit" to exit.
                >> """)

        if user == "1":
            parking_table = rename_headers_to_index(parking_table)
        elif user == "2":
            use = input("Enter column name to keep for...\nUse: ")
            spaces = input("Number of Spaces: ")

            # returns only use and spaces columns, replaces empty string with NaN, removes any rows with NaN
            parking_table = parking_table[[use, spaces]].replace(r'^s*$', float('NaN'), regex=True).dropna(axis=0)

            # removes rows that have the same name as headers (most common in multi-page tables in pdfs)
            parking_table = parking_table[parking_table[use] != use]
            parking_table = parking_table[parking_table[spaces] != spaces]
            parking_table.columns = ["Use", "Number of Spaces"]
        elif user == "3":
            parking_table = parking_table.drop_duplicates(subset="Use")
        elif user == "4":
            parking_table.to_csv(os.path.join('input_csv', f'{filename}.csv'), index=False)
        elif user == "exit":
            sys.exit("Exiting program.")

    insert_df(parking_table, state, region)


def rename_headers_to_index(df):
    """Renames DataFrame headers to its index

    Args:
        df: DataFrame to modify

    Returns: DataFrame with indexed column headers

    """
    df.columns = [str(i) for i in range(len(df.columns))]
    return df


def remove_beginning_non_alpha(txt):
    """Removes non-alphabetic characters in a string

    Args:
        txt: str

    Returns: str
    """
    match = re.search(r'[a-zA-Z]', txt)
    if match:
        index = match.start()
        return txt[index:]
    else:
        return txt
