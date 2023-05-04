# Parking Requirement Database
*(for database credentials: place database.ini file into repo directory on your machine)*

Currently:
 + web-scraping
 + ORM database management
 + PostgreSQL database
 + currently hosted by Supabase

Future development:
 + NLP
 + web-crawling

# Installing conda environment
1. Open Anaconda Prompt
2. Create conda environment from environment.yml: has all the necessary libraries and packages
   (including ipykernel)
   ```
   (base) > conda env create -f environment.yml
   ```
   NOTE: environment.yml will need to be updated if we need to use more packages
3. Main packages:
    - SQLAlchemy 2.0
    - Selenium
    - Beautiful Soup 4
    - ipykernel
    - lxml
    - html5lib
    - pandas, numpy
   

# Extra installation step for Jupyter Notebook
1. Open Anaconda Prompt
2. Install nb_conda_kernels: allows you to access conda environments in Jupyter Notebook
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
