import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
import math
import collections

def plot_coordinates(coordinates, filename='street_shape.png'):
    normalized = normalize_coordinates(coordinates)
    if not normalized:
        print("No coordinates to plot.")
        return
    try:
        x_values, y_values = zip(*normalized)
    except TypeError:
        print("Invalid format of coordinates.")
        return
    max_range = max(max(abs(x) for x in x_values), max(abs(y) for y in y_values))
    axis_limits = [-max_range, max_range]
    plt.figure(figsize=(10, 8))
    plt.scatter(x_values, y_values, c='blue', marker='o')
    plt.plot(x_values, y_values, c='red', marker='', linestyle='-')
    for index in range(len(normalized) - 1):  # Ensuring there's a next point
        add_perpendicular_vector(normalized, index)
    plt.title('Plot of Coordinates')
    plt.xlabel('X axis')
    plt.ylabel('Y axis')
    plt.xlim(axis_limits)
    plt.ylim(axis_limits)
    plt.gca().set_aspect('equal', adjustable='datalim')
    plt.grid(True)
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.savefig(filename, format='png', dpi=300, bbox_inches='tight')
    plt.show()
    plt.close()



def add_perpendicular_vector(coordinates, index):
    point = coordinates[index]
    if index < len(coordinates) - 1:
        next_point = coordinates[index + 1]
        vector = np.array([next_point[0] - point[0], next_point[1] - point[1]])
        perpendicular_vector = np.array([vector[1], -vector[0]])
        norm = np.linalg.norm(perpendicular_vector)
        if norm != 0:
            perpendicular_vector = perpendicular_vector / norm * 10
        plt.arrow(point[0], point[1], perpendicular_vector[0], perpendicular_vector[1],
                  head_width=2, head_length=3, fc='green', ec='green')
        






def even_oriented(coordinates, index):
    """ Return the perpendicular vector (y, -x) for even orientation. """
    if index < len(coordinates) - 1:  # Check if the next index exists
        point = coordinates[index]
        next_point = coordinates[index + 1]
        vector = (next_point[0] - point[0], next_point[1] - point[1])
        # Calculate the perpendicular vector (y, -x)
        perpendicular_vector = (vector[1], -vector[0])
        
        return perpendicular_vector
    else:
        return None  # No next point to define a vector

def odd_oriented(coordinates, index):
    """ Return the perpendicular vector (-y, x) for odd orientation. """
    if index < len(coordinates) - 1:  # Check if the next index exists
        point = coordinates[index]
        next_point = coordinates[index + 1]
        vector = (next_point[0] - point[0], next_point[1] - point[1])
        # Calculate the perpendicular vector (-y, x)
        perpendicular_vector = (-vector[1], vector[0])
        return perpendicular_vector
    else:
        return None  # No next point to define a 


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

def draw_line_on_image(image_path, unit_vector, line_length=20,wideness = 8):

    # Load the image
    image = Image.open(image_path)
    
    # Determine the center pixel coordinates based on image dimensions
    center_x = image.width // 2
    center_y = image.height // 2
    
    # Calculate the endpoint's coordinates
    end_x = int(center_x + unit_vector[0] * line_length)
    end_y = int(center_y + unit_vector[1] * line_length)
    
    # Draw a green line from the center to the calculated endpoint
    draw = ImageDraw.Draw(image)
    draw.line([(center_x, center_y), (end_x, end_y)], fill='green', width=wideness)
    
    # Display the image
    image.show()


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



def normalize_vector(vector):
    # Calculate the magnitude of the vector
    magnitude = math.sqrt(sum(x**2 for x in vector))
    
    # Avoid division by zero
    if magnitude == 0:
        raise ValueError("Cannot normalize a zero vector.")
    
    # Normalize each component of the vector
    normalized_vector = tuple(x / magnitude for x in vector)
    
    return normalized_vector

#example of usage:


def get_dominant_colors(image_path, p2, width, height):
    # Load the image
    image = Image.open(image_path)
    pixels = image.load()

    # Calculate the bounds of the rectangle centered at p2
    left = max(p2[0] - width // 2, 0)
    right = min(p2[0] + width // 2, image.width)
    top = max(p2[1] - height // 2, 0)
    bottom = min(p2[1] + height // 2, image.height)

    # Draw the rectangle on the image
    draw = ImageDraw.Draw(image)
    draw.rectangle([left, top, right, bottom], outline='red', width=3)

    # Collect colors within the rectangle
    color_counts = collections.Counter()
    for x in range(left, right):
        for y in range(top, bottom):
            color = pixels[x, y]
            color_counts[color] += 1

    # Get the three most common colors
    most_common_colors = color_counts.most_common(4)

    # Show and save the image with the rectangle
    image.show()
    image.save("output_with_rectangle.jpg")

    # Return the most common colors
    return [color for color, count in most_common_colors]




if __name__ == "__main__":
    pass
    
