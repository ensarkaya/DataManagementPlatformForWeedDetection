import os
import numpy as np
from skimage.io import imread, imsave
from tqdm import tqdm
import argparse
from utils import pad_array, is_patch_relevant, safe_imsave

def preprocess_and_save_patches(image_dir, mask_dir, output_dir, patch_size=256):
    images = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]
    os.makedirs(os.path.join(output_dir, 'img_patches'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'gt_patches'), exist_ok=True)

    saved_patches, skipped_patches = 0, 0

    for img_name in tqdm(images, desc="Processing"):
        base_img_name = img_name.split('.png')[0]
        img_path = os.path.join(image_dir, img_name)
        mask_name = img_name  
        mask_path = os.path.join(mask_dir, mask_name)
        if not os.path.exists(mask_path):  # Skip if corresponding mask does not exist
            continue

        image, mask = imread(img_path), imread(mask_path)
        if image.shape[:2] != mask.shape[:2]:
            print(f"Skipping {img_name}: image and mask sizes do not match.")
            continue

        num_patches_x, num_patches_y = np.ceil(image.shape[1] / patch_size).astype(int), np.ceil(image.shape[0] / patch_size).astype(int)
        for i in range(num_patches_y):
            for j in range(num_patches_x):
                img_patch, mask_patch = image[i*patch_size:(i+1)*patch_size, j*patch_size:(j+1)*patch_size], mask[i*patch_size:(i+1)*patch_size, j*patch_size:(j+1)*patch_size]
                # Pad the patch if it's smaller than the expected size
                pad_height = patch_size - img_patch.shape[0]
                pad_width = patch_size - img_patch.shape[1]     
                if pad_height > 0 or pad_width > 0:        
                    img_patch, mask_patch = pad_array(img_patch, patch_size), pad_array(mask_patch, patch_size)
                if is_patch_relevant(mask_patch):
                    patch_img_name = f'{base_img_name}_{i}_{j}_patch.png'
                    img_patch_path = os.path.join(output_dir, 'img_patches', patch_img_name)
                    mask_patch_path = os.path.join(output_dir, 'gt_patches', patch_img_name)

                    # img_patch_path = os.path.join(output_dir, 'img_patches', f'{img_name[:-4]}_patch_{i}_{j}{img_name[-4:]}')
                    # mask_patch_path = os.path.join(output_dir, 'gt_patches', f'{mask_name[:-4]}_patch_{i}_{j}{mask_name[-4:]}')
                    safe_imsave(img_patch_path, img_patch)
                    safe_imsave(mask_patch_path, mask_patch)
                    saved_patches += 1
                else:
                    skipped_patches += 1

    print(f"Processing completed: {saved_patches} patches saved, {skipped_patches} patches skipped due to irrelevance.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Preprocess images and masks into patches.")
    # parser.add_argument("--image_dir", required=True, help="Directory containing images.")
    # parser.add_argument("--mask_dir", required=True, help="Directory containing corresponding masks.")
    # parser.add_argument("--output_dir", required=True, help="Output directory for saved patches.")
    parser.add_argument("--patch_size", type=int, default=256, help="Size of the patches to be extracted.")
    return parser.parse_args()

def main():
    base_path = os.getcwd()

    image_path = os.path.join(base_path, '2024_01_15_initial_set_of_drone_images/img')
    mask_path = os.path.join(base_path, '2024_01_15_initial_set_of_drone_images/gt')
    output_dir = os.path.join(base_path, '2024_01_15_initial_set_of_drone_images/patches')

    args = parse_arguments()
    preprocess_and_save_patches(image_path, mask_path, output_dir, args.patch_size)

if __name__ == "__main__":
    main()