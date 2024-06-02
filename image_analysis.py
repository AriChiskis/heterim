from PIL import Image
import numpy as np
import pandas as pd
import webcolors
import os

def closest_color(rgb):
    min_colors = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - rgb[0]) ** 2
        gd = (g_c - rgb[1]) ** 2
        bd = (b_c - rgb[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]



def get_dominant_color(image_path):
    with Image.open(image_path) as img:
        # Convert image to numpy array
        data = np.array(img)
        # Reshape data in the form of a list of RGB values
        data = data.reshape((-1, 3))
        # Find unique rows (colors) in the data and count their occurrences
        unique_colors, counts = np.unique(data, axis=0, return_counts=True)
        # Find the most dominant color
        dominant_color = unique_colors[np.argmax(counts)]
        # Find the closest color name
        closest_name = closest_color(dominant_color)
        return dominant_color, closest_name


def closest_color_from_colors_table(df, target_rgb):
    # Convert the 'rgb' column string into tuples of integers
    df['rgb_tuple'] = df['rgb'].apply(lambda x: tuple(map(int, x.split(', '))))
    
    # Calculate the Euclidean distance between the target_rgb and all RGBs in the dataframe
    df['distance'] = df['rgb_tuple'].apply(lambda rgb: np.sqrt(sum((x - y) ** 2 for x, y in zip(rgb, target_rgb))))
    
    # Find the row in DataFrame with the smallest distance
    closest_row = df.loc[df['distance'].idxmin()]
    
    # Return the type of the closest color

    return closest_row['transliteration']




def main(df):
    screenshot_path = 'screenshot.png'
    cropped_image_path = 'cropped_image.png'
    color_info_path = 'dominant_color.txt'

    # Crop the image as previously defined
    
    # Get the dominant color and its name
    dominant_color, color_name = get_dominant_color(cropped_image_path)
    print(f"Dominant Color in picutre: {dominant_color},\tColor Name: {color_name}")
    meaning_of_color = closest_color_from_colors_table(df,dominant_color)
    print(f"Meaning of Color from map: {meaning_of_color},\t\tColor Name: {color_name}")


    # Save the dominant color and its name to a text file
    with open(color_info_path, 'w') as file:
        file.write(f"Dominant Color RGB: {dominant_color}\nColor Name: {color_name}")
        print(f"Dominant color info saved to {color_info_path}")



# def process_images_in_folder(folder_path, df):
#     for filename in os.listdir(folder_path):
#         if filename.endswith(".png"):  # Check for PNG images
#             full_path = os.path.join(folder_path, filename)
#             dominant_color, color_name = get_dominant_color(full_path)
#             meaning_of_color = closest_color_from_colors_table(df, dominant_color)
            
#             # Print the results
#             print("\n\n")
#             print(f"Dominant Color in picture {filename}: {dominant_color},\tColor Name: {color_name}")
#             print(f"Meaning of Color from map: {meaning_of_color},\t\tColor Name: {color_name}")


def process_images_in_folder(folder_path, df_colors, df_addresses):
    # Ensure the predicted color column exists
    if 'predicted color' not in df_addresses.columns:
        df_addresses['predicted color'] = None

    for index, row in df_addresses.iterrows():
        # Formulate the filename from the street and number
        filename = f"רחוב {row['street']} {row['number']}.png"
        full_path = os.path.join(folder_path, filename)

        if os.path.exists(full_path):
            # If the file exists, process it to get the dominant color
            dominant_color, color_name = get_dominant_color(full_path)
            meaning_of_color = closest_color_from_colors_table(df_colors, dominant_color)

            # Update the DataFrame with the predicted color
            df_addresses.at[index, 'predicted color'] = meaning_of_color

            # Optionally print the results
            print(f"Dominant Color in picture {filename}: {dominant_color}, Color Name: {color_name}")
            print(f"Meaning of Color from map: {meaning_of_color}, Color Name: {color_name}")
        else:
            print(f"File not found: {full_path}")

    

    return df_addresses


if __name__ == '__main__':
    df_colors = pd.read_csv('colors.csv')
    pd_addresses = pd.read_csv("addresses.csv")
    projected_color_addresses = process_images_in_folder(r'map_colors_to_addresses',df_colors,pd_addresses)
    print(projected_color_addresses)
    projected_color_addresses.to_csv('projected_color_addresses.csv', encoding='utf-8', index=False)
