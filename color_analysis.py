import draw_street
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

banana_color = (253, 220, 151)
light_yellow = (254, 254, 152)
maccab_yellow = (254, 254, 25)

orange = (253, 118, 21)

purple_1 = (209, 147, 253)
purple_2 = (195, 61, 253)
purple_3 = (114, 25, 214)

pink_flower_color = (253, 146, 149)
pink_flower_color = (253, 146, 149)

pink = (253, 147, 153)


red_flower_color = (253, 70, 77)

banana_2 = (253, 220, 151)
black_map_color = (36, 38, 40)
purple_map_color = (209, 147, 253)
pink_flower_color = (253, 146, 149)
red_flower_color = (253, 70, 77)


orange_map_color = (253, 118, 21)
orange_2 = (238, 127, 55)
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
                  orange_map_color, orange_2 , 
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


# Dictionary with keys as tuples of color names and values as descriptions, all with each word starting with a capital letter
color_combinations = {
    ('Orange', 'Pink Flower', 'Purple', 'Red Flower'): 'Purple Flower In Orange',
    ('Orange', 'Pink Flower', 'Purple'): 'Purple Flower In Orange',
    ('Orange', 'Purple', 'Red Flower'): 'Purple Flower In Orange',
    ('Orange','Purple'): 'Purple In Orange',
    ('Orange') : 'Orange',
    ('Orange','Red Flower'): 'Purple Flower In Orange',
    ('Orange',' Pink Flower'): 'Purple Flower In Orange',
    ('Brown') : 'Brown' , 
    ('Light Yellow') : 'Light Yellow'  , 
    ('Yellow') : ('Yellow')   , 
    ('Yellow' , 'Light Yellow') : 'Edge In Yellow , Light Yellow' , 
    ('Orange , Yellow') : 'Edge In Orange , Yellow' 

      

    
}




def find_closest_colors(colors, dataset_colors):
    """
    Find the closest color in dataset_colors for each color in the colors array.

    Args:
    colors (list of tuples): List of RGB colors (e.g., [(255, 100, 50), (0, 0, 255)])
    dataset_colors (list of tuples): List of RGB colors in the dataset.

    Returns:
    list: A list of RGB tuples where each tuple is the closest color from the dataset
          for the corresponding color in the input list. 
    """
    # Convert lists to numpy arrays for vectorized operations
    colors = np.array(colors)
    dataset_colors = np.array(dataset_colors)
    
    closest_colors = []

    print("Starting to find closest colors...")
    # Iterate over each color in the input list

    for color in colors:
        # print(f"Analyzing color: {color}")
        # Compute the Euclidean distance between the color and each color in the dataset
        distances = np.sqrt(np.sum((dataset_colors - color) ** 2, axis=1))
        # print(f"Distances from color {color} to each dataset color: {distances}")

        # Find the index of the smallest distance
        closest_color_index = np.argmin(distances)
        # print(f"Closest color index for {color}: {closest_color_index}")
        
        # Append the closest color to the result list
        closest_color = tuple(dataset_colors[closest_color_index])
        print(f"Closest color to {color} is {closest_color}")
        closest_colors.append(closest_color)
    print(f"closest_colors is {closest_colors}")

    # print("Finished finding closest colors.")
    return closest_colors


def create_color_percentage_dataframe(colors, percentages):
    """
    Create a DataFrame that aggregates the total percentages for each unique color and includes a column for names based on pre-defined color combinations.

    Args:
    colors (list of tuples): List of RGB colors (e.g., [(255, 100, 50), (0, 0, 255)])
    percentages (list of floats): List of percentages corresponding to each color.

    Returns:
    DataFrame: A pandas DataFrame with columns 'Color', 'Total Percentage', and 'Name', showing the aggregated percentage for each unique color and the associated name.
    """
    # Create a DataFrame from the colors and percentages
    df = pd.DataFrame({
        'Color': [str(color) for color in colors],  # Convert colors to string to use them as keys
        'Percentage': percentages
    })

    # Group by 'Color' and sum the 'Percentage'
    result_df = df.groupby('Color', as_index=False).sum()

    # Color to name mapping based on predefined combinations
    color_to_name = {
        '(209, 147, 253)': 'Purple',
        '(253, 146, 149)': 'Pink Flower',
        '(253, 70, 77)': 'Red Flower',

        '(253, 118, 21)': 'Orange',
        '(238, 127, 55)' : 'Orange' , 
        '(125, 71, 25)':'dark_road_on_orange',
        '(145, 78, 24)' : 'semi_dark_road_on_orange',
        '(197, 121, 37)': 'light_road_on_orange',

        '(253, 220, 151)': 'Banana',
         '36, 38, 40)': ' black_map_color', #edge  on banana road

        '(254, 254, 152)':'Light Yellow',
        '(73, 82, 51)': 'dark_road_on_light_yellow',
        '164, 166, 107': 'mid_dark_road_on_light_yellow',
        '(108, 113, 74)': 'semi_dark_road_on_light_yellow' , 

        '(164, 81, 57)' : 'Brown' , 
        '(102, 65, 55)' :'dark_brown_road' , 
        '(133, 87, 73)' : 'light_brown_road' , 

        '(90, 210, 20)' : 'light_green' , 
        '(25, 63, 26)' : 'dark_green' , 
        '(152, 143, 37)' :'kaki_green' , 

        '(49, 65, 175)' : 'dark_blue' , 
        
        '(56, 24, 23)' : 'very_dark_brown' , 
        '(254, 254, 25)' : 'Yellow' , 
        '(252, 253, 18)' : 'Yellow' , 
        '(89, 93, 23)' : 'mustard_road_on_yellow' , 
        '(230, 235, 58)' : 'semi_road_on_yellow'



        

    }

    # Map colors to names
    result_df['Name'] = result_df['Color'].map(color_to_name)

    # Sort by 'Total Percentage' in descending order (optional)
    result_df = result_df.sort_values(by='Percentage', ascending=False).reset_index(drop=True)

    return result_df


def filter_and_sort_names_by_percentage(df, threshold):
    """
    Filters a DataFrame for names where the percentage is above a specific threshold
    and returns a tuple of sorted, unique names.

    Args:
    df (pandas.DataFrame): DataFrame with columns 'Percentage' and 'Name'.
    threshold (float): The percentage threshold to filter the names by.

    Returns:
    tuple: A tuple containing the names sorted lexicographically that have a percentage above the threshold.
    """
    # Filter the DataFrame where 'Percentage' is greater than the threshold
    filtered_df = df[df['Percentage'] > threshold]
    
    # Get unique names from the filtered DataFrame
    unique_names = filtered_df['Name'].unique()
    
    # Sort the names lexicographically
    sorted_names = sorted(unique_names)
    
    # Convert the sorted names to a tuple
    return tuple(sorted_names)


def remove_color_rows(df, colors_to_remove):
    """
    Removes rows from a DataFrame based on an array of RGB colors.

    Args:
    df (pandas.DataFrame): DataFrame with a column named 'Color' that contains RGB tuples.
    colors_to_remove (list of tuples): List of RGB tuples to be removed from the DataFrame.

    Returns:
    pandas.DataFrame: A DataFrame that does not include rows with the specified colors.
    """
    # Ensure the 'Color' column contains tuples for comparison
    df['Color'] = df['Color'].apply(lambda x: tuple(x) if isinstance(x, list) else x)
    print(df)

    # Convert the list of colors to remove into a set for faster lookup
    colors_to_remove_set = set([str(color) for color in colors_to_remove])
    # Filter the DataFrame to exclude the specified colors
    filtered_df = df[~df['Color'].isin(colors_to_remove_set)]
 
    return filtered_df


def get_center_pixel_color(image):
    # Load the image
    pixels = image.load()

    # Calculate the center coordinates
    center_x = image.width // 2
    center_y = image.height // 2

    # Get the color of the center pixel
    center_pixel_color = pixels[center_x, center_y]

    return center_pixel_color


def color_image_classification(image,colors_to_avoid,dataset_colors,treshhold=5):
    kmeans_colors , precentages = draw_street.reduce_to_n_colors(image,4)
    dataset_colors = find_closest_colors(kmeans_colors,dataset_colors)
    # print(dataset_colors)
    prcantage_colors_df = create_color_percentage_dataframe(dataset_colors,precentages)
    filtered = remove_color_rows(prcantage_colors_df,colors_to_avoid)
    color_classification = filter_and_sort_names_by_percentage(filtered,treshhold)
    return color_classification


####################################################
def black_map_case(image,colors_to_avoid,dataset_colors,outer_normal):
    square_center = draw_street.square_center_after_moving_by_outer_normal(image,outer_normal,step_size=250)
    cropped_image = draw_street.crop_image(image,square_center,300,300)

    classification = color_image_classification(cropped_image,colors_to_avoid,dataset_colors)
    return classification

def banana_case(image,dataset_colors,colors_to_avoid,outer_normal):
    square_center = draw_street.square_center_after_moving_by_outer_normal(image,outer_normal,step_size=300)
    cropped_image = draw_street.crop_image(image,square_center,350,350)

    classification = color_image_classification(cropped_image,colors_to_avoid,dataset_colors)
    return classification

def purple_color_case(image,dataset_colors,colors_to_avoid,outer_normal):
    square_center = draw_street.square_center_after_moving_by_outer_normal(image,outer_normal,step_size=200) # good
    cropped_image = draw_street.crop_image(image,square_center,250,250)

    classification = color_image_classification(cropped_image,colors_to_avoid,dataset_colors)
    return classification

def pink_flower_color_case(image,dataset_colors,colors_to_avoid,outer_normal):
    square_center = draw_street.square_center_after_moving_by_outer_normal(image,outer_normal,step_size=200)
    cropped_image = draw_street.crop_image(image,square_center,250,250)

    classification = color_image_classification(cropped_image,colors_to_avoid,dataset_colors)
    return classification

def red_flower_color_case(image,dataset_colors,colors_to_avoid,outer_normal):
    square_center = draw_street.square_center_after_moving_by_outer_normal(image,outer_normal,step_size=200)
    cropped_image = draw_street.crop_image(image,square_center,250,250)

    classification = color_image_classification(cropped_image,colors_to_avoid,dataset_colors)
    return classification

def orange_color_case(image,dataset_colors,colors_to_avoid,outer_normal):
    square_center = draw_street.square_center_after_moving_by_outer_normal(image,outer_normal,step_size=0)
    cropped_image = draw_street.crop_image(image,square_center,250,250)
 
    # cropped_image = draw_street.crop_image(image,square_center,250,250)
    classification = color_image_classification(cropped_image,colors_to_avoid,dataset_colors)
    return classification
####################################################

"""neeed to do it # to do איש יקר"""
def case_classification(image,dataset_colors,colors_to_avoid,outer_normal):
    color_center = get_center_pixel_color(image)  # todo change it from one pixel to neiberhoud
    data_set_color = find_closest_colors(colors = [color_center],dataset_colors=dataset_colors)[0] #garbage
    print(f"center is: {data_set_color}")
    if data_set_color == banana_color:
        print(1)
        return banana_case(image,dataset_colors,colors_to_avoid,outer_normal)
    
    if data_set_color == black_map_color:
        print(2)
        return black_map_case(image,dataset_colors,colors_to_avoid,outer_normal)
    
    if data_set_color == purple_map_color:
        print(3)
        return purple_color_case(image,dataset_colors,colors_to_avoid,outer_normal)
    
    if data_set_color == pink_flower_color:
        print(4)
        return pink_flower_color_case(image,dataset_colors,colors_to_avoid,outer_normal)
    
    if data_set_color == red_flower_color:
        print(5)
        return red_flower_color_case(image,dataset_colors,colors_to_avoid,outer_normal)
    
    if data_set_color == orange_map_color:
        print(6)
        return orange_color_case(image,dataset_colors,colors_to_avoid,outer_normal)
    else:
        black_map_case(image,dataset_colors,colors_to_avoid,outer_normal)
        
    

    
    





    