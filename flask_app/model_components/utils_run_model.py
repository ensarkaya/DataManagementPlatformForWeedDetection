from skimage.io import imread
import numpy as np

def calculate_pixel_ratio(processed_image_path):
    # Load the image using scikit-image
    image_path = processed_image_path
    image = imread(image_path)

    # Define the RGB color codes for the classes
    colors = {
        'background': np.array([195, 195, 195]),
        'sorghum': np.array([31, 119, 189]),
        'weeds': np.array([255, 127, 14]),
    }

    # Initialize a dictionary to hold the count of pixels for each class
    class_pixel_count = {
        'background': 0,
        'sorghum': 0,
        'weeds': 0,
    }

    # Let's first check the shape of the image to ensure it's in the expected format
    image_shape = image.shape

    # Display the shape of the image and also check if the image has an alpha channel
    image_shape, image[0,0,:], np.unique(image.reshape(-1, image.shape[2]), axis=0)

    # Adjust the colors to ignore the alpha channel and account for slight variations in color
    def count_pixels(image, color):
        # Create a mask that matches the color within a tolerance
        color_mask = np.all(np.abs(image[:, :, :3] - color[:3]) <= 10, axis=-1)
        return np.sum(color_mask)

    # Recalculate the pixel counts for each class
    class_pixel_count = {class_name: count_pixels(image, color) for class_name, color in colors.items()}

    # Calculate total number of pixels
    total_pixels = image_shape[0] * image_shape[1]

    # Calculate the percentage of each class in the image
    class_percentage = {class_name: (pixel_count / total_pixels) * 100 for class_name, pixel_count in class_pixel_count.items()}

    return class_percentage
