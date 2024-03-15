import os
from skimage.io import imread, imsave
from skimage.transform import resize
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import torch
from PIL import Image
import numpy as np  

# Set a seed for torch operations
torch.manual_seed(42)  

class SorghumDataset(Dataset):
    def __init__(self, image_dir, mask_dir=None, patch_size=256, transform=None, mask_transform=None, is_train=True, is_test=False, use_preprocessed_patches=False, preprocessed_dir=None):
        self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.patch_size = patch_size
        self.transform = transform
        self.mask_transform = mask_transform
        self.is_train = is_train
        self.is_test = is_test
        self.use_preprocessed_patches = use_preprocessed_patches
        self.preprocessed_dir = preprocessed_dir

        if self.use_preprocessed_patches and self.preprocessed_dir:
            self.patches = self.load_preprocessed_patches()
        else:
            self.images = [file for file in os.listdir(image_dir)]
            print(f"Found images: {self.images}")
            print(f'file names in image_dir: {os.listdir(image_dir)}')
            self.patches = self.create_patches()


    def __len__(self):
        return len(self.patches)

    def __getitem__(self, idx):
        try:
            patch_data = self.patches[idx]
            if patch_data is None:
                # Log and handle missing patch data
                print(f"Warning: Patch data at index {idx} is None.")
                raise ValueError(f"Patch at index {idx} is None. This should not happen with proper checks in place.")
        except IndexError:
            raise IndexError(f"Index {idx} out of bounds for patches list with length {len(self.patches)}.")

        # For both training and testing, we expect a tuple of (img_patch, mask_patch, img_name, coords)
        img_patch, mask_patch, img_name, coords = patch_data

        # Convert numpy arrays to PIL Images
        image = Image.fromarray(img_patch)
        
        # Apply transformations to the image
        if self.transform:
            image = self.transform(image)
        else:
            # Convert image to tensor if no other transformations are specified
            image = torch.from_numpy(np.array(image)).long()           

        # Handle the mask
        if self.mask_dir:
            # Convert mask to class indices and then to tensor for training/validation
            mask = self.rgb_to_index(np.array(mask))
            mask = torch.from_numpy(mask).long()

            # Apply mask transformations if specified and required
            if self.mask_transform:
                mask = self.mask_transform(mask)
        else:
            # Return a dummy tensor for mask if mask_dir is None
            # This tensor can be of shape (1, H, W) with zeros indicating no mask information
            mask = torch.zeros(1, *image.shape[1:3], dtype=torch.long)

        return image, mask, img_name, coords


    def create_patches(self):
        patches = []
        for img_name in self.images:
            img_path = os.path.join(self.image_dir, img_name)
            mask_path = os.path.join(self.mask_dir, img_name) if self.mask_dir else None  # Conditional mask path

            image = imread(img_path)
            mask = imread(mask_path) if self.mask_dir else np.zeros((image.shape[0], image.shape[1], image.shape[2] if image.ndim == 3 else 1), dtype=np.uint8)

            # Calculate number of patches along each dimension
            num_patches_x, num_patches_y = np.ceil(image.shape[1] / self.patch_size).astype(int), np.ceil(image.shape[0] / self.patch_size).astype(int)
            for i in range(num_patches_y):
                for j in range(num_patches_x):
                    # Define the patch boundaries
                    start_i, start_j = i * self.patch_size, j * self.patch_size
                    end_i, end_j = start_i + self.patch_size, start_j + self.patch_size

                    img_patch = image[start_i:end_i, start_j:end_j]
                    mask_patch = mask[start_i:end_i, start_j:end_j]

                    # Pad the patch if it's smaller than the expected size
                    pad_height = self.patch_size - img_patch.shape[0]
                    pad_width = self.patch_size - img_patch.shape[1]

                    if pad_height > 0 or pad_width > 0:
                        img_patch = np.pad(img_patch, ((0, pad_height), (0, pad_width), (0, 0)), mode='constant', constant_values=0)
                        # Adjust mask padding based on its dimensionality
                        if mask_patch.ndim == 3:  # For masks with depth (color masks or dummy masks with depth)
                            mask_patch = np.pad(mask_patch, ((0, pad_height), (0, pad_width), (0, 0)), mode='constant', constant_values=0)
                        else:  # For grayscale masks without depth
                            mask_patch = np.pad(mask_patch, ((0, pad_height), (0, pad_width)), mode='constant', constant_values=0)

                    # Check if this is a training image and if the patch is relevant
                    if self.is_train and not self.is_patch_relevant(mask_patch):
                        continue
                    img_name_wo_ext = os.path.splitext(img_name)[0]  # Changed to handle any image format, not just .png
                    patch_img_name = f'{img_name_wo_ext}_{i}_{j}_patch.png'
                    patches.append((img_patch, mask_patch, patch_img_name, (i, j)))

        return patches


    def is_patch_relevant(self, mask_patch):
        # Assuming the color for sorghum is [31, 119, 180] and for weeds is [255, 127, 14]
        sorghum_color_1 = np.array([31, 119, 180])
        sorghum_color_2 = np.array([31, 119, 189])
        weed_color = np.array([255, 127, 14])

        # Check if there's at least one pixel of sorghum or weed
        has_sorghum = np.any(np.all(mask_patch == sorghum_color_1, axis=-1)) or np.any(np.all(mask_patch == sorghum_color_2, axis=-1))
        has_weed = np.any(np.all(mask_patch == weed_color, axis=-1))

        return has_sorghum or has_weed
    
    def rgb_to_index(self, mask, tolerance=10):  
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

    def load_preprocessed_patches(self):
        patches = []
        img_patch_dir = os.path.join(self.preprocessed_dir, 'img_patches')
        mask_patch_dir = os.path.join(self.preprocessed_dir, 'gt_patches')

        # Verify that each image patch has a corresponding mask patch
        for img_patch_name in os.listdir(img_patch_dir):
            img_patch_path = os.path.join(img_patch_dir, img_patch_name)
            mask_patch_name = img_patch_name  # Assuming image and mask names are the same
            mask_patch_path = os.path.join(mask_patch_dir, mask_patch_name)

            # Check if the mask patch exists for the current image patch
            if not os.path.exists(mask_patch_path) or not os.path.isfile(img_patch_path):
                print(f"Missing or corrupt file: {img_patch_path} or {mask_patch_path}")
                continue 

            try:
                img_patch = imread(img_patch_path)
                mask_patch = imread(mask_patch_path)

                # Ensure both image and mask patches are successfully loaded (not None and have content)
                if img_patch is not None and mask_patch is not None:
                    components = img_patch_name.split("_")
                    i, j = int(components[-3]), int(components[-2])  
                    patches.append((img_patch, mask_patch, img_patch_name, (i, j)))
                else:
                    print(f"Failed to load image or mask for {img_patch_name}. One of them is None.")
            except Exception as e:
                print(f"Error loading {img_patch_name}: {e}")

        return patches

    
# Transforms for training and validation
train_val_transform = transforms.Compose([
    transforms.ToTensor(),
    # Add any other image-specific transforms or augmentations here
])

# Transforms for testing (full images)
test_transform = transforms.Compose([
    transforms.ToTensor(),
    # Add normalization or other relevant transforms here
])

# No resizing needed as patches are already handled in the dataset class

def get_data_loaders(image_path, mask_path, test_image_path, test_mask_path, batch_size=2, patch_size=256, preprocessed_dir=None, use_preprocessed_patches=False):
    # Determine if preprocessed patches should be used
    if use_preprocessed_patches:
        # Assuming preprocessed patches are stored in a specific structure
        image_path = os.path.join(preprocessed_dir, 'img_patches')
        mask_path = os.path.join(preprocessed_dir, 'gt_patches')
        test_image_path = image_path  # Update if you have a separate test set of preprocessed patches
        test_mask_path = mask_path

    # Initialize the datasets
    combined_dataset = SorghumDataset(image_dir=image_path, mask_dir=mask_path, patch_size=patch_size, transform=train_val_transform, is_train=True, is_test=False, use_preprocessed_patches=use_preprocessed_patches, preprocessed_dir=preprocessed_dir)

    # Determine sizes for training and validation datasets
    total_size = len(combined_dataset)
    train_size = int(0.75 * total_size)
    val_size = total_size - train_size

    # Splitting the combined dataset
    train_dataset, val_dataset = torch.utils.data.random_split(combined_dataset, [train_size, val_size])

    # Initialize the test dataset
    test_dataset = SorghumDataset(image_dir=test_image_path, mask_dir=test_mask_path, patch_size=patch_size, transform=test_transform, is_train=False, is_test=True, use_preprocessed_patches=use_preprocessed_patches, preprocessed_dir=preprocessed_dir)

    # Data loaders for each set
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
    test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False, num_workers=2)  # Adjust if test set also uses patches

    return train_loader, val_loader, test_loader

def get_run_loader(test_image_dir, batch_size=1, patch_size=256, transform=None):
    """
    Create a DataLoader for test images.

    Parameters:
    - test_image_dir: Directory containing test images.
    - batch_size: Number of images per batch.
    - patch_size: Size of patches the images are divided into (if applicable).
    - transform: Transformations to be applied on test images.

    Returns:
    - A DataLoader for the test images.
    """
    # Initialize the test dataset
    run_dataset = SorghumDataset(image_dir=test_image_dir, mask_dir=None, patch_size=patch_size, transform=transform, is_train=False, is_test=True, use_preprocessed_patches=False, preprocessed_dir=None)

    # Data loader for the test set
    run_loader = DataLoader(run_dataset, batch_size=batch_size, shuffle=False, num_workers=2)

    return run_loader

