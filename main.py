import pandas as pd
from scraper_functions import *
from database_functions import *
import os

# WEB-SCRAPER

# INSERT INTO OBJECT

# INSERT INTO DB

# connect()


def create_csv_url(state, region, url="", table_num=0):

    region_file = region.replace(' ', '_')

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
    while user != "exit":
        print(f"{parking_table}\nn: {parking_table.shape}\nColumn names: {parking_table.columns}\n")
        user = input(
            """Processing steps:
                1. Remove extra headers
                2. Remove extra columns and removes categories 
                3. Rename columns to "Use" and "Number of Spaces" (only use with 2 columns)
                4. Remove duplicates
                5. Save as .csv
                Enter "exit" to leave and start insertion.
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

    insert_df(parking_table, state, region)


def remove_extra_header(df):
    col = len(df.columns) - 1
    df.columns = [headers[col] for headers in list(df)]
    return df


def remove_extra_column(df, use, spaces):
    # Remove categories like "Commercial"
    filtered = df[[use, spaces]]
    return filtered


def insert_csv():
    test = pd.read_csv(r'input_csv\Los_Angeles_County_CA.csv')
    use = "Use.1"
    spaces = "Number of Spaces"
    # Remove categories like "Commercial"
    # filtered = test[test[use] != test[spaces]].dropna(axis=1)
    filtered = test[[use, spaces]]
    filtered.columns = ["Use", "Number of Spaces"]
    print(filtered)
    # insert_df(filtered)


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 160)
pd.set_option('display.max_rows', None)
st = "IL"
reg = "Franklin Park"
table_number = 1
municode = "https://library.municode.com/il/franklin_park/codes/code_of_ordinances?nodeId=CO_TIT9ZOOR_CH11OREPALO_9-11-5REOREVEPASP"

# test_connection()
create_csv_url("IL", "Winnebago County")
# create_csv_url(st, reg, municode, table_number)
# read_database()

