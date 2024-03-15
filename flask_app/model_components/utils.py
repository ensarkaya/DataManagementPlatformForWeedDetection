import gc
import os
import numpy as np
from skimage.io import imread, imsave
import torch
from PIL import Image
from torch.cuda.amp import GradScaler
import tqdm

from hyperparameter_tuning import save_hyperparams_and_scores_to_csv

def pad_array(array, patch_size, pad_value=0):
    """
    Pad the array to the specified patch size. Handles both 2D and 3D arrays.

    Parameters:
    - array: Input array to be padded.
    - patch_size: The desired patch size (assumed to be square).
    - pad_value: Padding value to be used.

    Returns:
    - Padded array.
    """
    # Calculate the padding amounts
    pad_height = patch_size - array.shape[0]
    pad_width = patch_size - array.shape[1]
    
    # Apply different padding based on the dimensionality of the array
    if array.ndim == 3:  # For 3D arrays (e.g., RGB images)
        return np.pad(array, ((0, pad_height), (0, pad_width), (0, 0)), mode='constant', constant_values=pad_value)
    elif array.ndim == 2:  # For 2D arrays (e.g., masks)
        return np.pad(array, ((0, pad_height), (0, pad_width)), mode='constant', constant_values=pad_value)
    else:
        raise ValueError("Unsupported array dimensionality for padding.")
    
def is_patch_relevant(mask_patch):
    sorghum_color_1, sorghum_color_2, weed_color = np.array([31, 119, 180]), np.array([31, 119, 189]), np.array([255, 127, 14])
    return np.any(np.all(mask_patch == sorghum_color_1, axis=-1)) or np.any(np.all(mask_patch == sorghum_color_2, axis=-1)) or np.any(np.all(mask_patch == weed_color, axis=-1))

def safe_imsave(path, image):
    try:
        imsave(path, image, check_contrast=False)
    except Exception as e:
        print(f"Error saving image {path}: {e}")

def rgb_to_index(mask, tolerance=10):  
    """Convert RGB mask to class index mask."""  
    index_mask = np.zeros(mask.shape[:2], dtype=np.uint8)  # Initialize index mask

    # Background
    background_color = np.array([195, 195, 195])
    index_mask[np.all(np.abs(mask - background_color) <= tolerance, axis=-1)] = 0

    # Sorghum (updated color)
    sorghum_color = np.array([31, 119, 180])
    index_mask[np.all(np.abs(mask - sorghum_color) <= tolerance, axis=-1)] = 1

    # Weeds
    weed_color = np.array([255, 127, 14])
    index_mask[np.all(np.abs(mask - weed_color) <= tolerance, axis=-1)] = 2

    return index_mask

def calculate_metrics(outputs, masks, n_classes):
    # Convert outputs to binary format
    preds = torch.argmax(outputs, dim=1)
    metrics = {
        'IoU': [],
        'Precision': [],
        'Recall': [],
        'F1': []
    }
    
    for cls in range(n_classes):
        pred_cls = preds == cls
        mask_cls = masks == cls

        intersection = (pred_cls & mask_cls).float().sum()
        union = (pred_cls | mask_cls).float().sum()
        iou = (intersection + 1e-6) / (union + 1e-6)
        
        precision = (intersection + 1e-6) / (pred_cls.float().sum() + 1e-6)
        recall = (intersection + 1e-6) / (mask_cls.float().sum() + 1e-6)
        f1 = 2 * (precision * recall) / (precision + recall + 1e-6)

        metrics['IoU'].append(iou.item())
        metrics['Precision'].append(precision.item())
        metrics['Recall'].append(recall.item())
        metrics['F1'].append(f1.item())

    return metrics

def map_color(mask, color_map):
    """ Map class labels to RGB colors """
    colored_mask = np.zeros((mask.shape[1], mask.shape[2], 3), dtype=np.uint8)

    for cls, color in color_map.items():
        colored_mask[mask[0] == cls] = color

    return colored_mask

def extract_coordinates(patch_file_name):
    """
    Extract the row and column indices from the patch file name.
    Filename format is 'img_20210903_D1_3_patch_ROW_COL_predicted'.
    
    Args:
        patch_file_name (str): The name of the patch file.
    
    Returns:
        tuple: Coordinates (row, col) indicating the patch's position.
    """
    # Split the filename by underscores
    parts = patch_file_name.split('_')
    # Find the indices of "patch" and "predicted" to correctly extract row and column indices
    try:
        patch_index = parts.index('patch')
        # The row and column indices are right after 'patch'
        row_idx = int(parts[patch_index + 1])
        col_idx = int(parts[patch_index + 2])
    except ValueError as e:
        raise ValueError(f"Error extracting coordinates from filename '{patch_file_name}': {e}")
    
    return (row_idx, col_idx)

def cleanup_patch_files(directory):
    """
    Remove patch files from the specified directory.

    Args:
        directory (str): Directory from which patch files will be deleted.
    """
    patch_files = [f for f in os.listdir(directory) if 'patch' in f]
    for patch_file in patch_files:
        try:
            os.remove(os.path.join(directory, patch_file))
        except OSError as e:
            print(f"Error removing file {patch_file}: {e}")

def extract_image_identifier(patch_file_name):
    """
    Extract a unique identifier from the patch file name that identifies the source image.
    This function should ignore the row and column indices of the patch.
    
    Assuming file name format is 'img_YYYYMMDD_D1_3_XXX_patch_ROW_COL_predicted.png'
    or 'Platte_YYYYMMDD_Sorghum_XXX_ROW_COL'.
    """
    # Split the filename by underscores and remove the patch-specific parts
    parts = patch_file_name.split('_')
    if 'patch' in parts:
        # The unique identifier is everything before the "patch" keyword
        identifier_index = parts.index('patch')
        identifier_parts = parts[:identifier_index]
    else:
        # Assuming another format without "patch", adjust based on your needs
        identifier_parts = parts[:-2]  # This removes the last two elements, usually row and col indices
    
    identifier = '_'.join(identifier_parts)
    return identifier


def determine_max_row_col(patch_files):
    max_row, max_col = 0, 0
    for patch_file in patch_files:
        row, col = extract_coordinates(patch_file)
        max_row = max(max_row, row)
        max_col = max(max_col, col)
    return max_row, max_col

def stitch_patches_to_full_image_by_identifier(patch_dir, patch_files, image_size, patch_size=256):
    """
    Stitch patches for a specific image into a full-resolution image.
    
    Args:
        patch_dir (str): Directory containing patch predictions.
        patch_files (list): List of patch filenames for a specific image.
        image_size (tuple): The dimensions (height, width) of the full-resolution image.
        patch_size (int): Size of the patches (assumed square).
    
    Returns:
        np.array: The stitched full-resolution image.
    """
    try:
        # Initialize an empty array for the full-resolution image
        full_image = np.zeros((image_size[0], image_size[1], 3), dtype=np.uint8)
        
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
    except Exception as e:
        print(f"Error stitching patches to full image: {e}")
        return None

def cleanup_patch_files_by_identifier(directory, identifier):
    """
    Remove patch files for a specific image from the specified directory.

    Args:
        directory (str): Directory from which patch files will be deleted.
        identifier (str): Unique identifier for the image whose patches are to be deleted.
    """
    patch_files = [f for f in os.listdir(directory) if 'patch' in f]
    for patch_file in patch_files:
        try:
            os.remove(os.path.join(directory, patch_file))
        except OSError as e:
            print(f"Error removing file {patch_file}: {e}")


def train_and_evaluate_val_los(model, criterion, optimizer, scheduler, train_loader, val_loader, device, hyperparams, num_epochs=15, validate_every_n_epochs=3, accumulation_steps=3, early_stopping_patience=3, results_file='hyperparams_and_scores.csv'):
    scaler = GradScaler(enabled=torch.cuda.is_available())
    best_val_loss = float('inf')
    epochs_without_improvement = 0

    for epoch in range(num_epochs):
        model.train()
        optimizer.zero_grad()

        # Training loop
        for i, (images, masks) in enumerate(tqdm(train_loader, desc=f"Training Epoch {epoch}")):
            images = images.to(device)
            masks = masks.to(device)

            with torch.cuda.amp.autocast(enabled=torch.cuda.is_available()):
                outputs = model(images)
                loss = criterion(outputs, masks) / accumulation_steps

            scaler.scale(loss).backward()
            if (i + 1) % accumulation_steps == 0:
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad()

        # Validation step
        if epoch % validate_every_n_epochs == 0:
            model.eval()
            total_val_loss = 0
            with torch.no_grad():
                for val_images, val_masks in tqdm(val_loader, desc="Validating"):
                    val_images = val_images.to(device)
                    val_masks = val_masks.to(device)

                    outputs = model(val_images)
                    val_loss = criterion(outputs, val_masks)
                    total_val_loss += val_loss.item()

            average_val_loss = total_val_loss / len(val_loader)

            if average_val_loss < best_val_loss:
                best_val_loss = average_val_loss
                epochs_without_improvement = 0
                save_hyperparams_and_scores_to_csv(results_file, hyperparams, best_val_loss)
            else:
                epochs_without_improvement += 1

            if epochs_without_improvement >= early_stopping_patience:
                print("Early stopping triggered.")
                break

        scheduler.step()

        # Clear memory
        gc.collect()
        torch.cuda.empty_cache()

    return best_val_loss
