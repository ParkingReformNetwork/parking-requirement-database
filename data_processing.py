from database_functions import *
from scraper_functions import *
import pandas as pd
import os
import sys


def create_csv_url(state, region, url="", table_num=0):

    region_file = region.replace(' ', '_')

    # check if csv file exists for the region, state
    if os.path.isfile(rf"input_csv/{region_file}_{state}.csv"):
        print("Opening .csv")
        parking_table = pd.read_csv(rf"input_csv/{region_file}_{state}.csv")

    else:
        if url == "":
            raise Exception("No .csv or url")

        print("Retrieving HTML...")
        html = get_html(url)
        print("Reading HTML...")

        html_tables = str(parse_table(html)).encode('UTF-8')
        # using read_html to remove superscripts
        tables = pd.read_html(html_tables)  # require lxml & html5lib
        parking_table = tables[table_num]
        parking_table.to_csv(rf'input_csv\{region_file}_{state}.csv', index=False)

    user = ""
    while user != "insert":
        print(f"{parking_table}\nn: {parking_table.shape}\nColumn names: {parking_table.columns}\n")
        user = input(
            """Processing steps:
                1. Remove extra headers
                2. Remove extra columns and removes categories 
                3. Rename columns to "Use" and "Number of Spaces" (only use with 2 columns)
                4. Remove duplicates
                5. Save as .csv
                Enter "insert" to start insertion.
                Enter "exit" to exit.
                >> """)

        if user == "1":
            parking_table = remove_extra_header(parking_table)
        elif user == "2":
            use = input("Enter column name to keep for...\nUse: ")
            spaces = input("Number of Spaces: ")
            parking_table = parking_table[[use, spaces]]
        elif user == "3":
            parking_table.columns = ["Use", "Number of Spaces"]
        elif user == "4":
            parking_table = parking_table.drop_duplicates(subset="Use")
        elif user == "5":
            parking_table.to_csv(rf'input_csv\{region_file}_{state}.csv', index=False)
        elif user == "exit":
            sys.exit("Exiting program.")

    insert_df(parking_table, state, region)


def remove_extra_header(df):
    col = len(df.columns) - 1
    df.columns = [headers[col] for headers in list(df)]
    return df


def remove_extra_column(df, use, spaces):
    # Remove categories like "Commercial"
    filtered = df[[use, spaces]]
    filtered = filtered[filtered[use] != filtered[spaces]]
    return filtered