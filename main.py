import color_analysis
import selenium_gis
import time
import draw_street

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from time import sleep
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import os
import pandas as pd
import re
from PIL import Image, ImageDraw

if __name__ == "__main__":
    banana_color = (253, 220, 151)
    banana_2 = (253, 220, 151)
    black_map_color = (36, 38, 40)
    purple_map_color = (209, 147, 253)
    pink_flower_color = (253, 146, 149)
    red_flower_color = (253, 70, 77)

    orange_map_color = (253, 118, 21)
    brown_road_on_orange = (125, 71, 25)
    light_road_on_orange = (197, 121, 37)
    semi_dark_road_on_orange = (145, 78, 24)

    light_yellow = (254, 254, 152) 
    dark_road_on_light_yellow = (73, 82, 51)
    mid_dark_road_on_light_yellow = (164, 166, 107)
    semi_dark_road_on_light_yellow = (108, 113, 74)

    brown = (164, 81, 57)
    dark_brown_road = (102, 65, 55)
    light_brown_road = (133, 87, 73)

    light_green = (90, 210, 20)
    dark_green = (25, 63, 26)
    kaki_green = (152, 143, 37)

    dark_blue = (49, 65, 175)

    very_dark_brown = (56, 24, 23)

    yellow = (254, 254, 25)
    yellow_2 = (252, 253, 18)
    mustard_road_on_yellow = (89, 93, 23)
    semi_road_on_yellow = (230, 235, 58)
    colors_to_avoid = [banana_2,banana_color,
                   black_map_color , 
                   brown_road_on_orange,light_road_on_orange ,semi_dark_road_on_orange , 
                   dark_road_on_light_yellow , mid_dark_road_on_light_yellow , semi_dark_road_on_light_yellow ,
                    dark_brown_road , light_brown_road ,
                     light_green , dark_green , kaki_green ,
                       dark_blue , 
                       very_dark_brown , 
                       yellow , yellow_2 , 
                       mustard_road_on_yellow , semi_road_on_yellow
                    ]



    dataset_colors = [banana_color,banana_2 ,
                  black_map_color , 
                  purple_map_color,
                  pink_flower_color,
                  red_flower_color,
                  orange_map_color,
                  brown_road_on_orange,
                  light_road_on_orange,semi_dark_road_on_orange ,
                  light_yellow ,
                  dark_road_on_light_yellow , mid_dark_road_on_light_yellow , semi_dark_road_on_light_yellow , 
                  brown , 
                  dark_brown_road , light_brown_road , 
                  light_green , dark_green , kaki_green , 
                  dark_blue , 
                  very_dark_brown , 
                  yellow , yellow_2 , 
                  mustard_road_on_yellow , semi_road_on_yellow
                  ]

    sleep_time = 0.2
    # Setup the ChromeDriver
    driver = webdriver.Chrome()
    df_addresses = pd.read_csv('addresses.csv')
    link = 'https://gisn.tel-aviv.gov.il/iView2js4/index.aspx'
    driver = webdriver.Chrome()
    result = []
    image_path = 'screenshot.png'
    try:
        # Open the web page
        driver.get(link)
        time.sleep(20) # let it the page load all the stuff (it is very very slow at the start)
        print("finished loading")
        print("loading map")
        # selenium_gis.load_map(driver)
        print("finished loading map")
        print("getting coardinates")
        street_number =84
        street_name = 'שדרות רוטשילד'
        coardinates = selenium_gis.search_side_street_coardiantes(driver,name=street_name,starting_number=street_number,length=5)
        new_coordinates = draw_street.normalize_coordinates(coardinates)
        draw_street.plot_coordinates(coordinates=new_coordinates)
        print(f"the coardiantes are :{new_coordinates} ")
        for i in range(len(new_coordinates)):
            
            selenium_gis.search_street_and_number(driver,name=street_name,number=street_number + 2*i,Close_toolbarLocates=True)
            time.sleep(3)
            selenium_gis.clear_map_signs(driver)
            time.sleep(0.5)
            selenium_gis.take_screenshot(driver)
            time.sleep(0.5)
            print(draw_street.even_oriented)
            outer_normal = draw_street.normalize_vector(draw_street.even_oriented(new_coordinates,i))
            print(f"outer_normal is :{outer_normal}")
            image = Image.open(image_path)
            classification_i = color_analysis.case_classification(image,dataset_colors,colors_to_avoid,outer_normal)
            result.append((street_number +i*2,classification_i))
            print(f"\n\n result_{i} is:   ___ {result[i]}___\n\n")
        print("\n\n\n final result is: \n\n\n")
        print(result)

    




        

        # coardinates = search_side_street_coardiantes(driver,length=2
    finally:
        pass


