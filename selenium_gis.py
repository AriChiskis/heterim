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
from bs4 import BeautifulSoup
import pathlib


ODD = 1
EVEN = 0

"""first version with decumentation and a lot simpler code for understanding in my opinion"""




def zoomin(driver,sleep_time=0.2):
    """this function will do a zoom in on the map, probably will be use when we want to zoomin after we have
        navigated to a spesific address"""
    # Setup the ChromeDriver
    try:
    # Loop to click the zoom button five times
        for _ in range(5):
            # Wait until the button is clickable (up to 10 additional seconds each time)
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'btnZoomIn'))
            )
            # Click the button
            button.click()
            # Wait a bit between clicks to allow the map to zoom in
            time.sleep(sleep_time)

    finally:
        # Close the browser after some time or based on some other condition
        pass


def zoom(driver,sleep_time=0.2,OUT=False,times=1):
    """zoom on the map n times, by default in"""
    #set up the zoom
    zoom = 'btnZoomIn'
    if OUT:
         zoom = 'btnZoomOut'         
     # Setup the ChromeDriver
    try:
    # Loop to click the zoom button five times
        for _ in range(times):
            # Wait until the button is clickable (up to 10 additional seconds each time)
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, zoom))
            )
            # Click the button
            button.click()
            # Wait a bit between clicks to allow the map to zoom in
            time.sleep(sleep_time)

    finally:
        # Close the browser after some time or based on some other condition
        pass
     

def click_on_first_option(driver):
        """ this function clicking on the first option in the dropdown, 
            the reason is because in this site this is the way i have found to get the click to work and to go the a spesific address
        """
        actions = ActionChains(driver)
        # Send the DOWN ARROW key and then the ENTER key
        actions.send_keys(Keys.ARROW_DOWN)
        actions.send_keys(Keys.ENTER)
        # Perform the action
        actions.perform()
        sleep(1)


def click_on_toolbarLocates(driver,sleep_time=0.2):
        """clicking simply on a html toolbarLocates (and opening it) / (or closing it)
            we let it sleep time of default 0.2 because this website is shit and can be slow
            NOTE: it is exactly has the same functionality of the function "click_on_element_by_ID" on ID = toolbarLocates
            I just did it becuase it is a very important button and if you want to use it especially for this  """
    # Click the button with ID 'toolbarLocates'
        toolbar_locates_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'toolbarLocates'))
        )
        time.sleep(sleep_time)
        toolbar_locates_button.click()
        # Wait for the street name input to become visible and interactable


def click_on_element_by_ID(driver,ID,sleep_time=0.2):
        """clicking simply on a html element by its ID
            we let it sleep time of default 0.2 because this website is shit and can be slow """
        element_id_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, ID))
        )
        time.sleep(sleep_time)
        element_id_button.click()
        return element_id_button


def move_mouse_to_center(driver):
    # Get the size of the window/viewport
    window_size = driver.execute_script("return [window.innerWidth, window.innerHeight]")
    center_x = window_size[0] / 2
    center_y = window_size[1] / 2

    # First, move to the top left of the `<body>` element
    body = driver.find_element(By.TAG_NAME, 'body')
    actions = ActionChains(driver)
    actions.move_to_element_with_offset(body, 0, 0)  # Move to top left of the body element
    actions.perform()
    
    # Now move to the center from the top-left corner
    actions = ActionChains(driver)  # Reset the actions
    actions.move_by_offset(center_x, center_y).perform()  # Move to the center
    print("Moved mouse to the center of the viewport.")


def extract_xyz_coordinates(driver):
    # Find the element containing the coordinates
    element = driver.find_element(By.ID, "txtCoords")
    # Get the text content of the element
    text = element.text
    
    # Use a regular expression to extract x, y, z values
    pattern = r"x:\s*(\d+(?:\.\d+)?)\s*y:\s*(\d+(?:\.\d+)?)\s*z:\s*(\d+(.\d+)?)"
    match = re.search(pattern, text)
    
    if match:
        x = float(match.group(1))
        y = float(match.group(2))
        z = float(match.group(3))

        if match != None:
            print(f"x : {x} , y: {y} , z: {z}")
        else:
            print("fuck !")


    
        return x, y, z
    else:
        return None


def get_xyz_coordinate(driver,sleep_time = 1):
     move_mouse_to_center(driver)
     time.sleep(sleep_time)
     return extract_xyz_coordinates(driver)


def get_xy_coardinates(driver):
     xyz = get_xyz_coordinate(driver)
     if xyz != None:
          return xyz[:-1]
     else:
          return None


def write_street_name(driver,name,sleep_time=0.2):
        """writing street name on toolbarLocates in input "inputStreets"  and clicking on the first option
            NOTE : toolbarLocate button should have been open"""
        
        street_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'inputStreets'))
    )
        time.sleep(sleep_time)
        street_input.clear()
        time.sleep(sleep_time)
        street_input.send_keys(name)
        time.sleep(sleep_time)


def write_street_number(driver,number,sleep_time=0.2,number_is_string = True):
        """writing street number on toolbarLocates in input מספר בית  and clicking on the first option
            NOTE : toolbarLocate button should have been open"""
        house_number_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="מס בית..."]'))
        )

        house_number_input.clear()
        time.sleep(sleep_time)
        if number_is_string:
              house_number_input.send_keys(number)
        else:
            house_number_input.send_keys(str(number))
        time.sleep(sleep_time)

def write_street_number_as_string(driver,string_number,sleep_time=0.2):
        """writing street number on toolbarLocates in input מספר בית  and clicking on the first option
            NOTE : toolbarLocate button should have been open
            NOTE : here number is string cause it can be numbers like 2 but also numbers like 2a
        """

        house_number_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="מס בית..."]'))
        )

        house_number_input.clear()
        time.sleep(sleep_time)
        house_number_input.send_keys(string_number)
        time.sleep(sleep_time)


def search_street_and_number(driver,name,number,Open_toolbarLocates = True,Close_toolbarLocates = False,sleep_time=0.2):
        """searches for a street and a number and clicking on it and eventually it apperas on the map.

            PAREMTERS:
            driver = webdriver 

            name = street name (string) 

            number = house number / number address of the street (int)

            Close_toolbarLocates = a boolean variable that says if we want to close toolbarLocates at the end

            NOTE:
                the reason that Close_toolbarLocates exists is that I want to save Selenium requests, for 
                example in the search_street function,you don't have to write the name of the street
                every time, so it can be faster 

            """
        search_street_sleep_time = 0.5
        if Open_toolbarLocates:
            # Click the button with ID 'toolbarLocates'
            print("open toolbar")
            click_on_toolbarLocates(driver)

        # Wait for the street name input to become visible and interactable
        write_street_name(driver,name)
        click_on_first_option(driver)

        # Wait for the house number input to become visible and interactable
        write_street_number(driver,number)
        click_on_first_option(driver)


        if Close_toolbarLocates:
            click_on_toolbarLocates(driver)
            print("closed toolbar")
        # Optionally, you can wait to observe the input effects or add further actions
        time.sleep(search_street_sleep_time)


def search_street_and_number_as_string(driver,name,number_as_string,Open_toolbarLocates = True,Close_toolbarLocates = False,sleep_time=0.2):
        """searches for a street and a number and clicking on it and eventually it apperas on the map.

            PAREMTERS:
            driver = webdriver 

            name = street name (string) 

            number = house number / number address of the street (string) instead of number

            Close_toolbarLocates = a boolean variable that says if we want to close toolbarLocates at the end

            NOTE:
                the reason that Close_toolbarLocates exists is that I want to save Selenium requests, for 
                example in the search_street function,you don't have to write the name of the street
                every time, so it can be faster 

            """
        search_street_sleep_time = 0.5
        if Open_toolbarLocates:
            # Click the button with ID 'toolbarLocates'
            print("open toolbar")
            click_on_toolbarLocates(driver)

        # Wait for the street name input to become visible and interactable
        write_street_name(driver,name)
        click_on_first_option(driver)

        # Wait for the house number input to become visible and interactable
        write_street_number(driver,number_as_string)
        click_on_first_option(driver)


        if Close_toolbarLocates:
            click_on_toolbarLocates(driver)
            print("closed toolbar")
        # Optionally, you can wait to observe the input effects or add further actions
        time.sleep(search_street_sleep_time)


def search_consecative_number_in_street(driver, name='רחוב דיזנגוף', number=150):
    '''given a number street, it searches map point of the consecative house of the street
        example: i am in streeet
            name='רחוב דיזנגוף',
            number=150
            it will check automatically for the address
            name='רחוב דיזנגוף',
            number=151

            NOTE: it is very important to remeber that the toolbarLocates (כפתור חיפושים, בסימן זכוכית מגדלת באתר) 
                is supposed to br open 
                here we will just change house number input for not waisting time bacause the street input will be already
                set in.
                

                '''
    sleep_time = 0.2 # Make sure sleep_time is defined    
    # Wait for the house number input to become visible and interactable
    write_street_number(driver,number+1)
    click_on_first_option(driver)
    time.sleep(sleep_time)


def search_street(driver,name='רחוב דיזנגוף',starting_number=150,length=3):
        """this function will visit over all the addresses street_name[ starting_number, starting_number+range ]
            PARAMETERS:
                driver = webdriver (ofcourse)
                name = name of the street
                starting_number = the start of street search (usually it will be number 1 because we want to start from the first number of the street
                length = the range of addresses that we want to scan eventually
            EXAMPLE: 
                name = dizengoff
                starting_number = 1
                range = 300
                MEANING: it will go over all on dizengodd street from starting_number 1 all over 
            """

        search_street_and_number(driver,name,starting_number,Close_toolbarLocates=True)
        house_number = starting_number

        for i in range(length-1):
            click_on_toolbarLocates(driver) #opening toolbarLocates
            search_consecative_number_in_street(driver=driver, name=name, number=house_number)
            #zoomin(sleep_time=sleep_time) #if you want to do zoomin on every house number
            house_number+=1
            click_on_toolbarLocates(driver) #closing toolbarLocates
        


def search_street_coardinates(driver,name='רחוב דיזנגוף',starting_number=150,length=3,get_coardinates=get_xy_coardinates):
        """description not valid, mnot good , need to work on it
        
        
        
    
            this function will visit over all the addresses street_name[ starting_number, starting_number+range ]
            PARAMETERS:
                driver = webdriver (ofcourse)
                name = name of the street
                starting_number = the start of street search (usually it will be number 1 because we want to start from the first number of the street
                length = the range of addresses that we want to scan eventually
   
                
            """

        street_coardinates = [None for i in range(length)]
        search_street_and_number(driver,name,starting_number,Close_toolbarLocates=True)
        #coaerdinate of starting point
        street_coardinates[0] = get_coardinates(driver)
        house_number = starting_number
        

        for i in range(1,length):
            click_on_toolbarLocates(driver) #opening toolbarLocates
            search_consecative_number_in_street(driver=driver, name=name, number=house_number)
            #zoomin(sleep_time=sleep_time) #if you want to do zoomin on every house number
            house_number+=1
            street_coardinates[i] = get_xyz_coordinate(driver) #getting coardinate of street+coardinates[i]
            click_on_toolbarLocates(driver) #closing toolbarLocates
            
        return street_coardinates


def load_map(driver):
    """this function loads the map of תוכנית 5000 אזורי ייעוד') on the regular map of the website"""
    sleep_time = 3

    # Click the button with ID 'toolbarLayers'
    toolbarLayers_button_id = 'toolbarLayers'
    toolbar_layers_button = click_on_element_by_ID(driver,toolbarLayers_button_id)
    print('Layer toolbar opened')
    time.sleep(sleep_time)

    # Wait for the layer search input to become visible and interactable
    layer_search_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="אתר שכבה..."]'))
    )
    
    # Click on the element with ID 'spnlayer1016'
    spn_layer_button_id =  'spnlayer1016'
    spn_layer_button = click_on_element_by_ID(driver,spn_layer_button_id)
    print('Clicked on שכבות רסטריות')
    time.sleep(sleep_time)

    # Click on the element with ID 'spnSubLayer607'
    spn_sub_layer_button_id = 'spnSubLayer607'
    spn_sub_layer_button_button = click_on_element_by_ID(driver,spn_sub_layer_button_id)
    print('Clicked on תוכנית 5000 אזורי ייעוד')

    # Click on the checkbox with ID 'chk607'
    #clicking on opening_map
    checkbox_id = 'chk607'
    checkbox_button = click_on_element_by_ID(driver,checkbox_id)
    # Re-click the toolbarLayers button to collapse the layers menu
    toolbar_layers_button.click()
    print('Layer toolbar closed')
    time.sleep(sleep_time + 5)


def clear_map_signs(driver):
    """clear_map_signs (the black dot that mentions the street that you have navigated to)"""
    # Define a reasonable time to wait for elements to be interactable
    print("clear_map_signs start_clearing")
    wait_time = 10
    try:
        # Wait for the clear button to be clickable and then click it
        clear_button = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.ID, 'btnClear'))
        )
        clear_button.click()
        print("Map signs have been cleared.")
    except Exception as e:
        print(f"An error occurred while trying to clear map signs: {e}")

    # Optionally, add a short delay to observe changes on the UI, if necessary
    time.sleep(3)


def locate_address(driver,name,number):
    """this function goes to a certain address: (street,number)
        then zooms in on the center of the address (identified by a black address map sign)
        and then clears it (that we will be reasdy to take the screenshot)"""
    search_street_and_number(driver,name,number,Close_toolbarLocates=True)
    time.sleep(3)
    zoomin(sleep_time)
    clear_map_signs(driver)


def take_screenshot(driver, file_path='screenshot.png'):
    """The WebDriver takes the screenshot and saves it to the specified file path.
        I create this function to take screenshot To identify the color of the building plot and as a result understand the building rights"""
    try:
        # The WebDriver takes the screenshot and saves it to the specified file path
        driver.save_screenshot(file_path)
        print(f"Screenshot saved to {file_path}")
    except Exception as e:
        print(f"Failed to take screenshot: {e}")


def locate_and_capture_address(driver, df, folder_path='map_colors_to_addresses'):
    """
    Locates addresses specified in a pandas DataFrame and captures screenshots of the map view for each address.
    
    This function automates the process of navigating to specific addresses on a map, managing the map's interface,
    and taking screenshots of each location. The screenshots are saved in a specified directory, making it easy to
    visually verify or review the map status for each address.

    Parameters:
    - driver: Selenium WebDriver instance that is used to control the browser.
    - df: pandas DataFrame containing the address data. The DataFrame must have columns 'street' and 'number'
          that specify the street name and the number for each address respectively.
    - folder_path (str, optional): The path to the directory where screenshots will be saved. Defaults to
          'map_colors_to_addresses'. If the directory does not exist, it will be created.

    The function constructs the complete address by prefixing 'רחוב' to the street name from the DataFrame.
    For each address, it calls another function `locate_address` to manage map interaction, such as centering
    the map on the address and adjusting zoom levels or other settings as needed.

    After setting the map view, the function captures a screenshot of the browser window and saves it to the
    specified folder. The filename for each screenshot is constructed using the address and house number
    to ensure each screenshot can be uniquely identified.

    THIS DECOUMENTATION WROTE CHATGPT
    """
    # Ensure the target folder exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Iterate over each row in the dataframe
    for index, row in df.iterrows():
        street = row['street']
        number = row['number']
        name = f'רחוב {street}'
        
        # Call the function to locate the address and manage the map
        locate_address(driver, name, number)
        
        # Construct the filename for the screenshot
        file_name = f"{name} {number}.png"
        file_path = os.path.join(folder_path, file_name)
        
        # Take screenshot and save it
        driver.save_screenshot(file_path)
        print(f"Screenshot saved to {file_path}")


def search_side_street_coardiantes(driver,name,starting_number,length=3,get_coardinates=get_xy_coardinates):
        """
        this function iterates over a range of streets (even orr odd) given a starting point and a length of iteration
        (example starting_number = 150 ,length = 4 , 150 ,152 ,154 ,156)
        and creates the vector of the coardinates
        """
   
                
 

        street_coardinates = [None for i in range(length)]
        search_street_and_number(driver,name,starting_number,Close_toolbarLocates=True)
        #coaerdinate of starting point
        street_coardinates[0] = get_coardinates(driver)
        house_number = starting_number
        coardinates = []
        coardinates.append(get_xy_coardinates(driver))
        clear_map_signs(driver)
        take_screenshot(driver,file_path=name + " " + str(house_number) + '.png')


        

        for i in range(1,length):
            click_on_toolbarLocates(driver) #opening toolbarLocates
            search_consecative_number_in_street(driver=driver, name=name, number=house_number+1)
            #zoomin(sleep_time=sleep_time) #if you want to do zoomin on every house number
            house_number+=2
            street_coardinates[i] = get_coardinates(driver) #getting coardinate of street+coardinates[i]
            clear_map_signs(driver)
            coardinates.append(get_xy_coardinates(driver))
            click_on_toolbarLocates(driver) #closing toolbarLocates
            take_screenshot(driver,file_path=name  + " "  + str(house_number) + '.png')
        print("\n\n__coardiantes are: \n\n")
        print(coardinates)
        print("\n\n\n")
        return street_coardinates


def create_directory(street,streets_folder):
    # Specify the directory name
        folder_name = street
        relative_path = pathlib.Path(streets_folder)
        # Full path to the new folder
        full_path = relative_path / folder_name
        odd_path = full_path / "odd"
        even_path = full_path /  "even"
        # Create the folder if it does not exist
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)

        if not odd_path.exists():
            odd_path.mkdir(parents=True, exist_ok=True)
        
        if not even_path.exists():
            even_path.mkdir(parents=True, exist_ok=True)
        

        return full_path




     
def take_side_street_screenshots_and_coardiantes(driver , street_dir , side_list , side , get_coardinates = get_xy_coardinates ):
    street_coardinates = []
    for number in side_list:
        click_on_toolbarLocates(driver = driver) # open tollabrLocate
        write_street_number(driver = driver , number=number,number_is_string=True)
        click_on_toolbarLocates(driver = driver) # close tollabrLocate
        clear_map_signs(driver = driver)
        street_coardinates.append( get_coardinates(driver) )
        take_screenshot(driver = driver , file_path = street_dir / side / (number + ".png") )
    return street_coardinates
     

def scan_street_side_and_get_coardinates(driver , street , streets_folder = "streets" , get_coardinates= get_xy_coardinates):
    street_dir = create_directory(street=street , streets_folder=streets_folder)
    street_numbers = get_street_numbers(driver=driver,street=street)
    odd_list, even_list = separate_street_numbers_to_odd_and_even(street_numbers=street_numbers)

    odd_coardiantes = take_side_street_screenshots_and_coardiantes(driver = driver , street_dir=street_dir , side_list= odd_list , side = "odd")
    even_coardinates = take_side_street_screenshots_and_coardiantes(driver = driver , street_dir=street_dir , side_list= even_list , side = "even")
    file_path = pathlib.Path(street_dir / "coardinates.txt")

    # Writing the lists to the file
    with file_path.open("w") as file:
        # Writing list1 by converting each element to string and joining with comma
        file.write(','.join(map(str, odd_coardiantes)) + '\n')
        # Writing list2 in the same way
        file.write(','.join(map(str, even_coardinates)) + '\n')


    return odd_coardiantes , even_coardinates

    


        
     
     

def get_street_numbers(driver,street):
    numbers = []
    click_on_toolbarLocates(driver) #open clicbarLocates

    write_street_name(driver,street)
    click_on_first_option(driver)
    # Get the page source from Selenium
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    # Find the element by ID or class or whatever suits your needs
    dropdown_list = soup.find('ul', {'id': 'inputHouses_listbox'})
    if dropdown_list:
        for li in dropdown_list.find_all('li'):
            numbers.append(li.text)
    
    click_on_toolbarLocates(driver) #close clicbarLocates
    
    return numbers


def separate_street_numbers_to_odd_and_even(street_numbers):
    odd_list = []
    even_list = []
    
    # Regex pattern to extract numbers from a string
    number_pattern = re.compile(r'\d+')

    for item in street_numbers:
        # Find all numbers in the string
        numbers = number_pattern.findall(item)
        # Check each number
        for number in numbers:
            if int(number) % 2 == 0:
                even_list.append(item)
                break  # Move to next string after classifying
            else:
                odd_list.append(item)
                break  # Move to next string after classifying
    
    return odd_list, even_list






def new_func(get_street_numbers, separate_street_numbers_to_odd_and_even, driver):
    street_numbers = get_street_numbers(driver=driver,street='רחוב חנקין')
    print(street_numbers)
    odd_list, even_list = separate_street_numbers_to_odd_and_even(street_numbers)
    print("Odd List:", odd_list)
    print("Even List:", even_list)

if __name__ == "__main__":
    sleep_time = 0.2

    driver = webdriver.Chrome()
    link = 'https://gisn.tel-aviv.gov.il/iView2js4/index.aspx'


    


    try:

        # Open the web page
        driver.get(link)
        time.sleep(20) # let it the page load all the stuff (it is very very slow at the start)
        load_map(driver)
        street = "רחוב יהודה המכבי"
        scan_street_side_and_get_coardinates(driver = driver , street = street)
        

 
    finally:
         pass

