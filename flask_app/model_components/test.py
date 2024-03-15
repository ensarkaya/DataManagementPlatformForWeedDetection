import sys
import torch
import gc
from PIL import Image
from torchvision.transforms import ToPILImage, Resize
import torch.nn as nn
import os
import numpy as np
sys.path.append(os.path.dirname(__file__))
from model import ResNetUNet
from data_prep import get_data_loaders
from utils import calculate_metrics, cleanup_patch_files, cleanup_patch_files_by_identifier, determine_max_row_col, extract_image_identifier, map_color, extract_coordinates, stitch_patches_to_full_image_by_identifier

def stitch_patches_to_full_image(patch_dir, image_size, patch_size=256):
    """
    Stitch patches from patch_dir into a full-resolution image.
    
    Args:
        patch_dir (str): Directory containing patch predictions.
        image_size (tuple): The dimensions (height, width) of the full-resolution image.
        patch_size (int): Size of the patches (assumed square).
    
    Returns:
        np.array: The stitched full-resolution image.
    """
    # Initialize an empty array for the full-resolution image
    full_image = np.zeros((image_size[0], image_size[1], 3), dtype=np.uint8)

    # List all patch files
    patch_files = [f for f in os.listdir(patch_dir) if f.endswith('_predicted.png')]
    
    for patch_file in patch_files:
        # Extract patch coordinates from the file name
        coords = extract_coordinates(patch_file)
        
        # Load the patch image
        patch_image = np.array(Image.open(os.path.join(patch_dir, patch_file)))
        
        # Calculate the position in the full image
        start_y = coords[0] * patch_size
        start_x = coords[1] * patch_size
        
        # Place the patch in the corresponding position of the full_image
        full_image[start_y:start_y+patch_size, start_x:start_x+patch_size] = patch_image

    return full_image


def save_segmentation(images, masks, outputs, image_names, save_dir, n_images=1):
    with torch.no_grad():
        images = images.cpu()
        masks = masks.cpu()
        outputs = torch.argmax(outputs, dim=1).cpu()

        color_map = {
            0: [195, 195, 195],  # Background
            1: [31, 119, 189],   # Sorghum
            2: [255, 127, 14]    # Weeds
        }

        for i in range(n_images):
            # Correctly extracting base name, row index, and column index
            parts = image_names[i].split('_')
            base_name = '_'.join(parts[:-4])  # Everything except the last four elements
            row_index = parts[-3]  # Third last element
            col_index = parts[-2]  # Second last element

            # Construct filenames for saving using both row and column indices
            gt_filename = f'{base_name}_patch_{row_index}_{col_index}_groundtruth.png'
            pred_filename = f'{base_name}_patch_{row_index}_{col_index}_predicted.png'

            # Save ground truth mask with color mapping
            gt_mask_colored = map_color(masks[i].unsqueeze(0), color_map)
            gt_mask_image = Image.fromarray(gt_mask_colored)
            gt_mask_image.save(os.path.join(save_dir, gt_filename))

            # Save predicted mask with color mapping
            pred_mask_colored = map_color(outputs[i].unsqueeze(0), color_map)
            pred_mask_image = Image.fromarray(pred_mask_colored)
            pred_mask_image.save(os.path.join(save_dir, pred_filename))


def main():
    # Define the base path relative to the current working directory
    base_path = os.getcwd()

    image_path = os.path.join(base_path, '2024_01_15_initial_set_of_drone_images/img')
    mask_path = os.path.join(base_path, '2024_01_15_initial_set_of_drone_images/gt')
    test_image_path = os.path.join(base_path, '2024_01_15_initial_set_of_drone_images/test_img')
    test_mask_path = os.path.join(base_path, '2024_01_15_initial_set_of_drone_images/test_gt')
    model_path = os.path.join(base_path, 'models/best_model.pth')
    resnet_model_path = os.path.join(base_path, 'models/resnet34.pth')
    save_dir = os.path.join(base_path, 'generated_masks')

    # Ensure the directory for saving images exists
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    batch_size = 1

    # Assuming the model is intended to be in the same directory structure
    _, _, test_loader = get_data_loaders(image_path, mask_path, test_image_path, test_mask_path, batch_size=batch_size) 

    # Load Model
    model = ResNetUNet(n_classes=3, resnet_model_path=resnet_model_path)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    # Load saved model weights
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    model.load_state_dict(torch.load(model_path, map_location=device))

    # Model in evaluation mode
    model.eval()
    
    all_metrics = {
        'IoU': [],
        'Precision': [],
        'Recall': [],
        'F1': []
    }

    with torch.no_grad():
        #image_identifiers = set(extract_image_identifier(f) for f in os.listdir(save_dir) if f.endswith('_predicted.png'))
        for batch, (images, masks, image_names, coords) in enumerate(test_loader):
            images = images.to(device)
            masks = masks.to(device)
            outputs = model(images)

            metrics = calculate_metrics(outputs, masks, n_classes=3)
            # Save segmentation results
            save_segmentation(images, masks, outputs, image_names, save_dir, n_images=images.size(0))

            # Extract identifiers from image_names and add to the set
            # for name in image_names:
            #     image_identifiers.add(extract_image_identifier(name))
                
            for key in all_metrics:
                all_metrics[key].extend(metrics[key])

            # Optional: cleanup
            del images, masks, outputs
            gc.collect()

    # Print average metrics
    for key in all_metrics:
        average_metric = np.mean(all_metrics[key])
        print(f'Average {key}: {average_metric}')
    
    # Extract unique identifiers for all processed images based on saved patches
    image_identifiers = set(extract_image_identifier(f) for f in os.listdir(save_dir) if f.endswith('_predicted.png'))

    for identifier in image_identifiers:
        # Filter patch files for the current image based on the unique identifier
        patch_files = [f for f in os.listdir(save_dir) if f.startswith(identifier) and f.endswith('_predicted.png')]
        
        if not patch_files:
            print(f"No patch files found for stitching for image {identifier}.")
            continue
        
        # Determine the full image size from the patch files
        max_row, max_col = determine_max_row_col(patch_files)
        image_size = ((max_row + 1) * 256, (max_col + 1) * 256)
        
        # Stitch the patches together for the current image
        full_image = stitch_patches_to_full_image_by_identifier(save_dir, patch_files, image_size, patch_size=256)
        
        # Save the stitched image with a unique name to ensure no overwrites
        full_image_path = os.path.join(save_dir, f"{identifier}_stitched_full_image.png")
        Image.fromarray(full_image).save(full_image_path)

    # Cleanup: Remove the saved patches for the current image
    cleanup_patch_files(save_dir)


if __name__ == '__main__':
    main()

