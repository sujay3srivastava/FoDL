# -*- coding: utf-8 -*-
"""SingleLabelClassifier: 2d Input

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AQLkBvH_tDQXVqzduLDM1HEELvrt3Ruv
"""

import random
import torch
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import os
import numpy as np
import sys
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import pandas as pd
torch.manual_seed(3)
torch.cuda.manual_seed_all(3)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
np.random.seed(3)
random.seed(3)
os.environ['PYTHONHASHSEED'] = str(3)

"""
Hyper Parameters
"""
input_size = 2
hidden_size1 = 5
hidden_size2 = 3
num_classes = 2
num_epochs = 100
batch_size = 16
learning_rate = float(1e-2)
if torch.cuda.is_available():
  device = 'cuda'
else:
  device = 'cpu'
save = True

class Dataset(Dataset):
    def __init__(self, mode='train', transform=None):
        super(Dataset, self).__init__()
        if mode == "train":
            self.df = pd.read_csv("./datasets/task2a/train_t19.csv")
        elif mode == "test":
            self.df = pd.read_csv("./datasets/task2a/test_t19.csv")
        elif mode == "val":
            self.df = pd.read_csv("./datasets/task2a/dev_t19.csv")

        if mode != "test":
            self.y = self.df["label"].to_numpy()
            self.X = self.df[["x1", "x2"]].to_numpy()

    def __getitem__(self, index):
        # Prepare a sample dictionary to store the input 'x' and target 'y'
        sample = {}

        # Get the 'x' (input features) and 'y' (target label) for the given 'index'
        sample["x"] = torch.tensor(self.X[index], dtype=torch.float32)
        sample["y"] = torch.tensor(self.y[index], dtype=torch.long)

        return sample

    def __len__(self):
        # Return the total number of samples in the dataset
        return len(self.X)

def make_dataloaders(batch_size=16):
    # Create train, validation, and test datasets
    train_ds = Dataset(mode='train')
    val_ds = Dataset(mode='val')
    test_ds = Dataset(mode='test')

    # Create train, validation, and test data loaders
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=2, pin_memory=False)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=False)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=False)

    # Return the data loaders
    return train_loader, val_loader, test_loader

class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size1, hidden_size2, num_classes):
        super(NeuralNet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size1)  # First fully connected layer
        self.tanh = nn.Tanh()  # Tanh activation function
        self.fc2 = nn.Linear(hidden_size1, hidden_size2)  # Second fully connected layer
        self.tanh = nn.Tanh()  # Tanh activation function
        self.out = nn.Linear(hidden_size2, num_classes)  # Output layer

    def forward(self, x):
        x = self.fc1(x)  # Pass the input through the first fully connected layer
        out1 = self.tanh(x)  # Apply Tanh activation to the output of the first layer
        out2 = self.fc2(out1)  # Pass the output of the first layer through the second fully connected layer
        out2 = self.tanh(out2)  # Apply Tanh activation to the output of the second layer
        out = self.out(out2)  # Compute the final output of the neural network
        intermediate_out = [out1, out2, out]  # Store intermediate outputs for potential use
        return out, intermediate_out

def train(model, optimizer, criterion, train_loader, val_loader, num_epochs=10):
    avg_losses = []
    avg_acc = []

    for epoch in range(num_epochs):
        total_step = len(train_loader)
        sum_loss = 0
        model.train()

        # Training loop
        for i, sample in enumerate(train_loader):
            # Move tensors to the configured device
            x = sample['x'].to(device)
            labels = sample['y'].to(device)

            # Forward pass
            outputs, _ = model(x)
            loss = criterion(outputs, labels)

            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            sum_loss += loss.item()

        avg_loss = sum_loss / total_step
        print('Loss of the network after {} epochs: {}'.format(epoch, avg_loss))
        avg_losses.append(avg_loss)

        # Validation loop
        with torch.no_grad():
            model.eval()
            total, correct = 0, 0
            for i, sample in enumerate(val_loader):
                # Move tensors to the configured device
                x = sample['x'].to(device)
                labels = sample['y'].to(device)

                # Forward pass
                outputs, _ = model(x)
                _, predicted = torch.max(outputs.data, 1)

                total += labels.size(0)
                correct += (predicted == labels).sum().item()

            acc = 100 * correct / total
            print('Accuracy of the network after {} epochs: {} %'.format(epoch, acc))
            avg_acc.append(acc)

    return avg_losses, avg_acc

def predict(input, epoch=50):
    model = NeuralNet(input_size, hidden_size1, hidden_size2, num_classes).to(device)
    state_dict = torch.load(f"./output/q2a/checkpoints/ckpt_{epoch}.pth")
    model.load_state_dict(state_dict['model_state_dict'])
    input = torch.tensor(input, dtype=torch.float32).to(device)
    with torch.no_grad():
        model.eval()
        out, intermediate_outputs = model(input)
    return out.detach().cpu().numpy(), [out.detach().cpu().numpy() for out in intermediate_outputs]

# Define the plot_surface function
def plot_surface(epoch=50):
    # ... (Existing code for plot_surface) ...

# Define the plot_decision_boundary function
def plot_decision_boundary(epoch=50):
    # ... (Existing code for plot_decision_boundary) ...

if __name__ == "__main__":
    batch_size = 16
    input_size = 2
    hidden_size1 = 50
    hidden_size2 = 30
    num_classes = 3
    learning_rate = 0.01
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    train_loader, val_loader, test_loader = make_dataloaders(batch_size=batch_size)

    # Uncomment and use these lines for training the model
    # model = NeuralNet(input_size, hidden_size1, hidden_size2, num_classes).to(device)
    # criterion = nn.CrossEntropyLoss(reduction='mean')
    # optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=0.1)
    # optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    # train(model, optimizer, criterion, train_loader, val_loader)

    # Uncomment and use this loop to plot decision boundaries and surfaces for different epochs
    for epoch in [1, 2, 10, 50, 99]:
        plot_decision_boundary(epoch=epoch)
        # plot_surface(epoch=epoch)

