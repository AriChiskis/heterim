
import pandas as pd
from selenium import webdriver
from selenium_gis import scan_street_side_and_get_coardinates , init_setup
from movement_logic import process_street , save_dataframe
from draw_street import plot_coordinates
import pathlib


def get_random_streets(df, n):
    """
    Selects n random street names from a DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing street names.
    n (int): Number of random street names to select.

    Returns:
    list: A list containing n random street names.
    """
    # Check if n is greater than the number of rows in the DataFrame
    if n > len(df):
        raise ValueError("n is larger than the total number of streets available.")
    
    # Extract n random names
    random_streets = df.sample(n=n).reset_index(drop=True)
    
    # Convert the DataFrame column to a list
    street_list = random_streets['Street Name'].tolist()
    
    return street_list



# Example usage:
# Creating a sample DataFrame

LINK = 'https://gisn.tel-aviv.gov.il/iView2js4/index.aspx'



def format_street_name(street_name):
    # Strip leading/trailing whitespace and split the name
    parts = street_name.strip().split()
    
    # Check if the first word is "רחוב"
    if parts[0] != "רחוב":
        return "רחוב " + street_name
    
    return street_name


def test_street(driver,street,streets_directory,link = LINK):
    try:
                # Define the column names
        columns = ['Number', 'Side', 'Colors', 'Street', 'Type_of_building']
        # Create an empty DataFrame with these columns
        df = pd.DataFrame(columns=columns)

        init_setup(driver=driver , link= link , time_to_wait_to_load=40)
        street_name = format_street_name(street_name = street)
        odd_coar , even_coar = scan_street_side_and_get_coardinates(driver = driver, street=street)

        street_directory = streets_directory / street_name
        plot_coordinates(coordinates1=odd_coar,coordinates2=even_coar,filename=street_directory / pathlib.Path("shape.png"))
        street_directory = streets_directory / street_name
        df = process_street(base_directory=street_directory,global_df=df)
        save_dataframe(file_path=street_directory / pathlib.Path("inquiries.csv"),dataframe=df)


    except ValueError as e:
        print(e)


def test_random_streets(driver,n,df_streets,streets_directory,link = LINK):
        try:

            random_streets_list = get_random_streets(df = df_streets, n = n)
            print(f"the streets are {random_streets_list}")
            init_setup(driver=driver , link=link , time_to_wait_to_load=40)
            print(f"random stret are : {random_streets_list}")
            for street in random_streets_list:
                odd_coar , even_coar = scan_street_side_and_get_coardinates(driver = driver, street=street)
                plot_coordinates(coordinates1=odd_coar,coordinates2=even_coar,filename= streets_directory / street /  pathlib.Path("shape.png"))
                print("finished")
            
            driver.quit()
            columns = ['Number', 'Side', 'Colors', 'Street', 'Type_of_building']
            for street in random_streets_list:
                df = pd.DataFrame(columns=columns)
                street_directory = streets_directory / street
                print(f"proccessing street {street}\n")
                df = process_street(base_directory=street_directory,global_df=df)
                print("\n")

                save_dataframe(ile_path=street_directory / pathlib.Path("inquiries.csv"),dataframe=df)

        except ValueError as e:
            print(e)

if __name__ == "__main__":
    pass

    #test_random_streets(driver=driver,n=1,df_streets=df_streets,link=LINK)



