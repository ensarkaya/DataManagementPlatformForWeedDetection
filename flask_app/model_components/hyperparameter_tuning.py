import gc 
from data_prep import get_data_loaders 
from model import ResNetUNet 
import optuna 
import torch 
from torch import nn, optim 
from torch.utils.data import DataLoader 
import os 
import numpy as np 
from torch.cuda.amp import GradScaler 
from tqdm import tqdm 
from train_eval import calculate_f1_score_multiclass 
import csv

def save_hyperparams_and_scores_to_csv(file_path, hyperparams, f1_score):
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Learning Rate", "Batch Size", "Num Epochs", "F1 Score"])  # Header
        writer.writerow([hyperparams['lr'], hyperparams['batch_size'], hyperparams['num_epochs'], f1_score])


def objective(trial):
    # Hyperparameter search space definition
    # lr = trial.suggest_float("lr", 1e-5, 1e-1, log=True)
    # batch_size = trial.suggest_categorical("batch_size", [2, 4, 8, 16, 32])
    # beta1 = trial.suggest_float("beta1", 0.8, 0.99)
    # beta2 = trial.suggest_float("beta2", 0.9, 0.999)
    # num_epochs = trial.suggest_int("num_epochs", 10, 15)  

    # Refined hyperparameter search space definition
    lr = trial.suggest_float("lr", 3e-4, 1e-3, log=True)
    batch_size = trial.suggest_categorical("batch_size", [16, 32])
    beta1 = trial.suggest_float("beta1", 0.8, 0.99)
    beta2 = trial.suggest_float("beta2", 0.9, 0.999)
    num_epochs = trial.suggest_int("num_epochs", 12, 15)  

    # Data loading
    base_path = os.getcwd()
    image_path = os.path.join(base_path, '2024_01_15_initial_set_of_drone_images/img')
    mask_path = os.path.join(base_path, '2024_01_15_initial_set_of_drone_images/gt')
    test_image_path = os.path.join(base_path, '2024_01_15_initial_set_of_drone_images/test_img')
    test_mask_path = os.path.join(base_path, '2024_01_15_initial_set_of_drone_images/test_gt')
    preprocessed_path = os.path.join(base_path, '2024_01_15_initial_set_of_drone_images/patches')
    use_preprocessed_patches = os.path.exists(preprocessed_path) and os.path.isdir(preprocessed_path)

    train_loader, val_loader, _ = get_data_loaders(
        image_path, mask_path, test_image_path, test_mask_path,
        use_preprocessed_patches=use_preprocessed_patches,
        preprocessed_dir=preprocessed_path, batch_size=batch_size, patch_size=256)

    # Model, loss, and optimizer
    model = ResNetUNet(n_classes=3)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, betas=(beta1, beta2))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Initialize the scheduler
    step_size = trial.suggest_int("step_size", 1, 10)  # Example: evaluate every 1 to 10 epochs
    gamma = trial.suggest_float("gamma", 0.1, 0.9)  # Decay rate between 0.1 and 0.9
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=step_size, gamma=gamma)

    # Construct hyperparams dictionary
    hyperparams = {
        'lr': lr,
        'batch_size': batch_size,
        'num_epochs': num_epochs,
        'beta1': beta1,
        'beta2': beta2
    }

    # Specify the results file path
    results_file = 'hyperparams_and_f1_scores_second.csv'

    # Training and evaluation
    f1_score = train_and_evaluate_f1(
        model=model, criterion=criterion, optimizer=optimizer, scheduler=scheduler,
        train_loader=train_loader, val_loader=val_loader, device=device,
        hyperparams=hyperparams, num_epochs=num_epochs, results_file=results_file)

    # Optuna optimizes by minimizing the returned value
    return -f1_score  # Return negative F1 score for optimization


def train_and_evaluate_f1(model, criterion, optimizer, scheduler, train_loader, val_loader, device, hyperparams, num_epochs=15, validate_every_n_epochs=3, accumulation_steps=3, early_stopping_patience=3, results_file='hyperparams_and_scores.csv'):
    scaler = GradScaler(enabled=torch.cuda.is_available())
    best_f1 = -1  # Initialize with a value less than 0, since F1 score ranges from 0 to 1
    epochs_without_improvement = 0
    #results_file='hyperparams_and_scores_second.csv'

    for epoch in range(num_epochs):
        model.train()
        optimizer.zero_grad()

        # Training loop
        for i, (images, masks, img_name, coords) in enumerate(tqdm(train_loader, desc=f"Training Epoch {epoch}")):
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

        # Validation step for F1 score
        if epoch % validate_every_n_epochs == 0:
            model.eval()
            f1_scores = []

            with torch.no_grad():
                for val_images, val_masks, _, _ in tqdm(val_loader, desc="Validating"):
                    val_images = val_images.to(device)
                    val_masks = val_masks.to(device)

                    outputs = model(val_images)
                    preds = torch.argmax(outputs, dim=1)

                    # Calculate F1 score using the provided multiclass F1 score function
                    f1 = calculate_f1_score_multiclass(val_masks.cpu().numpy(), preds.cpu().numpy(), num_classes=3)
                    f1_scores.append(f1)

            average_f1 = np.mean(f1_scores)

            print(f'Epoch {epoch}, Average F1 Score: {average_f1:.4f}')

            if average_f1 > best_f1:
                best_f1 = average_f1
                epochs_without_improvement = 0
                save_hyperparams_and_scores_to_csv(results_file, hyperparams, best_f1)
            else:
                epochs_without_improvement += 1

            if epochs_without_improvement >= early_stopping_patience:
                print("Early stopping triggered.")
                break

        scheduler.step()

        # Clear memory
        gc.collect()
        torch.cuda.empty_cache()

    return best_f1

if __name__ == "__main__":
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=100, timeout=200000)

    print("Best trial:")
    trial = study.best_trial

    print(f"  Value: {trial.value}")
    print("  Params: ")
    for key, value in trial.params.items():
        print(f"    {key}: {value}")
