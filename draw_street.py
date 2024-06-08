import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
import math
import collections
from sklearn.cluster import KMeans
import webcolors
import pandas as pd

import numpy as np
import matplotlib.pyplot as plt

import numpy as np
import matplotlib.pyplot as plt

def plot_coordinates(coordinates1, coordinates2, filename='street_shape.png'):
    # Normalize coordinates and prepare plots for two different lists
    normalized1 = normalize_coordinates(coordinates1)
    normalized2 = normalize_coordinates(coordinates2)
    if not normalized1 and not normalized2:
        print("No coordinates to plot.")
        return
    plt.figure(figsize=(10, 8))
    
    # Process each list of coordinates
    for normalized, color, direction in [(normalized1, 'blue', 1), (normalized2, 'orange', -1)]:
        if normalized:
            try:
                x_values, y_values = zip(*normalized)
                plt.scatter(x_values, y_values, c=color, marker='o')
                plt.plot(x_values, y_values, c=color, linestyle='-')
                for index in range(len(normalized) - 1):
                    add_perpendicular_vectors(normalized, index, direction)
            except TypeError:
                print("Invalid format of coordinates.")
                return
    
    plt.title('Plot of Coordinates')
    plt.xlabel('X axis')
    plt.ylabel('Y axis')
    set_plot_limits(normalized1, normalized2)
    plt.gca().set_aspect('equal', adjustable='datalim')
    plt.grid(True)
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.savefig(filename, format='png', dpi=300, bbox_inches='tight')
    plt.show()
    plt.close()

def set_plot_limits(coordinates1, coordinates2):
    # Gather all coordinates for setting plot limits
    all_coords = coordinates1 + coordinates2
    x_values, y_values = zip(*all_coords)
    max_range = max(max(abs(x) for x in x_values), max(abs(y) for y in y_values))
    axis_limits = [-max_range, max_range]
    plt.xlim(axis_limits)
    plt.ylim(axis_limits)

def add_perpendicular_vectors(coordinates, index, direction):
    point = coordinates[index]
    if index < len(coordinates) - 1:
        next_point = coordinates[index + 1]
        vector = np.array([next_point[0] - point[0], next_point[1] - point[1]])
        if direction == 1:
            perpendicular_vector = np.array([vector[1], -vector[0]])  # Normal direction
        else:
            perpendicular_vector = np.array([-vector[1], vector[0]])  # Inverted direction
        
        norm = np.linalg.norm(perpendicular_vector)
        if norm != 0:
            perpendicular_vector = perpendicular_vector / norm * 30  # Scale the vector for visibility
        plt.arrow(point[0], point[1], perpendicular_vector[0], perpendicular_vector[1], 
                  head_width=2, head_length=3, fc='green', ec='green')

def even_oriented(coordinates, index):
    """ Return the perpendicular vector (y, -x) for even orientation. """
    size = len(coordinates)
    if index < size - 1:  # Check if the next index exists
        point = coordinates[index]
        next_point = coordinates[index + 1]
        vector = (next_point[0] - point[0], next_point[1] - point[1])
        # Calculate the perpendicular vector (y, -x)
        perpendicular_vector = (vector[1], -vector[0])
        
        return perpendicular_vector
    else:
        """
        if you have reahced the last point meaning coordinates[size -1]
        then take the outer normal of coordinates[size - 1] - coordinates[ size - 2]"""
        
        point = coordinates[size - 2]
        next_point = coordinates[size - 1]
        vector = (next_point[0] - point[0], next_point[1] - point[1])
        perpendicular_vector = (vector[1], -vector[0])
        return perpendicular_vector
    

def straight_oriented(coordinates, index):
    """ Return the perpendicular vector (y, -x) for even orientation. """
    size = len(coordinates)
    if index < size - 1:  # Check if the next index exists
        point = coordinates[index]
        next_point = coordinates[index + 1]
        vector = (next_point[0] - point[0], next_point[1] - point[1])
        return vector
    else:
        """
        if you have reahced the last point meaning coordinates[size -1]
        then take the outer normal of coordinates[size - 1] - coordinates[ size - 2]"""
        
        point = coordinates[size - 2]
        next_point = coordinates[size - 1]
        vector = (next_point[0] - point[0], next_point[1] - point[1])
        return vector
    
def odd_oriented(coordinates, index):
    """ Return the perpendicular vector (-y, x) for odd orientation. """
    size = len(coordinates)
    if index < size - 1:  # Check if the next index exists
        point = coordinates[index]
        next_point = coordinates[index + 1]
        vector = (next_point[0] - point[0], next_point[1] - point[1])
        # Calculate the perpendicular vector (-y, x)
        perpendicular_vector = (-vector[1], vector[0])
        return perpendicular_vector
    else:
        """if you have reahced the last point meaning coordinates[size -1]
        then take the outer normal of coordinates[size - 1] - coordinates[ size - 2]"""
        point = coordinates[size - 2]
        next_point = coordinates[size - 1]
        # Calculate the perpendicular vector (-y, x)
        vector = (next_point[0] - point[0], next_point[1] - point[1])
        perpendicular_vector = (-vector[1], vector[0])
        return perpendicular_vector

def straight_oriented(coordinates,index):
    size = len(coordinates)
    if index < size - 1:  # Check if the next index exists
        point = coordinates[index]
        next_point = coordinates[index + 1]
        vector = (next_point[0] - point[0], next_point[1] - point[1])

        return vector
    else:
        """if you have reahced the last point meaning coordinates[size -1]
        then take the outer normal of coordinates[size - 1] - coordinates[ size - 2]"""
        point = coordinates[size - 2]
        next_point = coordinates[size - 1]
        # Calculate the perpendicular vector (-y, x)
        vector = (next_point[0] - point[0], next_point[1] - point[1])
        return vector

def normalize_coordinates(coordinates):
    # Get the first point's x and y coordinates
    first_x, first_y = coordinates[0] 

    # Subtract the first point's coordinates from each coordinate
    normalized = [(x - first_x, y - first_y) for x, y in coordinates]
  
    return normalized


def draw_arrow(image_path, base_point, direction_vector, arrow_color="red", arrow_length=100):
    """
        Function: draw_arrow
    Description
    This function draws an arrow on an image from a specified base point in a given direction. The arrow consists of a main line and a head, and is useful for visualizing vectors or pointing out specific parts of an image.

    Parameters
    image_path (str): The path to the image file on which the arrow will be drawn. The image must be in a format that Pillow supports (e.g., JPG, PNG).
    base_point (tuple of int): A tuple specifying the (x, y) coordinates of the starting point of the arrow in pixel values.
    direction_vector (tuple of int): A tuple representing the vector (dx, dy) that defines the direction and length of the arrow from the base point.
    arrow_color (str, optional): The color of the arrow. Default is "red". Color can be specified as a named color that Pillow recognizes or as RGB tuples.
    arrow_length (int, optional): The length of the arrow line in pixels. Default is 100. This parameter controls the length of the main line of the arrow.
    Returns
    This function does not return any value. It directly modifies the image by drawing an arrow and displays the modified image. Optionally, the image can be saved after modification by uncommenting the image.save() line in the function.
        """
    # Load the image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Calculate the end point of the arrow
    end_point = (base_point[0] + direction_vector[0], base_point[1] + direction_vector[1])

    # Draw the main line of the arrow
    draw.line([base_point, end_point], fill=arrow_color, width=5)

    # Drawing the arrow head
    # Calculate the angle of the arrow
    import math
    angle = math.atan2(direction_vector[1], direction_vector[0])

    # Determine the points of the arrow head
    arrow_head_length = 20  # Length of the arrow head lines
    left_angle = angle + math.pi / 6
    right_angle = angle - math.pi / 6

    left_point = (end_point[0] + arrow_head_length * math.cos(left_angle),
                  end_point[1] + arrow_head_length * math.sin(left_angle))
    right_point = (end_point[0] + arrow_head_length * math.cos(right_angle),
                   end_point[1] + arrow_head_length * math.sin(right_angle))

    # Draw the arrow head
    draw.line([end_point, left_point], fill=arrow_color, width=5)
    draw.line([end_point, right_point], fill=arrow_color, width=5)

    # Save or display the modified image
    image.show()
    # image.save('output_image.png')  # Optionally save the modified image


def draw_dot_on_image(image_path, unit_vector, step_size = 5,wideness = 8):
    try:
        # Load the image
        image = Image.open(image_path)
    except IOError:
        print("Error: The image could not be opened. Check the file path.")
        return

    # Determine the center pixel coordinates based on image dimensions
    center_x = image.width // 2
    center_y = image.height // 2
    
    # Calculate the new point's coordinates
    new_x = int(center_x + unit_vector[0] * step_size)
    new_y = int(center_y + unit_vector[1] * step_size)
    print(new_x , new_y)


    
    
    # Check if new coordinates are within the image dimensions
    if not (0 <= new_x < image.width and 0 <= new_y < image.height):
        print("Error: Calculated coordinates are outside the image boundaries.")
        return

    # Draw a larger, contrasting color dot at the new location
    radius = 20  # Increased radius of the dot
    draw = ImageDraw.Draw(image)
    draw.line([(center_x, center_y), (new_x, new_y)], fill='green', width=wideness)
    draw.ellipse([(new_x - radius, new_y - radius), (new_x + radius, new_y + radius)], fill='blue')
    
    # Save the image or display it
    image.show()
    # Optionally save to a file to inspect
    image.save("output_image.jpg")
    return (new_x,new_y)


def square_center_after_moving_by_outer_normal(image,unit_vector,step_size):
    center_x = image.width // 2
    center_y = image.height // 2
    
    # Calculate the new point's coordinates
    new_x = int(center_x + unit_vector[0] * step_size)
    new_y = int(center_y   - unit_vector[1] * step_size)
    return new_x , new_y


def normalize_vector(vector):
    # Calculate the magnitude of the vector
    magnitude = math.sqrt(sum(x**2 for x in vector))
    
    # Avoid division by zero
    if magnitude == 0:
        raise ValueError("Cannot normalize a zero vector.")
    
    # Normalize each component of the vector
    normalized_vector = tuple(x / magnitude for x in vector)
    
    return normalized_vector


def crop_image(image, p2, width, height):
    # Load the image
    # image = Image.open(image_path)
    pixels = image.load()

    # Calculate the bounds of the rectangle centered at p2
    left = max(p2[0] - width // 2, 0)
    right = min(p2[0] + width // 2, image.width)
    top = max(p2[1] - height // 2, 0)
    bottom = min(p2[1] + height // 2, image.height)

    # Draw the rectangle on the image
    draw = ImageDraw.Draw(image)
    # draw.rectangle([left, top, right, bottom], width=3)
    # image.show()

    # Show and save the image with the rectangle
    cropped_image = image.crop((left, top, right, bottom))
    # cropped_image.show()
    cropped_image.save("cropped_output.jpg")
    # image.save("output_with_rectangle.jpg")

    return cropped_image


# def reduce_to_n_colors(image,n):
#     # Load the image and convert it to RGB if it's not
#     rgb_image = image.convert('RGB')

#     # Convert the image data to a list of RGB values
#     np_image = np.array(rgb_image)
#     pixels = np_image.reshape((-1, 3))

#     # Perform k-means clustering to find four dominant colors
#     kmeans = KMeans(n_clusters=n)
#     kmeans.fit(pixels)
#     dominant_colors = kmeans.cluster_centers_.astype(int)

#     # Map each pixel to the nearest dominant color
#     labels = kmeans.labels_
#     new_pixels = dominant_colors[labels].reshape(np_image.shape)

#     # Convert the array back to an Image object and save or display it
#     new_image = Image.fromarray(np.uint8(new_pixels))
#     # new_image.show()
#     new_image.save("reduced_colors_output.jpg")

#     return dominant_colors


def reduce_to_n_colors(image, n):
    # Load the image and convert it to RGB if it's not
    rgb_image = image.convert('RGB')

    # Convert the image data to a list of RGB values
    np_image = np.array(rgb_image)
    pixels = np_image.reshape((-1, 3))

    # Perform k-means clustering to find n dominant colors
    kmeans = KMeans(n_clusters=n)
    kmeans.fit(pixels)
    dominant_colors = kmeans.cluster_centers_.astype(int)

    # Map each pixel to the nearest dominant color
    labels = kmeans.labels_
    new_pixels = dominant_colors[labels].reshape(np_image.shape)

    # Convert the array back to an Image object and save or display it
    new_image = Image.fromarray(np.uint8(new_pixels))
    new_image.save("reduced_colors_output.jpg")

    # Count the occurrences of each color label
    total_pixels = labels.size
    label_counts = collections.Counter(labels)
    
    # Sort the dominant colors by their counts in descending order and calculate percentages
    # sorted_dominant_colors_with_percents = [
    #     (dominant_colors[label], count / total_pixels * 100) for label, count in label_counts.most_common()
    # ]

    # Create two lists for colors and their corresponding percentages
    colors_list = []
    percentages_list = []

    # Fill the lists with sorted data
    for label, count in label_counts.most_common():
        colors_list.append(tuple(dominant_colors[label]))
        percentages_list.append(count / total_pixels * 100)

    return colors_list, percentages_list


def closest_color(requested_color):
    min_colors = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]


def get_color_name(rgb_color):
    try:
        # Try to get the exact name
        color_name = webcolors.rgb_to_name(rgb_color)
    except ValueError:
        # If the color is not defined, get the closest color name
        color_name = closest_color(rgb_color)
    return color_name


def get_center_pixel_color(image):
    # Load the image
    pixels = image.load()

    # Calculate the center coordinates
    center_x = image.width // 2
    center_y = image.height // 2

    # Get the color of the center pixel
    center_pixel_color = pixels[center_x, center_y]

    return center_pixel_color



if __name__ == "__main__":
    odd = [(183998.0, 668298.0),(184019.0, 668292.0),(184253.0, 668234.0),(184586.0, 668377.0),(184348.0, 668238.0),(184608.0, 668394.0),(185070.0, 669050.0),(185339.0, 669288.0),(185226.0, 669233.0),(185262.0, 669264.0),(185253.0, 669370.0),(185311.0, 669301.0),(185294.0, 669311.0),(185361.0, 669332.0),(185374.0, 669345.0),(185408.0, 669372.0),(185442.0, 669383.0) ] 
    even = [(184566.0, 668294.0),(184536.0, 668275.0),(184486.0, 668242.0),(184051.0, 668226.0),(184005.0, 668237.0),(184595.0, 668320.0),(184620.0, 668340.0),(184647.0, 668358.0),(184673.0, 668388.0),(184698.0, 668403.0),(184752.0, 668469.0),(184779.0, 668499.0),(184810.0, 668533.0),(184849.0, 668496.0),(184855.0, 668583.0),(184898.0, 668645.0),(184919.0, 668665.0),(184979.0, 668739.0),(185003.0, 668799.0),(185062.0, 668891.0),(185050.0, 668923.0),(185132.0, 669001.0),(185244.0, 669170.0),(185258.0, 669189.0),(185352.0, 669273.0),(185594.0, 669404.0) ] 
    plot_coordinates(coordinates1=odd,coordinates2=even)


