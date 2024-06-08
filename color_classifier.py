import draw_street
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
import time
from sklearn.cluster import KMeans
import numpy as np
from PIL import ImageColor, Image  # Consider using scikit-image for potentially better performance



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
    # "square_line_turkiz" : (197, 248, 187) , 
    # "square_light_green": (222, 246, 152) ,
    "black" : (36, 38, 42) , 
    "red_train" : (208, 24, 18) , 
    "gray_train" : (200, 204, 203) , 
    
}


def distance_in_lab_space(color1, color2):
    """
    Calculates the perceptual distance between two colors using the CIELAB color space and the Delta E 2000 formula.

    Args:
        color1: A tuple representing an RGB color (R, G, B), values from 0 to 255.
        color2: A tuple representing another RGB color (R, G, B), values from 0 to 255.

    Returns:
        A float representing the Delta E (ΔE) distance between the colors.
    """
    # Convert RGB to LAB
    color1_rgb = sRGBColor(color1[0], color1[1], color1[2], is_upscaled=True)
    color2_rgb = sRGBColor(color2[0], color2[1], color2[2], is_upscaled=True)
    
    color1_lab = convert_color(color1_rgb, LabColor)
    color2_lab = convert_color(color2_rgb, LabColor)
   

    # Attempt to calculate Delta E using a try-except to handle potential issues with numpy.asscalar
    try:
        delta_e = delta_e_cie2000(color1_lab, color2_lab)
      
        return delta_e.item()  # Convert to Python scalar if necessary
    except AttributeError:
        # If numpy.asscalar is deprecated, this block handles conversion from numpy scalar
        try:
            return float(delta_e)
        except UnboundLocalError:
            # Handle the case where delta_e was never assigned due to an upstream error
            print("Failed to calculate delta E. Check color conversion.")
            return None



def color_classifier(color, epsilon = 30):
  """
  Classifies a color based on its distance to base colors in the CIELAB space.

  Args:
      color: A tuple representing an RGB color (R, G, B).
      base_colors: A dictionary mapping color names to RGB tuples.
      epsilon: A small threshold value for distance comparison.

  Returns:
      A string representing the closest base color name if the distance is
      within epsilon, otherwise returns "other".
  """

  closest_color = None
  min_distance = float('inf')  # Initialize with positive infinity
#   print("start color_classifier")
#   print(f"closest_color {closest_color} ,min_distance : {min_distance} , epsilon = {epsilon} ")


  for color_name, base_color in base_colors.items():

    distance = distance_in_lab_space(color, base_color)

    if distance < min_distance:
      min_distance = distance
      closest_color = color_name



#   print(f"closest_color {closest_color} ,min_distance : {min_distance} , epsilon = {epsilon} ")

  return closest_color if min_distance <= epsilon else "other"


# def calculate_color_percentages(image_path, base_colors, epsilon=30):
#     """
#     Optimized function to calculate the percentage of each base color in an image by first collecting unique colors.

#     Args:
#         image_path: The path to the image file.
#         base_colors: A dictionary mapping color names to RGB tuples.
#         epsilon: Threshold for deciding color match proximity.

#     Returns:
#         A dictionary mapping color names to their approximate percentages in the image (as floats between 0 and 1).
#     """
#     # Open the image and convert to RGB
#     start_time = time.time()  # Start timing

#     image = image_path.convert('RGB')
#     width, height = image.size

#     # Collect all unique colors and their counts
#     unique_colors = {}
#     for y in range(height):
#         for x in range(width):
#             pixel = image.getpixel((x, y))
#             if pixel in unique_colors:
#                 unique_colors[pixel] += 1
#             else:
#                 unique_colors[pixel] = 1

#     # Map each unique color to the closest base color
#     color_map = {}
#     for color in unique_colors:
#         closest_color_name = color_classifier(color, base_colors, epsilon=epsilon)
#         if closest_color_name in color_map:
#             color_map[closest_color_name] += unique_colors[color]
#         else:
#             color_map[closest_color_name] = unique_colors[color]

#     # Add 'other' key to handle any unmatched color explicitly if necessary
#     if 'other' not in color_map:
#         color_map['other'] = 0

#     # Calculate percentages
#     total_pixels = width * height
#     percentages = {color_name: count / total_pixels for color_name, count in color_map.items()}

    
#     end_time = time.time()  # End timing
#     print(f"Calculation took {end_time - start_time:.2f} seconds.") 

#     return percentages
def crop_image_center(image, crop_width, crop_height):
    """
    Crops an image around its center based on specified dimensions.

    Args:
        image_path (str): Path to the image file.
        crop_width (int): The width of the crop area.
        crop_height (int): The height of the crop area.

    Returns:
        PIL.Image: The cropped image.
    """
    # Load the image
    width, height = image.size

    # Calculate the center of the image
    center_x, center_y = width // 2, height // 2

    # Calculate the bounding box of the cropped area
    left = max(center_x - crop_width // 2, 0)
    right = min(center_x + crop_width // 2, width)
    top = max(center_y - crop_height // 2, 0)
    bottom = min(center_y + crop_height // 2, height)

    # Crop the image
    cropped_image = image.crop((left, top, right, bottom))

    return cropped_image


def downscale_image(image, scale_factor):
    """
    Scales down an image by a given factor using high-quality resampling.

    Args:
        image (PIL.Image): The original image.
        scale_factor (float): The factor by which the image dimensions should be reduced.

    Returns:
        PIL.Image: The downscaled image.
    """
    width, height = image.size
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    # Use LANCZOS resampling (also known as ANTIALIAS in older versions)
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    return resized


def apply_kmeans(image, num_clusters):
    """
    Applies k-means clustering to reduce the number of colors in an image.

    Args:
        image (PIL.Image): The input image to process.
        num_clusters (int): The number of color clusters to form, which corresponds to the number of unique colors in the output image.

    Returns:
        PIL.Image: An image where the original colors are replaced by the centroid of the clusters they belong to.
    """
    # Convert the image to numpy array for processing
    data = np.array(image)
    # Reshape the data into a two-dimensional array of (pixel_count, 3) where 3 represents RGB channels
    pixels = data.reshape((-1, 3))
    
    # Apply k-means clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(pixels)
    # Get the RGB values of the cluster centers (centroids)
    new_colors = kmeans.cluster_centers_.astype(int)
    
    # Replace each pixel's colors with the corresponding centroid color
    new_image_data = new_colors[kmeans.labels_].reshape(data.shape)
    
    # Convert the numpy array back to a PIL.Image object
    new_image = Image.fromarray(new_image_data.astype('uint8'), 'RGB')
    return new_image


def calculate_color_percentages(image, epsilon=30, scale_factor=0.5, num_clusters=10,crop_width = 400, crop_height = 400):
    print("calculating_color_percentages ")

    start_time = time.time()

    # Load and process image
    original_image = image.convert('RGB')

    print("cropping image") 
    cropped_image = crop_image_center(original_image,crop_width=crop_width , crop_height=crop_height)
    # scaled_image = downscale_image(original_image, scale_factor)
    # scaled_image.show()
    simplified_image = apply_kmeans(cropped_image, num_clusters)
    # simplified_image.show()
    print("kmeaned inage")

  
    width, height = simplified_image.size
    pixels = simplified_image.load()

    # Collect all unique colors and their counts
    unique_colors = {}
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            if pixel in unique_colors:
                unique_colors[pixel] += 1
            else:
                unique_colors[pixel] = 1

    # Map each unique color to the closest base color
    color_map = {}
    for color, count in unique_colors.items():
        closest_color_name = color_classifier(color, epsilon)
        if closest_color_name in color_map:
            color_map[closest_color_name] += count
        else:
            color_map[closest_color_name] = count

    # Handle any unmatched colors explicitly
    if 'other' not in color_map:
        color_map['other'] = 0

    # Calculate percentages
    total_pixels = width * height
    percentages = {color_name: count / total_pixels for color_name, count in color_map.items()}

    end_time = time.time()
    print(f"Calculation took {end_time - start_time:.2f} seconds.")
    return percentages


def filter_colors_precentage(precentages,trheshhold):
  filtered = {color_name : precentage for color_name, precentage in precentages.items() if precentage >= trheshhold}
  return filtered













if __name__ == "__main__":
    image_path = 'streets/רחוב ולנברג ראול/even/32.png'
    opened_image = image = Image.open(image_path)
    
    image = Image.open(image_path)
    center_x = image.width // 2
    center_y = image.height // 2
    center = (center_x,center_y)
    coardiantes = [(184566.0, 668294.0),(184536.0, 668275.0),(184486.0, 668242.0),(184051.0, 668226.0),(184005.0, 668237.0),(184595.0, 668320.0),(184620.0, 668340.0),(184647.0, 668358.0),(184673.0, 668388.0),(184698.0, 668403.0),(184752.0, 668469.0),(184779.0, 668499.0),(184810.0, 668533.0),(184849.0, 668496.0),(184855.0, 668583.0),(184898.0, 668645.0),(184919.0, 668665.0),(184979.0, 668739.0),(185003.0, 668799.0),(185062.0, 668891.0),(185050.0, 668923.0),(185132.0, 669001.0),(185244.0, 669170.0),(185258.0, 669189.0),(185352.0, 669273.0),(185594.0, 669404.0)]

    street = draw_street.normalize_coordinates(coardiantes)
       

    # hankin8_12 = draw_street.normalize_coordinates([(180282.0, 666326.0), (180291.0, 666364.0), (180299.0, 666391.0)])
    # print(dizengodff_150_158)
    outer_normal = draw_street.normalize_vector(draw_street.even_oriented(street,18))

    new_center = draw_street.square_center_after_moving_by_outer_normal(image=image,unit_vector=outer_normal,step_size=-0)

    cropped_image = draw_street.crop_image(image=image,p2=new_center,width=400,height=400)

    color_percentages = calculate_color_percentages(image=cropped_image,epsilon=30)

    print(color_percentages,"\n\n")
    filtered = filter_colors_precentage(color_percentages,trheshhold=0.08)
    print(filtered,"\n\n")















    
    




