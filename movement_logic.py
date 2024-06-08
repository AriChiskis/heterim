from PIL import Image
from color_classifier import calculate_color_percentages
from color_classifier import filter_colors_precentage
import draw_street
import pathlib
import re
from collections import deque
from tqdm import tqdm

ENQUEUE = "ENQUEUE"
# Define your base color dictionary
base_colors = {
    "body": (253, 220, 151),
    "banana": (254, 254, 152),
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
from PIL import Image
from pathlib import Path

def move_by_normal(image_path, unit_normal, step_size=300, default_length=400, save_dir='cropped_pictures', file_name='new_center_cropped.jpg'):
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
    save_path = Path(save_dir)
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
    colors_to_check = ['orange', 'purple_1', 'purple_2', 'purple_3', 'red', 'pink', 'banana_yellow', 'maccabi_yellow', 'brown', 'khaki', 'park_green']

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
    if 'purple_1' in color_percentages and color_percentages['purple_1'] >= color_thresholds.get('purple_1', 0):
        significant_colors['purple_1'] = color_percentages['purple_1']
        # Further check for 'pink' and 'red_flower'
        for color in ['pink', 'red_flower']:
            if color in color_percentages and color_percentages[color] >= color_thresholds.get(color, 0):
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
    # Step 3: Move by street direction vector and crop the second image
    second_cropped_image = move_by_normal(image_path, street_direction,file_name="yellow_case_street_direction.png")
    # second_cropped_image.show()  # Optionally display the image

    # Step 4: Check colors along the direction (second cropped image)
    color_line_check = check_purple1_line(second_cropped_image, color_thresholds)

    return {
        "dominant_colors": dominant_colors,
        "line_colors": color_line_check
    }


def process_park_green_case(image_path, normal_vector):
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
    return dominant_colors


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

    # Check if yellow is significant in the center of the image
    if 'body' in colors_in_center and colors_in_center['body'] >= body_threshold:
        # Process the image for the yellow case since yellow is significant
        #step 1
        in_square = check_if_in_square(image=image)
        if in_square == ENQUEUE:
            return ENQUEUE
        #step 2
        results = process_body_yellow_case(image_path, normal_vector, street_direction, color_thresholds)

        # Analyze the results from the yellow case
        dominant_colors = results['dominant_colors']
        line_colors = results['line_colors']
        # Check if dominant_colors is empty
        if not dominant_colors:
            return ENQUEUE
        else:
            return results

    we_in_park_green =  ('park_green' in colors_in_center and colors_in_center['park_green'] >= green_treshold)
    we_in_boulivard_light_green = ('boulivard_light_green' in colors_in_center and colors_in_center['boulivard_light_green'] >= green_treshold)
    if (we_in_park_green) or (we_in_boulivard_light_green):
        dominant_colors = process_park_green_case(image_path=image_path,normal_vector=normal_vector)

        # Check if dominant_colors is empty
        if not dominant_colors:
            return ENQUEUE
        else:
            return dominant_colors
        
    #now we in a case that we dont need to go we just check what is the color
    cropped_image = move_by_normal(image_path=image_path,unit_normal=(0,0),file_name="no_spesific_case_dominant_colors.png")
    dominant_colors = analyze_dominant_colors(image=cropped_image,color_threshold=0.3)
# Check if dominant_colors is empty
    if not dominant_colors:
        return ENQUEUE
    else:
        return dominant_colors
            

# Define the thresholds for each color
color_thresholds = {
    'purple1': 0.2,  # 10% threshold for purple1
    'pink': 0.05,    # 5% threshold for pink
    'red_flower': 0.05  # 5% threshold for red_flower
}



# def move_perpendicular(image_path, unit_normal, step_size=300, default_length=400, clockwise=True):
#     """
#     Moves from the center of the image in a direction perpendicular to a unit normal vector, crops a region, and saves the image.

#     Args:
#         image_path (str): The path to the image file.
#         unit_normal (tuple): A tuple (dx, dy) representing the unit normal vector direction.
#         step_size (int): The step size in pixels to move from the center.
#         default_length (int): The side length of the square to crop around the new center.
#         clockwise (bool): If True, move perpendicular in the clockwise direction; otherwise, counterclockwise.

#     Returns:
#         None, but saves a cropped image at the new location.
#     """
#     # Load the image
#     image = Image.open(image_path)
#     width, height = image.size

#     # Calculate the new center based on the perpendicular direction
#     dx, dy = unit_normal
#     if clockwise:
#         perp_dx, perp_dy = -dy, dx
#     else:
#         perp_dx, perp_dy = dy, -dx

#     center_x, center_y = width // 2, height // 2
#     new_x = center_x + int(perp_dx * step_size)
#     new_y = center_y + int(perp_dy * step_size)

#     # Define the cropping area
#     half_length = default_length // 2
#     left = max(new_x - half_length, 0)
#     upper = max(new_y - half_length, 0)
#     right = min(new_x + half_length, width)
#     lower = min(new_y + half_length, height)

#     # Crop the image
#     cropped_image = image.crop((left, upper, right, lower))

#     # Save the cropped image
#     cropped_image.save('new_perpendicular_cropped.jpg')






# def move_park_green(image_path, unit_normal, step_size, default_length, epsilon=30):
#     move_by_normal(image_path, unit_normal, step_size, default_length)
#     # Open the newly created cropped image
#     cropped_image = Image.open('new_center_cropped.jpg')
#     # Calculate the color percentages in the cropped image
#     color_percentages = calculate_color_percentages(image=cropped_image, epsilon=epsilon)
#     amINearTrainRail = am_i_near_train_rail(colors_in_center=color_percentages)
#     if amINearTrainRail:
#         print("train case , picture enqueued")
#         return ENQUEUE


#     return color_percentages




# def move_yellow_body(image_path, unit_normal, step_size, default_length, epsilon=30):
#     """
#     Moves from the center of the image in the direction of a unit normal vector, crops a region,
#     and analyzes the color percentages of the cropped area.

#     Args:
#         image_path (str): The path to the image file.
#         unit_normal (tuple): A tuple (dx, dy) representing the unit normal vector direction.
#         step_size (int): The step size in pixels to move from the center.
#         default_length (int): The side length of the square to crop around the new center.
#         base_colors (dict): A dictionary mapping color names to RGB tuples.
#         epsilon (int): Threshold for deciding color match proximity.

#     Returns:
#         A dictionary mapping color names to their approximate percentages in the cropped image.
#     """
#     # Move and crop the image based on the provided unit normal vector and step size
#     move_by_normal(image_path, unit_normal, step_size, default_length)

#     # Open the newly created cropped image
#     cropped_image = Image.open('new_center_cropped.jpg')

#     # Calculate the color percentages in the cropped image
#     color_percentages = calculate_color_percentages(image=cropped_image, epsilon=epsilon)

#     return color_percentages


# def move_purple_type_1(image_path, unit_normal, step_size=300, default_length=400, epsilon=30,clockwise=True):
#     """
#     Analyzes a region in the direction of a unit normal vector and another region perpendicular to that direction to determine if it's "mixed purple type 1".

#     Args:
#         image_path (str): The path to the image file.
#         unit_normal (tuple): A tuple (dx, dy) representing the unit normal vector direction.
#         step_size (int): The step size in pixels to move from the center.
#         default_length (int): The side length of the square to crop around the new center.
#         base_colors (dict): A dictionary mapping color names to RGB tuples.
#         epsilon (int): Threshold for deciding color match proximity.

#     Returns:
#         A tuple: ("mixed purple type 1", right_side_colors) if red_flower or pink_flower are found in the perpendicular direction; otherwise, ("purple type 1", right_side_colors).
#     """
#     # First, move and analyze colors in the direction of the unit normal vector
#     move_by_normal(image_path, unit_normal, step_size, default_length)
#     cropped_image = Image.open('new_center_cropped.jpg')
#     right_side_colors = calculate_color_percentages(image = cropped_image,epsilon = epsilon)

#     # Use the move_perpendicular function to move in the perpendicular direction
#     move_perpendicular(image_path, unit_normal, step_size, default_length, clockwise=clockwise)  # You can set clockwise to False if needed
#     perp_cropped_image = Image.open('new_perpendicular_cropped.jpg')
#     perp_colors = calculate_color_percentages(image = perp_cropped_image, epsilon = epsilon)


#     # Check for the presence of "red_flower" or "pink_flower" in the perpendicular direction

#     if ('red_flower' in perp_colors or 'pink_flower' in perp_colors) and ('shiny_pink' in right_side_colors ):
#         return ("mixed purple type 1 flower with shiny pink stripes at the back", right_side_colors)

    
#     if ('red_flower' in perp_colors or 'pink_flower' in perp_colors):
#         return ("mixed purple type 1 flower", right_side_colors)
    
#     if 'shiny_pink' in right_side_colors:
#          return ("mixed purple type 1 with shiny_pink stripes",right_side_colors )


#     return ("purple type 1", right_side_colors)




# def decide_the_kind_of_building(image_path , outer_normal , yellow_threshold=0.2):
#     print("deciding ...")
#     """
#     Analyzes an image to determine the type of building based on specific color criteria.

#     Args:
#         image_path (str): The path to the image file.
#         base_colors (dict): A dictionary mapping color names to RGB tuples.
#         epsilon (int): Threshold for color matching proximity.
#         yellow_threshold (float): The minimum percentage of "yellow" color required to further analyze yellow_body.

#     Returns: 
#         tuple or str: The classification of the building based on color analysis.
#     """
#     # Load and analyze the central part of the image
#     image = Image.open(image_path).convert('RGB')
#     colors_in_center = calculate_color_percentages(image=image)

#     significant_colors = {color: perc for color, perc in colors_in_center.items() if perc >= 0.3}
    
#     print("deciding cases now")

#     amINearTrainRail= am_i_near_train_rail(colors_in_center=colors_in_center)
#     if amINearTrainRail:
#         print("train case , picture enqueued")
#         return ENQUEUE

#     # Check for the absence of "yellow_body" and "purple type 1"
#     if 'body' not in colors_in_center and 'purple_1' not in colors_in_center and 'park_green' not in colors_in_center and 'boulivard_light_green' not in colors_in_center: # case that there is no purple_type1 and yellow body
#         print("significant color case:")
#         if significant_colors:
#             if 'shiny_pink' in colors_in_center:
#                 significant_colors['shiny_pink'] = colors_in_center['shiny_pink']
#             print("Significant colors above 30% threshold:", significant_colors)
#             return significant_colors
#         else:
#             print("No significant colors identified above the 30% threshold.")

#             return ENQUEUE


 
#     # Yellow case: Check if yellow is above the threshold and then move_yellow_body
#     if colors_in_center.get('body', 0) > yellow_threshold:
#         print(f" Yellow case: Check if yellow is above the threshold and then move_yellow_body")
#         #check if we are in square
#         square_line_turkiz = (197, 248, 187)
#         square_light_green = (222, 246, 152)
#         base_colors["square_line_turkiz"] = square_line_turkiz
#         base_colors["square_light_green"] = square_light_green
#         checking_square = calculate_color_percentages(image=image,epsilon = 3)
#         base_colors.pop("square_line_turkiz")
#         base_colors.pop("square_light_green")

#         if ("square_line_turkiz" in checking_square) or ("square_light_green" in checking_square) :
#             return ENQUEUE


#         colors_after_moving_yellow = move_yellow_body(image_path,outer_normal, step_size=300, default_length=400)
#         if 'purple_1' in colors_after_moving_yellow:
#             if colors_after_moving_yellow.get('purple_1', 0) > 0.15:
#                 result = move_purple_type_1(image_path=image_path, unit_normal=outer_normal)  # Assuming some unit_normal
#                 return result
#         #naybe another purple is there
#         print(colors_after_moving_yellow)
#     #park green case
         


#     if colors_in_center.get('park_green', 0) > 0.2:
#         print(f"park_green case: Check if park_green is above the threshold and then park_green")
#         colors_after_moving_green = move_park_green(image_path=image_path,unit_normal=outer_normal,step_size=300,default_length=400)
#         return colors_after_moving_green
#     # Purple case: Directly analyze if purple is present

#     if colors_in_center.get('boulivard_light_green', 0) > 0.2:
#         print(f"boulivard_light_green case: Check if boulivard_light_green is above the threshold and then boulivard_light_green")
#         move_by_normal(image_path, outer_normal)
#         # Open the newly created cropped image
#         cropped_image = Image.open('new_center_cropped.jpg')
#         # Calculate the color percentages in the cropped image
#         color_percentages = calculate_color_percentages(image=cropped_image, epsilon=30)
#         return color_percentages


#     if colors_in_center.get('purple_1', 0) > 0.2:
#         print(f"Purple case: Directly analyze if purple is present")
#         result = move_purple_type_1(image_path, unit_normal=outer_normal)  # Adjust unit_normal as needed
#         return result

#     print("Unable to classify building based on provided colors.")
#     return ENQUEUE









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
def process_images(coordinates_list, image_paths):
    # Initialize an empty queue
    queue = deque()
    results = [None] * len(image_paths)  # Preallocate list to store results
    normalized_coordinates = draw_street.normalize_coordinates(coordinates_list)  # Normalize all coordinates at once if possible
    last_non_enqueue_result = None  # Keep track of the last non-ENQUEUE result

    # Iterate over image paths and their corresponding coordinates
    for i, (coordinates, image_path) in enumerate(tqdm(zip(coordinates_list, image_paths), total=len(image_paths), desc="Processing Images")):
        outer_normal = draw_street.normalize_vector(draw_street.even_oriented(coordinates=normalized_coordinates, index=i))
        street_direction = draw_street.normalize_vector(draw_street.straight_oriented(coordinates=normalized_coordinates,index=i))
        result = decide_the_kind_of_building(image_path=image_path, normal_vector=outer_normal,street_direction=street_direction, color_thresholds=color_thresholds ,body_threshold=0.2,green_treshold=0.2)
        
        if result == "ENQUEUE":
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


def print_formatted_results(image_paths, results, file_name = "results" ,write_in_file = False):
    """
    Prints and writes formatted results of image processing to the console and a file.

    Args:
        image_paths (list): List of image file paths.
        results (list): List of results corresponding to each image.
        file_path (str): Path to the file where results will be written.
    """
    output = "\nResults for Image Processing:\n"
    output += "----------------------------------\n"
    for image_path, result in zip(image_paths, results):
        # Extract the basename of the image file
        basename = pathlib.Path(image_path).name
        output += f"{basename}:\n{result}\n"

    # Print to console
    if write_in_file:
        # Write to file
        with open(pathlib.Path(directory) / file_name, 'w') as file:
            file.write(output)
    else:
        print(output)





def check_street(directory ,coardinates,file_name = "results" ,write_in_file=True):
    image_paths = find_png_files_sorted(directory=directory)
    results = process_images(coordinates_list=coardinates , image_paths=image_paths)
    print_formatted_results(image_paths=image_paths,results=results,file_name=file_name,write_in_file = write_in_file)



    






if __name__ == "__main__":
    directory = "streets/רחוב יהודה המכבי/even"
    coardiantes = [(179735.0, 666798.0),(179751.0, 666795.0),(179773.0, 666792.0),(179885.0, 666791.0),(179902.0, 666788.0),(179925.0, 666786.0),(179952.0, 666783.0),(179978.0, 666782.0),(180012.0, 666785.0),(180049.0, 666784.0),(180108.0, 666775.0),(180159.0, 666785.0),(180181.0, 666785.0),(180198.0, 666787.0),(180231.0, 666787.0),(180242.0, 666786.0),(180254.0, 666786.0),(180274.0, 666786.0),(180311.0, 666787.0),(180333.0, 666787.0),(180352.0, 666787.0),(180427.0, 666733.0),(180465.0, 666794.0),(180475.0, 666796.0),(180488.0, 666797.0),(180495.0, 666798.0),(180486.0, 666794.0),(180515.0, 666801.0),(180527.0, 666803.0),(180535.0, 666803.0),(180577.0, 666811.0),(180589.0, 666816.0),(180599.0, 666816.0),(180607.0, 666818.0),(180630.0, 666826.0),(180639.0, 666828.0),(180650.0, 666831.0),(180660.0, 666832.0),(180690.0, 666840.0),(180703.0, 666845.0),(180735.0, 666856.0)       
    ]

    check_street(directory=directory,coardinates=coardiantes,write_in_file=True)












