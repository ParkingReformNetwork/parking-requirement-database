# Parking Requirement Database
*(for [database credentials](https://drive.google.com/file/d/1Lm7Akt0x7dssgo-t79D83HJ5eb1Kokuu/view?usp=sharing): place database.ini file into repo directory on your machine)*

Current development:
 + web scraping/crawling
 + ORM database management
 + PostgreSQL database
 + currently hosted by Supabase
 + [Wiki documentation](https://github.com/ParkingReformNetwork/parking-requirement-database/wiki)

Future development:
 + NLP
 + Website
 + Aggregation and other data analysis

## For Windows users:
Due to the use of scrapy-playwright (loading js elements when using scrapy), we recommend installing WSL/Ubuntu to run the scrapy spider. 

However, you may want to still have a conda environment on your Windows environment for quick debugging
and development through your IDE (ex. VSCode, PyCharm, etc).

Other utilities to consider include [this](https://superuser.com/questions/1262977/open-browser-in-host-system-from-windows-subsystem-for-linux) for commands like view(response) in scrapy shell. 

There may be more dependencies to install including:
- playwright install-deps
- etc

# Installing conda environment
1. Open Anaconda Prompt
2. Create conda environment from environment.yml: has all the necessary libraries and packages
   (including ipykernel)
   ```
   (base) > conda env create -f environment-[os].yml
   ```
   NOTE: environment.yml will need to be updated if we need to use more packages
3. Main packages:
    - SQLAlchemy 2.0
    - Camelot
    - Selenium
    - Beautiful Soup 4
    - ipykernel
    - lxml
    - html5lib
    - pandas, numpy
    - scrapy
    - scrapy-playwright
4. Use the following command to update environmental.yml
   ```
      conda env export > environment.yml
   ```
   
# Web scraping/crawling
*(currently trying to migrate from selenium/bs4 into scrapy)*
1. In the web_crawling folder (has settings.py and a folder called web_crawling)
   ```commandline
   scrapy crawl munispider
   ```
2. Check out the [wiki](https://github.com/ParkingReformNetwork/parking-requirement-database/wiki) for updated information

# Extra installation step for Jupyter Notebook
1. Open Anaconda Prompt
2. Install nb_conda_kernels in base environment: allows you to access conda environments in Jupyter Notebook
   (as long as ipykernel is installed)
    ```
   (base) > conda install nb_conda_kernels
   ```
3. When running .ipynb, switch kernel to "Python [conda env: db_env]"
4. A quick test to make sure the environment/kernel is working.
    ``` 
    import sqlalchemy
    sqlalchemy.__version__
   >> '2.0.12'
   ```


### Inserting into database
0. Download [Chrome driver](https://chromedriver.chromium.org/downloads). Change path of chrome driver in get_html() in scraper_functions.py.
1. Main function is create_csv_url() in data_processing.py
   ```
   from data_processing import *
   create_csv_url("CA", "Los Angeles County", [insert url], [insert table number])   # web-scrape
   create_csv_url("CA", "Los Angeles County")   # if csv exists
   ```
2. Follow prompts

### Reading database
1. Main function is read_database() in database_functions.py
   ```
   from database_functions import *
   read_database()
   ```
2. Follow prompts

### Reading pdfs
1. Main function is read_pdf() in scraper_functions.py
2. Install Ghostscript via your OS [here](https://camelot-py.readthedocs.io/en/master/user/install-deps.html)
3. Run function with parameters

