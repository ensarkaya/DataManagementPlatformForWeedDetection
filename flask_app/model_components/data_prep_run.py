import os
from skimage.io import imread
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import numpy as np  

class SorghumRunDataset(Dataset):
    def __init__(self, image_dir, patch_size=256, transform=None, is_test=False, use_preprocessed_patches=False, preprocessed_dir=None):
        self.image_dir = image_dir
        self.patch_size = patch_size
        self.transform = transform
        self.is_test = is_test
        self.use_preprocessed_patches = use_preprocessed_patches
        self.preprocessed_dir = preprocessed_dir

        self.images = [file for file in os.listdir(image_dir)]
        self.patches = self.create_patches()

    def __len__(self):
        return len(self.patches)

    def __getitem__(self, idx):
        patch_data = self.patches[idx]
        img_patch, img_name, coords = patch_data

        image = Image.fromarray(img_patch)

        if self.transform:
            image = self.transform(image)

        return image, img_name, coords

    def create_patches(self):
        patches = []
        for img_name in self.images:
            img_path = os.path.join(self.image_dir, img_name)
            image = imread(img_path)

            num_patches_x, num_patches_y = np.ceil(image.shape[1] / self.patch_size).astype(int), np.ceil(image.shape[0] / self.patch_size).astype(int)
            for i in range(num_patches_y):
                for j in range(num_patches_x):
                    start_i, start_j = i * self.patch_size, j * self.patch_size
                    end_i, end_j = start_i + self.patch_size, start_j + self.patch_size

                    img_patch = image[start_i:end_i, start_j:end_j]

                    pad_height = self.patch_size - img_patch.shape[0]
                    pad_width = self.patch_size - img_patch.shape[1]

                    if pad_height > 0 or pad_width > 0:
                        img_patch = np.pad(img_patch, ((0, pad_height), (0, pad_width), (0, 0)), mode='constant', constant_values=0)

                    img_name = img_name.split('.png')[0]
                    patch_img_name = f'{img_name}_{i}_{j}_patch.png'
                    patches.append((img_patch, patch_img_name, (i, j)))

        return patches

test_transform = transforms.Compose([
    transforms.ToTensor(),
    # Add normalization or other relevant transforms here
])

# Function to get data loaders for running (without masks)
def get_run_data_loaders(image_path, batch_size=1, patch_size=256, preprocessed_dir=None, use_preprocessed_patches=False):
    if use_preprocessed_patches:
        image_path = os.path.join(preprocessed_dir, 'img_patches')

    run_dataset = SorghumRunDataset(image_dir=image_path, patch_size=patch_size, transform=test_transform, is_test=True, use_preprocessed_patches=use_preprocessed_patches, preprocessed_dir=preprocessed_dir)

    run_loader = DataLoader(run_dataset, batch_size=batch_size, shuffle=False, num_workers=2)

    return run_loader
