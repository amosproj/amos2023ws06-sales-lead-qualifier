# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>

import os
import pickle

import boto3
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from pytorch_tabnet.callbacks import EarlyStopping
from pytorch_tabnet.pretraining import TabNetPretrainer
from pytorch_tabnet.tab_model import TabNetClassifier
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from torch.utils.data import DataLoader, TensorDataset

data_path = "s3://amos--data--features/preprocessed_data_files/preprocessed_data.csv"
df = pd.read_csv(data_path)

# df = df[df['google_places_confidence']>=0.7]
# df = df[df['MerchantSizeByDPV']!=0]

features = df.drop(
    columns=["MerchantSizeByDPV", "regional_atlas_investments_p_employee"], axis=1
)
# columns_to_remove = [col for col in features.columns if col.startswith('regional')]
# features = features.drop(columns=columns_to_remove)
class_labels = df["MerchantSizeByDPV"]

# split the data into training (80%), validation (10%), and testing (10%) sets
X_train, X_tmp, y_train, y_tmp = train_test_split(
    features, class_labels, test_size=0.2, random_state=42
)
X_val, X_test, y_val, y_test = train_test_split(
    X_tmp, y_tmp, test_size=0.5, random_state=42
)

# undersampler = RandomUnderSampler(random_state=42)
# X_train, y_train = undersampler.fit_resample(X_train, y_train)


X_train_tensor = torch.tensor(X_train.values, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train.values, dtype=torch.float32)
X_val_tensor = torch.tensor(X_val.values, dtype=torch.float32)
X_test_tensor = torch.tensor(X_test.values, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test.values, dtype=torch.float32)
y_val_tensor = torch.tensor(y_val.values, dtype=torch.float32)

classes, class_counts = torch.unique(y_train_tensor, return_counts=True)
class_weights = compute_class_weight(
    class_weight="balanced", classes=np.unique(y_train.values), y=y_train.values
)
class_weights = torch.tensor(class_weights, dtype=torch.float32)
print(f"class_weights = {class_weights}")


class NeuralNetworkClassifer(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, l1_reg=0):
        super(NeuralNetworkClassifer, self).__init__()
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


class FeedforwardNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(FeedforwardNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.relu3 = nn.ReLU()
        self.fc4 = nn.Linear(hidden_size, output_size)
        self.relu4 = nn.ReLU()
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        x1 = self.relu1(self.fc1(x))
        x2 = self.relu2(self.fc2(x1)) + x1
        x3 = self.relu3(self.fc3(x2)) + x2
        x4 = self.relu4(self.fc4(x3))
        return self.softmax(x4)


# input_size = X_train.shape[1]
# hidden_size = 128
# # output_size = 1
# output_size = 5
# l1_regularization = 0.01
# model = FeedforwardNN(input_size, hidden_size, 1)


# criterion = nn.CrossEntropyLoss()
# # criterion = nn.MSELoss(we)
# # criterion = torch.nn.L1Loss()

# optimizer = optim.Adam(model.parameters(), lr=0.0001)
# # optimizer = optim.SGD(model.parameters(), lr=0.0001, momentum=0.9)


# train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
# train_loader = DataLoader(train_dataset, batch_size=256, shuffle=True)

# early_stopping = EarlyStopping(
#     patience=10,
#     mode="min",
# )

# pretrainer = TabNetPretrainer()
# pretrainer.fit(X_train.values)
clf = TabNetClassifier()
# clf.fit(
#     X_train.values, y_train.values,
#     eval_set=[(X_val.values, y_val.values)],
#     eval_metric=['accuracy', 'logloss', 'f1'],
#     max_epochs=100,
#     patience=10,
#     callbacks=[early_stopping],
#     batch_size=64,
#     virtual_batch_size=32,
# )
# for epoch, loss in enumerate(clf.history['valid_logloss']):
#     print(f"Epoch {epoch + 1}, Validation Loss: {loss}")

patience = 10
best_valid_loss = float("inf")
counter = 0

# Training loop with manual early stopping
for epoch in range(1):  # Adjust the number of epochs based on your dataset
    clf.fit(
        X_train.values,
        y_train.values,
        eval_set=[(X_val.values, y_val.values)],
        eval_metric=["logloss"],
        max_epochs=100,
        batch_size=64,
        virtual_batch_size=32,
    )

    # # Get validation loss from the training history
    # current_valid_loss = clf.history['valid_balanced_accuracy'][0]

    # # Print validation loss
    # print(f"Epoch {epoch + 1}, Validation Loss: {current_valid_loss}")

    # # Check for early stopping
    # if current_valid_loss < best_valid_loss:
    #     best_valid_loss = current_valid_loss
    #     counter = 0
    # else:
    #     counter += 1
    #     if counter >= patience:
    #         print(f"Early stopping after {epoch + 1} epochs.")
    #         break
    predictions = clf.predict(X_test.values)
    print(classification_report(y_test, predictions))


# # Make predictions
# predictions = clf.predict(X_test.values)

# # Evaluate the model
# accuracy = clf.history['valid_accuracy'][-1]
# f1 = clf.history['valid_f1'][-1]
# f1_test = f1_score(predictions, y_test)


# print(f"Test Accuracy: {accuracy}")
# print(f"Test F1 Score: {f1}")
# print(f"f1_test = {f1_test}")


# num_epochs = 10

# for epoch in range(num_epochs):
#     for batch_X, batch_y in train_loader:
#         outputs = model(batch_X)
#         batch_y = batch_y.unsqueeze(1)

#         # L1 norm regularization
#         l1_reg = 0.0
#         lambda_l1 = 0.01
#         for param in model.parameters():
#             l1_reg += torch.norm(param, 1)

#         # Add L1 norm regularization term to the loss
#         loss = criterion(outputs, batch_y) + lambda_l1 * l1_reg
#         loss = torch.mean(loss * class_weights)

#         optimizer.zero_grad()
#         loss.backward()
#         optimizer.step()

#     print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}")


# with torch.no_grad():
#     model.eval()
#     test_outputs = model(X_test_tensor)

#     # clamp_ranges = [(-float('inf'), 0.49),(0.5,1.49),(1.5,2.49),(2.5,3.49),(3.5,float('inf'))]
#     # clamped_tensor = torch.zeros_like(test_outputs, dtype=torch.int)
#     # for i, (min_val,max_val) in enumerate(clamp_ranges):
#     #     mask = (test_outputs >= min_val) & (test_outputs < max_val)
#     #     clamped_tensor[mask] = i
#     # predicted_classes = torch.clamp(test_outputs, 0.5, 4.5).round().squeeze().numpy()
# # predicted_labels = torch.Tensor([1, 2, 3, 4])[predicted_classes]


# print(classification_report(y_test, clamped_tensor))
print(classification_report(y_test, predictions))
f1_test = f1_score(y_test, predictions, average="weighted")


local_directory = "../data/models/"
os.makedirs(local_directory, exist_ok=True)
local_save_path = os.path.join(
    local_directory,
    f"TabNet_f1({f1_test:.4f})_model.pkl",
)
with open(local_save_path, "wb") as file:
    pickle.dump(clf, file)

# upload to s3 bucket
s3_client = boto3.client("s3")
with open(local_save_path, "rb") as data:
    s3_client.upload_fileobj(
        data,
        "amos--models",
        f"TabNet_f1({f1_test:.4f})_model.pkl",
    )
    print(
        f"Model Saved at amos--models/TabNet_f1({f1_test:.4f})_model.pkl",
    )
