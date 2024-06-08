import pandas as pd
from simpledbf import Dbf5

def dbf_to_excel(dbf_path, excel_path):
    dbf = Dbf5(dbf_path)
    df = dbf.to_dataframe()
    df.to_excel(excel_path, index=False)

# Replace 'path_to_your_dbf_file.dbf' with the path to your DBF file
# Replace 'output_excel_file.xlsx' with the path where you want to save the Excel file
dbf_to_excel('Addresses.dbf', 'Addresses.xlsx')
