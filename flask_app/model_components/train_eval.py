import torch
import torch.nn as nn
import torch.optim as optim
from torch.cuda.amp import GradScaler, autocast
from torchvision.transforms import Resize
import gc
from data_prep import get_data_loaders
from model import ResNetUNet
import os
from sklearn.metrics import f1_score
import numpy as np
from tqdm import tqdm

def calculate_f1_score_multiclass(true_masks, pred_masks, num_classes=3):
    """
    Calculate the F1 score for multiclass segmentation.
    
    :param true_masks: Ground truth masks.
    :param pred_masks: Predicted masks.
    :param num_classes: Number of classes.
    :return: The average F1 score across all classes.
    """
    f1_scores = []
    for class_id in range(num_classes):
        true_binary = (true_masks == class_id)
        pred_binary = (pred_masks == class_id)
        f1 = f1_score(true_binary.flatten(), pred_binary.flatten(), average='binary', zero_division=0)
        f1_scores.append(f1)
    return np.mean(f1_scores)

def calculate_dice_score_multiclass(true_masks, pred_masks, num_classes=3):
    """
    Calculate the Dice score for multiclass segmentation.
    
    :param true_masks: Ground truth masks.
    :param pred_masks: Predicted masks.
    :param num_classes: Number of classes.
    :return: The average Dice score across all classes.
    """
    dice_scores = []
    for class_id in range(num_classes):
        true_binary = (true_masks == class_id)
        pred_binary = (pred_masks == class_id)
        intersection = np.logical_and(true_binary, pred_binary).sum()
        dice_score = (2. * intersection) / (true_binary.sum() + pred_binary.sum()) if (true_binary.sum() + pred_binary.sum()) > 0 else 1.0
        dice_scores.append(dice_score)
    return np.mean(dice_scores)


def main():
    # Load Data
    # image_path = r'D:\Thesis\model\2024_01_15_initial_set_of_drone_images\img'
    # mask_path = r'D:\Thesis\model\2024_01_15_initial_set_of_drone_images\gt'
    # test_image_path = r'D:\Thesis\model\2024_01_15_initial_set_of_drone_images\test_img'
    # test_mask_path = r'D:\Thesis\model\2024_01_15_initial_set_of_drone_images\test_gt'
    # preprocessed_path = r'D:\Thesis\model\2024_01_15_initial_set_of_drone_images\patches'

    # Define the base path relative to the current working directory
    base_path = os.getcwd()

    image_path = os.path.join(base_path, '2024_01_15_initial_set_of_drone_images/img')
    mask_path = os.path.join(base_path, '2024_01_15_initial_set_of_drone_images/gt')
    test_image_path = os.path.join(base_path, '2024_01_15_initial_set_of_drone_images/test_img')
    test_mask_path = os.path.join(base_path, '2024_01_15_initial_set_of_drone_images/test_gt')
    preprocessed_path = os.path.join(base_path, '2024_01_15_initial_set_of_drone_images\patches')

    use_preprocessed_patches = os.path.exists(preprocessed_path) and os.path.isdir(preprocessed_path)

    # image_size = (256, 256) 
    # batch_size = 4  
    train_loader, val_loader, _ = get_data_loaders(image_path, mask_path, test_image_path, test_mask_path, use_preprocessed_patches=use_preprocessed_patches,
        preprocessed_dir=preprocessed_path, batch_size=4, patch_size=256)

    # Model, Loss, Optimizer
    model = ResNetUNet(n_classes=3)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)  # Example scheduler

    # Training Configuration
    num_epochs = 15
    validate_every_n_epochs = 3
    accumulation_steps = 3
    scaler = GradScaler(enabled=torch.cuda.is_available())
    best_val_loss = float('inf')

    # Early Stopping Configuration
    early_stopping_patience = 3  # Number of epochs to wait for improvement before stopping
    epochs_without_improvement = 0

    for epoch in range(0, num_epochs):
        model.train()
        optimizer.zero_grad()

        # Training Loop
        for i, (images, masks, img_name, coords) in enumerate(tqdm(train_loader, desc="Training Epoch {}".format(epoch))):
            images = images.to(device)
            masks = masks.to(device)

            outputs = model(images)
            loss = criterion(outputs, masks) / accumulation_steps

            scaler.scale(loss).backward()
            if (i + 1) % accumulation_steps == 0:
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad()
                del images, masks, outputs, loss  # Delete variables to free up RAM
                gc.collect()  # Clear memory

        #Val Step
        if epoch % validate_every_n_epochs == 0:
                # Assuming softmax is applied to model outputs to obtain probabilities
                softmax = nn.Softmax(dim=1)

                # Set the model to evaluation mode
                model.eval()

                # Lists to store metric scores for each batch
                val_f1_scores = []
                val_dice_scores = []
                best_val_f1_score = -float('inf')  

                with torch.no_grad():
                    for val_images, val_masks, _, _ in tqdm(val_loader, desc="Validating"):
                        # Transfer images and masks to the current device (GPU, if available)
                        val_images = val_images.to(device)
                        val_masks = val_masks.to(device)
                        
                        # Forward pass: compute predicted outputs by passing inputs to the model
                        val_outputs = model(val_images)
                        
                        # Apply softmax to the model outputs to get class probabilities
                        val_probs = softmax(val_outputs)
                        
                        # Get the predictions by taking the argmax of the class probabilities
                        val_preds = torch.argmax(val_probs, dim=1)

                        # Metrics calculation is usually done on the CPU. There are two main reasons for this:
                        # 1. Many libraries for metric calculation (e.g., scikit-learn) expect NumPy arrays as input,
                        #    which requires transferring tensors from GPU to CPU.
                        # 2. Metric calculations are often not as computationally intensive as model training,
                        #    so using the GPU might not offer significant benefits. Additionally, doing this on the CPU
                        #    can help reduce GPU memory usage, which is often a limiting factor in training larger models.
                        val_preds_np = val_preds.cpu().numpy()
                        val_masks_np = val_masks.cpu().numpy()

                        # Calculate F1 and Dice scores for the current batch and append to the lists
                        f1_score_val = calculate_f1_score_multiclass(val_masks_np, val_preds_np)
                        dice_score_val = calculate_dice_score_multiclass(val_masks_np, val_preds_np)
                        val_f1_scores.append(f1_score_val)
                        val_dice_scores.append(dice_score_val)

                # Calculate average scores across all validation batches
                average_val_f1_score = np.mean(val_f1_scores)
                average_val_dice_score = np.mean(val_dice_scores)

                # Log the average validation F1 and Dice scores
                print(f'Validation F1 Score: {average_val_f1_score}, Dice Score: {average_val_dice_score}')
                     
                if average_val_f1_score > best_val_f1_score:
                    best_val_f1_score = average_val_f1_score
                    epochs_without_improvement = 0
                    torch.save(model.state_dict(), 'best_model.pth')
                else:
                    epochs_without_improvement += 1

                if epochs_without_improvement >= early_stopping_patience:
                    print("Early stopping triggered.")
                    break

        scheduler.step()  # Update learning rate
        # Clear memory
        gc.collect()
        torch.cuda.empty_cache()

if __name__ == '__main__':
    main()
