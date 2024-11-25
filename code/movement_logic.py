from PIL import Image
from color_classifier import calculate_color_percentages
from color_classifier import filter_colors_precentage
import draw_street as draw_street
import pathlib
import re
from collections import deque
from tqdm import tqdm
import pandas as pd

ENQUEUE = "ENQUEUE"
EVEN = 0 
ODD = 1
# Define your base color dictionary
base_colors = {
    "body": (253, 220, 151),
    "banana_yellow": (254, 254, 152),
    "maccabi_yellow": (254, 254, 25),
    "orange": (253, 118, 21),
    "purple_1": (209, 147, 253),
    "purple_2": (195, 61, 253),
    "purple_3": (114, 25, 214),
    # "pink_flower": (253, 146, 149),
    "red_flower":  (235, 87, 87) ,#(253, 70, 77),
    "pink": (253, 147, 153),
    "red": (254, 41, 23),
    "shiny_pink" : (254, 25, 161) ,  # for purple type 3 could be diagonal and double diagonal
    "dark_olive_green" : (57, 62, 24) ,
    "brown" : (164, 81, 58) , 
    "boulivard_light_green" : (164, 81, 58) , 
    "park_green" : (23, 61, 20) , 
    "black" : (36, 38, 42) ,
    "red_train" : (208, 24, 18) , 
    "gray_train" : (200, 204, 203) , 

}

##############################
# from PIL import Image
# from pathlib import Path

def move_by_normal(image_path, unit_normal,step_size=300, default_length=400, save_dir='cropped_pictures', file_name='new_center_cropped.jpg'):
    """
    Moves from the center of the image in the direction of a unit normal vector, crops a region, and saves the image.

    Args:
        image_path (str): The path to the image file.
        unit_normal (tuple): A tuple (dx, dy) representing the unit normal vector direction.
        step_size (int): The step size in pixels to move from the center.
        default_length (int): The side length of the square to crop around the new center.
        save_dir (str): The directory to save the cropped image.
        file_name (str): The name to save the cropped image as.

    Returns:
        None, but saves a cropped image at the specified location.
    """
    # Load the image
    image = Image.open(image_path)
    width, height = image.size

    # Calculate the new center based on the unit normal vector
    center_x, center_y = width // 2, height // 2
    new_x = center_x + int(unit_normal[0] * step_size)
    new_y = center_y - int(unit_normal[1] * step_size)

    # Define the cropping area
    half_length = default_length // 2
    left = max(new_x - half_length, 0)
    upper = max(new_y - half_length, 0)
    right = min(new_x + half_length, width)
    lower = min(new_y + half_length, height)

    # Crop the image
    cropped_image = image.crop((left, upper, right, lower))
    # cropped_image.show()

    # Create the directory if it does not exist
    save_path = pathlib.Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    # Save the cropped image
    full_save_path = save_path / file_name
    cropped_image.save(full_save_path)

    return cropped_image


def check_if_in_square(image, epsilon=3):
    """
    Check if the image is likely to be depicting a square based on specific color cues.

    Args:
        image (PIL.Image): Image to analyze.
        base_colors (dict): Dictionary of base colors used for analysis.
        epsilon (int): Epsilon value for color matching tolerance.

    Returns:
        str: "ENQUEUE" if colors indicative of a square are detected, otherwise "NOT ENQUEUE".
    """
    # Define colors that indicate a square
    square_line_turkiz = (197, 248, 187)
    square_light_green = (222, 246, 152)

    # Temporarily add square indicator colors to the base colors dictionary
    base_colors["square_line_turkiz"] = square_line_turkiz
    base_colors["square_light_green"] = square_light_green

    # Calculate color percentages including the temporary colors
    color_percentages = calculate_color_percentages(image=image, epsilon=epsilon)
    # Remove the temporary colors from the base colors dictionary
    base_colors.pop("square_line_turkiz", None)
    base_colors.pop("square_light_green", None)
 
    # Check if either color indicative of a square is present
    if "square_line_turkiz" in color_percentages or "square_light_green" in color_percentages:

        return ENQUEUE

    else:
        return "NOT ENQUEUE"


def am_i_near_train_rail(colors_in_center):
    red_train_treshhold_pass = False
    gray_train_treshhold_pass = False
    #check if we are in suspicious places , square , train , 
    if ("red_train" in colors_in_center):
        red_train_treshhold_pass = colors_in_center["red_train"] >= 0.1
    if ("gray_train" in colors_in_center):
        gray_train_treshhold_pass = colors_in_center["gray_train"] >= 0.15

    if (red_train_treshhold_pass or gray_train_treshhold_pass):
        print("not known no, suspected we are near train, dequing ")
        return 1
    else:
        return 0               


def analyze_dominant_colors(image, color_threshold=0.3):
    # image = image.convert('RGB')
    color_percentages = calculate_color_percentages(image)
    colors_to_check = ['orange', 'purple_1', 'purple_2', 'purple_3', 'red', 'pink', 'banana_yellow', 'maccabi_yellow', 'brown', 'dark_olive_green', 'park_green']

    # print(color_percentages)
    significant_colors = {color: perc for color, perc in color_percentages.items() if color in colors_to_check and perc >= color_threshold}
 
    # Check for the most dominant among the filtered colors
    if significant_colors:
        dominant_color = max(significant_colors, key=significant_colors.get)
        # Check for the presence of 'shiny pink' if purple variants are dominant
        if dominant_color in ['purple_1', 'purple_2', 'purple_3'] and ('shiny_pink' in color_percentages) and (color_percentages['shiny_pink'] >= 0.01):
            significant_colors['shiny_pink'] = color_percentages['shiny_pink']
        return significant_colors
    return {}


def check_purple1_line(image, color_thresholds):
    """
    Analyzes colors along a specific area of the image and checks if certain colors exceed defined thresholds.

    Args:
        image (PIL.Image): Image to analyze.
        color_thresholds (dict): Dictionary with colors as keys and their respective thresholds as values.

    Returns:
        dict: Dictionary with colors and their percentages if they exceed the thresholds.
    """
    color_percentages = calculate_color_percentages(image)
    significant_colors = {}

    # Check if 'purple1' is present and above the threshold

    if 'purple_1' in color_percentages and color_percentages['purple_1'] >= color_thresholds['purple_1']:
        significant_colors['purple_1'] = color_percentages['purple_1']
        # Further check for 'pink' and 'red_flower'
        for color in ['pink', 'red_flower']:
            if color in color_percentages and color_percentages[color] >= color_thresholds[color]:
                significant_colors[color] = color_percentages[color]

    return significant_colors


def process_body_yellow_case(image_path, normal_vector, street_direction, color_thresholds,dominant_color_threshold = 0.3):
    """
    Process the 'yellow case' by moving the image by normal, analyzing dominant colors,
    then moving by street direction and checking specific colors.

    Args:
        image_path (str): Path to the original image.
        normal_vector (tuple): The unit normal vector for initial movement.
        street_direction (tuple): The vector for the street direction movement.
        color_thresholds (dict): Thresholds for detecting significant colors.

    Returns:
        dict: Results of color analysis from both perspectives.
    """
    # Step 1: Move by normal and crop the image
    first_cropped_image = move_by_normal(image_path, normal_vector,file_name="yellow_case_outer_normal.png")
    # first_cropped_image.show()  # Optionally display the image

    # Step 2: Analyze dominant colors in the first cropped image
    dominant_colors = analyze_dominant_colors(image=first_cropped_image, color_threshold=dominant_color_threshold)
    # print(dominant_colors)
    if not dominant_colors:
        second_cropped_image = move_by_normal(image_path, normal_vector,step_size= 600 ,file_name="yellow_case_outer_normal_move_alot.png") 
        dominant_colors = analyze_dominant_colors(image=second_cropped_image, color_threshold=dominant_color_threshold)
        # print(f"second time {dominant_colors}")
        if not dominant_colors:
            return ENQUEUE

    # Step 3: Move by street direction vector and crop the second image
    third_cropped_image = move_by_normal(image_path, street_direction,file_name="yellow_case_street_direction.png")
    # second_cropped_image.show()  # Optionally display the image

    # Step 4: Check colors along the direction (second cropped image)
    color_line_check = check_purple1_line(third_cropped_image, color_thresholds)

    return {
        "dominant_colors": dominant_colors,
        "line_colors": color_line_check
    }


def process_park_green_case(image_path, normal_vector,street_direction):
    """
    Processes the park green case by checking for specific green color indicative of parks.

    Args:
        image_path (str): Path to the image file.
        normal_vector (tuple): The normal vector for moving the image.
        green_threshold (float): Threshold for green to confirm the green case.

    Returns:
        str: "ENQUEUE" if conditions met, otherwise "NOT ENQUEUE".
    """
    # Load the initial image and check colors
    image = Image.open(image_path).convert('RGB')
    colors_in_center = calculate_color_percentages(image=image)

    # First check: Determine if near a train rail
    if am_i_near_train_rail(colors_in_center):
        print("Train case detected, picture enqueued")
        return ENQUEUE

    # Move the image based on normal vector and check again
    cropped_image = move_by_normal(image_path, normal_vector,file_name="green_case_outer_normal.jpg")
    moved_colors = calculate_color_percentages(image=cropped_image)

    # Second check: After moving the image
    if am_i_near_train_rail(moved_colors):
        print("After movement: Still near train rail, picture enqueued")
        return ENQUEUE

    # Analyze dominant colors for the green case
    dominant_colors = analyze_dominant_colors(cropped_image)
    if not dominant_colors:
            return ENQUEUE
    
    second_cropped_image = move_by_normal(image_path, street_direction,file_name="green_case_street_direction.png")
    color_line_check = check_purple1_line(second_cropped_image, color_thresholds)

    return {
        "dominant_colors": dominant_colors,
        "line_colors": color_line_check
    }



def i_am_in_color(colors_in_picture , color , color_treshold):
    return color in colors_in_picture and colors_in_picture[color] >= color_treshold


def classical_case(image_path, normal_vector, street_direction, color_thresholds,step_size = 200):

        cropped_image = move_by_normal(image_path=image_path,unit_normal=(0,0),file_name="classical_case_dominant_colors.png")
        dominant_colors = analyze_dominant_colors(image=cropped_image,color_threshold=0.3)
        # Check if dominant_colors is empty
        if not dominant_colors:
            return ENQUEUE
        else:
            second_cropped_image = move_by_normal(image_path = image_path, unit_normal=street_direction,file_name="classical_checking_line_one_the_side_.png")
            color_line_check_street_direction = check_purple1_line(second_cropped_image, color_thresholds)
            #check also if there is a purple line with direction of inner normal of the street of the street

            third_cropped_image = move_by_normal(image_path=image_path , unit_normal= normal_vector , step_size= step_size , file_name="classical_checking_line_one_the_side_.png")
            color_line_check_inner_normal = check_purple1_line(third_cropped_image, color_thresholds)
            color_line_check = {**color_line_check_street_direction, **color_line_check_inner_normal}   #union of dictionaries          


            results = {
            "dominant_colors": dominant_colors,
            "line_colors": color_line_check
        }

            return results

def decide_the_kind_of_building(image_path, normal_vector, street_direction, color_thresholds, body_threshold,green_treshold):
    """
    Decides the kind of building based on the presence of significant yellow in the center of the image.
    If significant yellow is detected, it processes the image further in the yellow case scenario.

    Args:
        image_path (str): Path to the image file.
        normal_vector (tuple): The normal vector for movement and analysis in the yellow case.
        street_direction (tuple): The vector for movement along the street in the yellow case.
        color_thresholds (dict): Thresholds for significant colors in both analysis phases.
        yellow_threshold (float): Threshold for detecting significant yellow to trigger the yellow case.

    Returns:
        str or dict: "ENQUEUE" if no dominant colors are found; otherwise, a dictionary of results.
    """
    # Step 1: Load and analyze the central part of the image for yellow color
    image = Image.open(image_path).convert('RGB')
    colors_in_center = calculate_color_percentages(image=image)
    # Check if yellow or purple_1 is significant in the center of the image
    we_in_body = i_am_in_color(colors_in_picture=colors_in_center , color='body' , color_treshold=body_threshold)
    we_in_purple_1_line = i_am_in_color(colors_in_picture=colors_in_center , color='purple_1' , color_treshold=body_threshold)
    we_in_park_green =  i_am_in_color(colors_in_picture=colors_in_center,color='park_green',color_treshold=green_treshold)
    we_in_boulivard_light_green =  i_am_in_color(colors_in_picture=colors_in_center,color='boulivard_light_green',color_treshold=green_treshold)

    if we_in_body or we_in_purple_1_line:

        in_square = check_if_in_square(image=image)
        if in_square == ENQUEUE:
            return ENQUEUE
        results = process_body_yellow_case(image_path, normal_vector, street_direction, color_thresholds)
        # print(f"results yellow case: {results}")

    
    elif (we_in_park_green) or (we_in_boulivard_light_green):
        in_square = check_if_in_square(image=image)
        if in_square == ENQUEUE:
            return ENQUEUE  
        results = process_park_green_case(image_path=image_path,normal_vector=normal_vector,street_direction=street_direction)
        # print(f"results green case: {results}")

    else:
        #now we in a case that we dont need to go : we just check what is the color
        inner_normal = [-1*normal_vector[0] , -1*normal_vector[1]]
        results = classical_case(image_path=image_path , normal_vector=inner_normal,street_direction=street_direction,color_thresholds=color_thresholds)     
    
    if (results == ENQUEUE):
        return ENQUEUE
    elif not results["dominant_colors"]:
        return ENQUEUE
    else:
        return results

def alphanumeric_key(filename):
    """ Create a key for sorting filenames that are numbered potentially followed by a Hebrew letter. """
    # Match the numeric part and optional Hebrew letter just before the extension
    match = re.match(r"(\d+)([א-ת]?)\.png", filename.name)
    if match:
        number = int(match.group(1))
        letter = match.group(2)
        return (number, letter)
    return (0, '')  # Default key for filenames that do not match the expected pattern


def find_png_files_sorted(directory):
    # Create a Path object for the given directory
    path = pathlib.Path(directory)
    
    # Use the rglob method to find all .png files in the directory and subdirectories
    png_files = path.rglob('*.png')
    
    # Sort the files using the custom alphanumeric_key
    sorted_files = sorted(png_files, key=alphanumeric_key)
    
    # Return a list of paths to the .png files, converted to strings
    return [str(file) for file in sorted_files]


# Assuming draw_street and decide_the_kind_of_building are imported or defined elsewhere
def process_images(coordinates_list, image_paths,side = EVEN ):
    # Initialize an empty queue
    queue = deque()
    results = [None] * len(image_paths)  # Preallocate list to store results
    normalized_coordinates = draw_street.normalize_coordinates(coordinates_list)  # Normalize all coordinates at once if possible
    last_non_enqueue_result = None  # Keep track of the last non-ENQUEUE result

    # Iterate over image paths and their corresponding coordinates
    for i, (coordinates, image_path) in enumerate(tqdm(zip(coordinates_list, image_paths), total=len(image_paths), desc="Processing Images")):
        # print(f"analyzing on address {pathlib.Path(image_path).stem}")
        if side == EVEN:
            outer_normal = draw_street.normalize_vector(draw_street.even_oriented(coordinates=normalized_coordinates, index=i))
        else:
             outer_normal = draw_street.normalize_vector(draw_street.odd_oriented(coordinates=normalized_coordinates, index=i))

        street_direction = draw_street.normalize_vector(draw_street.straight_oriented(coordinates=normalized_coordinates,index=i))
        result = decide_the_kind_of_building(image_path=image_path, normal_vector=outer_normal,street_direction=street_direction, color_thresholds=color_thresholds ,body_threshold=0.2,green_treshold=0.2)
        if result == "ENQUEUE":
            # print(f"ENQUEUED {i}")
            queue.append(i)
        else:
            while queue:
                index = queue.popleft()
                results[index] = result
            results[i] = result
            last_non_enqueue_result = result  # Update the last non-ENQUEUE result

    # Check if there's any remaining queue items at the end of processing
    if queue:
        # If no non-ENQUEUE result was ever set, you might want to default to a specific value or handle the case separately
        fallback_result = last_non_enqueue_result if last_non_enqueue_result is not None else "DEFAULT_RESULT"
        while queue:
            index = queue.popleft()
            results[index] = fallback_result

    return results


# def print_formatted_results(image_paths, directory , results, side ,file_name = "results" ,translation_name = "translation.txt" , write_in_file = False):
#     """
#     Prints and writes formatted results of image processing to the console and a file.

#     Args:
#         image_paths (list): List of image file paths.
#         results (list): List of results corresponding to each image.
#         file_path (str): Path to the file where results will be written.
#     """
#     output = "\nResults for Image Processing:\n"
#     output += "----------------------------------\n"
#     translation_output = "\nResults for Image Processing:\n"
#     translation_output += "----------------------------------\n"

#     for image_path, result in zip(image_paths, results):
#         # Extract the basename of the image file
#         basename = pathlib.Path(image_path).name
#         output += f"{basename}:\n{result}\n"
#         result_translation = translate_color_scheme(dominant_colors=result["dominant_colors"],line_colors=result["line_colors"])
#         translation_output += f"{basename}:\n{result_translation}\n"

#     # Print to console
#     if write_in_file:
#         # Write to file
#         with open(pathlib.Path(directory) / file_name, 'w') as file:
#             file.write(output)

#         with open(pathlib.Path(directory) / translation_name, 'w') as file:
#             file.write(translation_output)
        
#     else:
#         print(output)




def print_formatted_results(image_paths, directory, results, side, street, global_df, file_name="results", translation_name="translation.txt", write_in_file=False):
    """
    Prints and writes formatted results of image processing to the console and a file, and updates a global DataFrame.

    Args:
        image_paths (list): List of image file paths.
        results (list): List of results corresponding to each image.
        directory (str): Directory path where results will be saved.
        side (str): Indicates whether the result is from the EVEN or ODD side.
        street_data (list): List of street names corresponding to each image.
        global_df (DataFrame): Global DataFrame to update.
        file_name (str, optional): Name of the file for saving results. Defaults to "results".
        translation_name (str, optional): Name of the file for saving translations. Defaults to "translation.txt".
        write_in_file (bool, optional): If True, writes results to a file. Defaults to False.
    """
    output = "\nResults for Image Processing:\n"
    output += "----------------------------------\n"
    translation_output = "\nTranslation of Results:\n"
    translation_output += "----------------------------------\n"

    new_data = []

    for image_path, result in zip(image_paths, results):
        basename = pathlib.Path(image_path).stem  # Using stem to exclude the file extension
        output += f"{basename}:\n{result}\n"
        result_translation = translate_color_scheme(dominant_colors=result["dominant_colors"], line_colors=result["line_colors"])
        translation_output += f"{basename}:\n{', '.join(result_translation)}\n"
        # print(basename)
        # Collect data for DataFrame
        new_data.append({
            "Number": basename,
            "Side": side,
            "Colors": (result),  # Assuming dominant_colors is a dictionary
            "Type_of_building" : result_translation ,
            "Street": street  # Add street name
        })

    # Update global DataFrame
    global_df = pd.concat([global_df, pd.DataFrame(new_data)], ignore_index=True)
    # print(global_df)

    # Output the results and translations
    if write_in_file:
        with open(pathlib.Path(directory) / file_name, 'w') as file:
            file.write(output)
        with open(pathlib.Path(directory) / translation_name, 'w') as file:
            file.write(translation_output)
    else:
        print(output)
        print(translation_output)

    return global_df  # Return the updated DataFrame

# Example usage:
# image_paths = ["path/to/image1.jpg", "path/to/image2.jpg"]
# results = [{'dominant_colors': {'red': 30, 'blue': 20}, 'line_colors': {'green': 15}}, {'dominant_colors': {'yellow': 25}, 'line_colors': {'pink': 5}}]
# street_data = ["Main St", "Second St"]
# directory = "path/to/results"
# side = "EVEN"
# global_df = print_formatted_results(image_paths, directory, results, side, street_data, global_df, write_in_file=False)


def check_street_side(directory ,coardinates, side , street ,global_df ,file_name = "results.txt" ,write_in_file=True):
    image_paths = find_png_files_sorted(directory=directory)
    results = process_images(coordinates_list=coardinates , image_paths=image_paths,side = side)
    dataframe = print_formatted_results(image_paths=image_paths, directory=directory , results=results, side = side , street=street , global_df=global_df , file_name=file_name,write_in_file = write_in_file )
    return dataframe


def process_street(base_directory,global_df):
    # Define paths to directories
    base_path = pathlib.Path(base_directory)
    street_name = base_path.name
    directory_even = base_path / "even"
    directory_odd = base_path / "odd"
    
    # Read coordinates from file
    coordinates_file = base_path / "coordinates.txt"
    with open(coordinates_file, 'r') as file:
        lines = file.readlines()
        coordinates_odd = eval(lines[0].strip())
        coordinates_even = eval(lines[1].strip())
    
    # Process coordinates
    even_dataframe = check_street_side(directory_even, coordinates_even, side=EVEN,street=street_name,global_df=global_df, write_in_file=True)
    even_and_odd_dataframe = check_street_side(directory_odd, coordinates_odd, side=ODD,street=street_name , global_df=even_dataframe ,write_in_file=True)
    return even_and_odd_dataframe
# Assuming draw_street and decide_the_kind_of_building are imported or defined elsewhere
def process_image(coordinates_list,index,image_path,side = EVEN ):

    normalized_coordinates = draw_street.normalize_coordinates(coordinates_list)  # Normalize all coordinates at once if possible

    if side == EVEN:
        outer_normal = draw_street.normalize_vector(draw_street.even_oriented(coordinates=normalized_coordinates, index=index))
    else:
        outer_normal = draw_street.normalize_vector(draw_street.odd_oriented(coordinates=normalized_coordinates, index=index))

    street_direction = draw_street.normalize_vector(draw_street.straight_oriented(coordinates=normalized_coordinates,index=index))
    result = decide_the_kind_of_building(image_path=image_path, normal_vector=outer_normal,street_direction=street_direction, color_thresholds=color_thresholds ,body_threshold=0.2,green_treshold=0.2)

    return result

#important
def is_even_or_odd(address):
    # Extract numbers from the string
    if isinstance(address, int):
        numbers = [address]
        address = str(address)
    else:
        numbers = re.findall(r'\d+', address)

    if numbers:
        # Convert the first group of digits found to an integer
        number = int(numbers[0])
        # Check if the number is even or odd
        if number % 2 == 0:
            return EVEN , address
        else:
            return ODD ,address
    else:
        return "No valid number found"
#important
def find_index_in_list(target, items):
    try:
        # Get the index of the target in the list
        index = items.index(target)
        return index
    except ValueError:
        # Return a message if the target is not in the list
        print("The item does not exist in the list.")
        exit(0)
#important
def process_address(base_directory,number):
    # Define paths to directories
    print(f"processing street {base_directory} address number : {number}")
    base_path = pathlib.Path(base_directory)
    directory_even = base_path / "even"
    directory_odd = base_path / "odd"
    coordinates_file = base_path / "coordinates.txt"
    with open(coordinates_file, 'r') as file:
        lines = file.readlines()
        coordinates_odd = eval(lines[0].strip())
        coordinates_even = eval(lines[1].strip())

    even_or_odd , string_num = is_even_or_odd(address=number)
    if even_or_odd == EVEN:
            image_path = (directory_even / (string_num + ".png"))
            
            images = find_png_files_sorted(directory=directory_even)
            index = find_index_in_list(target=str(image_path),items=images)
            return process_image(coordinates_list=coordinates_even,index=index , image_path=image_path, side=EVEN)
            
    if even_or_odd == ODD:
            image_path = (directory_odd / (string_num + ".png"))
            images = find_png_files_sorted(directory=directory_odd)

            index = find_index_in_list(target=str(image_path),items=images)
            return process_image(coordinates_list=coordinates_odd ,index=index , image_path=image_path, side=ODD)

# Define the thresholds for each color
color_thresholds = {
    'purple_1': 0.2,  # 10% threshold for purple1
    'pink': 0.08,    # 5% threshold for pink
    'red_flower': 0.08  # 5% threshold for red_flower
}


def translate_color_scheme(dominant_colors, line_colors):
    translation_dict = {
        'major_colors': {
            "banana_yellow": "אזור מגורים בבניה נמוכה",
            "maccabi_yellow": "אזור מגורים בבניה עירונית נמוכה",
            "orange": "אזור מגורים בבניה עירונית",
            "red": "אזור מגורים בבניה רבת קומות",
            "purple_1": "אזור תעסוקה מקומי",
            "purple_2": "אזור תעסוקה עירוני",
            "purple_3": "אזור תעסוקה מטרופוליני",
            "boulivard_light_green": "שטח פתוח עירוני",
            "park_green": "שטח פתוח מטרופוליני",
            "dark_olive_green" : "איזור פעילות מיוחד" ,
            "shiny_pink": "אזור תעסוקה סמוך להסעת המונים" , 
            "pink": "אזור מעורב לתעסוקה ולמגורים"
        },
        'minor_colors': {
            "pink": "ציר מעורב",
            "red_flower": "ציר מעורב",
            "shiny_pink": "אזור תעסוקה סמוך להסעת המונים",
            "purple_1": "חזית מסחרית",
        }
    }

    # Collect all major color translations from dominant_colors
    major_translations = [
        translation_dict['major_colors'][color]
        for color in dominant_colors
        if color in translation_dict['major_colors'] and color != "purple_1"
    ]
 
    # Check for 'purple_1' in both dominant_colors and color_line_check
    has_purple_1 = "purple_1" in dominant_colors or "purple_1" in line_colors

    # Check for 'pink' or 'red_flower' in color_line_check
    has_pink_or_red_flower = any(color in line_colors for color in ["pink", "red_flower"])

    # Conditionally append minor color translations
    if has_purple_1:
        if has_pink_or_red_flower:
            major_translations.append("ציר מעורב")
        else:
            major_translations.append("חזית מסחרית")
    return major_translations

def save_dataframe(file_path,dataframe):

        dataframe.to_csv(file_path, index=False)
        print(f"DataFrame saved to {file_path}")

# global_df = pd.DataFrame(columns=["Number", "Side", "Colors", "Street" , "Type_of_building"])
# Query the DataFrame for specific street and number

if __name__ == "__main__":
    directory = "streets/רחוב יהודה המכבי"
    street_data_df_path = "street_data.csv"
    df = pd.read_csv(street_data_df_path)
    query_result = df[(df['Street'] == "רחוב חנקין")]















