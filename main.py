import pathlib
import pandas as pd

from selenium import webdriver
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'code')))


LINK = 'https://gisn.tel-aviv.gov.il/iView2js4/index.aspx'
street_name_dir = "streets_names"
street_names_dir_path = pathlib.Path(street_name_dir)
streets_data_dir = "streets_data"
streets_data_dir_path = pathlib.Path(streets_data_dir)



from test import test_street , test_random_streets

STREET_NAME = 0
RANDOM = 1

STREET_NAME ="choose your street"
NUM_OF_STREETS = 2
DESICION = STREET_NAME


if __name__ == "__main__":
    driver = webdriver.Chrome()
    if (DESICION == STREET_NAME):
        test_street(driver=driver,street=STREET_NAME,streets_directory=streets_data_dir_path,link=LINK)
    
    else:
        df_streets = pd.read_csv((street_names_dir_path / "street_names.csv"))
        test_random_streets(driver=driver,n=NUM_OF_STREETS,df_streets=df_streets,streets_directory=streets_data_dir_path,link=LINK)

