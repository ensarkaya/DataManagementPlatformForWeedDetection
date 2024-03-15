import os
import numpy as np
from PIL import Image
from model_components.data_prep_run import get_run_data_loaders
from model_components.model import ResNetUNet 
from model_components.test import save_segmentation
from model_components.utils import calculate_metrics, cleanup_patch_files, determine_max_row_col, extract_image_identifier, map_color, stitch_patches_to_full_image_by_identifier
from model_components.utils_run_model import calculate_pixel_ratio
import tempfile
from flask import Flask, request, jsonify
import torch
from io import BytesIO
import base64
import re
import shutil
import uuid
app = Flask(__name__)

def secure_filename(filename):
    """
    Sanitize the filename by removing or replacing characters that are not
    alphanumeric, dashes, underscores, or dots.
    """
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    return filename

def save_segmentation_run(images, outputs, image_names, save_dir, n_images=1):
    # Ensure the save directory exists
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)  # Creates the directory if it doesn't exist
    with torch.no_grad():
        images = images.cpu()
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
            pred_filename = f'{base_name}_patch_{row_index}_{col_index}_predicted.png'

            # Save predicted mask with color mapping
            pred_mask_colored = map_color(outputs[i].unsqueeze(0), color_map)
            pred_mask_image = Image.fromarray(pred_mask_colored)
            pred_mask_image.save(os.path.join(save_dir, pred_filename))

def process_single_image_with_model(image_path, model_path, save_dir, resnet_model):
    # Load Model
    model = ResNetUNet(n_classes=3, resnet_model_path=resnet_model)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    
    # Load saved model weights
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    run_loader = get_run_data_loaders(image_path= image_path) 
    result_data = None  # Initialize result_data
    full_image = None  # Initialize full_image to handle the case where no images are processed
    with torch.no_grad():
        for batch, (images, image_names, _) in enumerate(run_loader):
            images = images.to(device)
            outputs = model(images)
            save_segmentation_run(images, outputs, image_names, save_dir, n_images=images.size(0))
            del images, outputs
    
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
        full_image_path = os.path.join(save_dir, f"{identifier}_generated.png")
        Image.fromarray(full_image).save(full_image_path)

        result_data = calculate_pixel_ratio(full_image_path)        
    # Cleanup: Remove the saved patches for the current image
    cleanup_patch_files(save_dir)

    if full_image is None:
        raise ValueError("No images were processed.")
    if result_data is None:
        raise ValueError("No result data was generated.")

    return full_image, result_data

@app.route('/process_images', methods=['POST'])
def process_images():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    image_file = request.files['image']
    base_path = os.getcwd()
    models = os.path.join(base_path, 'models')
    # Temporary directory for processing
    temp_dir = os.path.join(base_path, f'temp_{str(uuid.uuid4())}')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Save the incoming file temporarily
        image_path = os.path.join(temp_dir, secure_filename(image_file.filename))
        image_file.save(image_path)

        # Define paths and model parameters
        model_path = os.path.join(models, 'best_model.pth')
        resnet_model = os.path.join(models, 'resnet34.pth')
        if not os.path.exists(model_path):
            raise FileNotFoundError("Model file not found")
        save_dir = os.path.join(base_path, f'generated_masks_{str(uuid.uuid4())}')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Process the image
        generated_image, result_data = process_single_image_with_model(temp_dir, model_path, save_dir, resnet_model)

        # Convert the processed numpy.ndarray back to a PIL.Image object
        generated_image_pil = Image.fromarray(generated_image.astype('uint8'), 'RGB')

        # Now we can save it to a buffer and encode it as base64
        # Convert the processed image to a base64 string for JSON transfer
        buffered = BytesIO()
        generated_image_pil.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Prepare response
        response_data = {
            "image_base64": image_base64,
            "result_data": result_data
        }

        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Cleanup: remove the temporary file and directory
        try:
            if os.path.exists(save_dir):
                shutil.rmtree(save_dir)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Error removing the directory: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
