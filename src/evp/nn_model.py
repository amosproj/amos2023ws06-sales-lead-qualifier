# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>

import os

import boto3
import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from imblearn.under_sampling import RandomUnderSampler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset

data_path = "s3://amos--data--features/preprocessed_data_files/preprocessed_data.csv"
df = pd.read_csv(data_path)


features = df.drop(
    columns=["MerchantSizeByDPV", "regional_atlas_investments_p_employee"], axis=1
)
class_labels = df["MerchantSizeByDPV"]

# split the data into training (80%), validation (10%), and testing (10%) sets
X_train, X_test, y_train, y_test = train_test_split(
    features, class_labels, test_size=0.1, random_state=42
)

undersampler = RandomUnderSampler(random_state=42)
X_train, y_train = undersampler.fit_resample(X_train, y_train)

X_train_tensor = torch.tensor(X_train.values, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train.values, dtype=torch.long)
X_test_tensor = torch.tensor(X_test.values, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test.values, dtype=torch.long)


class NeuralNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, l1_reg=0):
        super(NeuralNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.fc4 = nn.Linear(hidden_size, output_size)
        self.softmax = nn.Softmax(dim=1)
        self.l1_reg = l1_reg

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.fc3(x)
        x = self.relu(x)
        x = self.fc4(x)
        x = self.softmax(x)
        return x

    def l1_norm_regularization(self):
        l1_penalty = torch.tensor(0.0, requires_grad=True)
        for name, param in self.named_parameters():
            if "weight" in name:
                l1_penalty = l1_penalty + torch.norm(param, p=1)
        return self.l1_reg * l1_penalty


input_size = X_train.shape[1]
hidden_size = 64
output_size = 5
l1_regularization = 0.01
model = NeuralNetwork(input_size, hidden_size, output_size, l1_regularization)


criterion = nn.CrossEntropyLoss()
# optimizer = optim.Adam(model.parameters(), lr=0.0005, momentum=0.9)
optimizer = optim.SGD(model.parameters(), lr=0.0001, momentum=0.9)

train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

num_epochs = 500

for epoch in range(num_epochs):
    for batch_X, batch_y in train_loader:
        outputs = model(batch_X)
        loss = criterion(outputs, batch_y) + model.l1_norm_regularization()

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}")


with torch.no_grad():
    test_outputs = model(X_test_tensor)
    predicted_labels = np.argmax(test_outputs.numpy(), axis=1)

from sklearn.metrics import classification_report

print(classification_report(y_test, predicted_labels))
