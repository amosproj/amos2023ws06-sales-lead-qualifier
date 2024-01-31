# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>

import os
import pickle

# import boto3
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

data_path = "preprocessed_data.csv"
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
class_weights_tensor = torch.tensor(class_weights, dtype=torch.float32)
print(f"class_weights = {class_weights}")


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
tabnet_model = TabNetClassifier(
    optimizer_fn=torch.optim.Adam,
    optimizer_params=dict(lr=2e-2, weight_decay=1e-5),
    scheduler_params=dict(mode="min", patience=5, min_lr=1e-5, factor=0.9),
    scheduler_fn=torch.optim.lr_scheduler.ReduceLROnPlateau,
)

# Training
# tabnet_model.fit(X_train, y_train, epochs=500, validation_data=(X_test, y_test), class_weight=class_weights_tensor)
tabnet_model.fit(
    X_train.values,
    y_train.values,
    eval_set=[(X_val.values, y_val.values)],
    eval_metric=["logloss"],
    max_epochs=500,
    patience=40,  # Set patience for early stopping
    batch_size=64,
    virtual_batch_size=32,
)


def calculate_f1_score(model, X, y_true):
    predictions = model.predict(X)
    y_pred = tf.argmax(predictions, axis=1).numpy()
    f1 = f1_score(y_true, y_pred, average="weighted")
    print(classification_report(y_test, y_pred))
    return f1


f1_score_test = calculate_f1_score(tabnet_model, X_test, y_test)
print(f"F1 Score on Test Set: {f1_score_test}")

# Save or use the trained model
tabnet_model.save("tabnet_model")

# patience = 10
# best_valid_loss = float("inf")
# counter = 0

# # Training loop with manual early stopping
# for epoch in range(1):  # Adjust the number of epochs based on your dataset
#     clf.fit(
#         X_train.values,
#         y_train.values,
#         eval_set=[(X_val.values, y_val.values)],
#         eval_metric=["logloss"],
#         max_epochs=100,
#         batch_size=64,
#         virtual_batch_size=32,
#     )

#     # # Get validation loss from the training history
#     # current_valid_loss = clf.history['valid_balanced_accuracy'][0]

#     # # Print validation loss
#     # print(f"Epoch {epoch + 1}, Validation Loss: {current_valid_loss}")

#     # # Check for early stopping
#     # if current_valid_loss < best_valid_loss:
#     #     best_valid_loss = current_valid_loss
#     #     counter = 0
#     # else:
#     #     counter += 1
#     #     if counter >= patience:
#     #         print(f"Early stopping after {epoch + 1} epochs.")
#     #         break
#     predictions = clf.predict(X_test.values)
#     print(classification_report(y_test, predictions))


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

# # upload to s3 bucket
# s3_client = boto3.client("s3")
# with open(local_save_path, "rb") as data:
#     s3_client.upload_fileobj(
#         data,
#         "amos--models",
#         f"TabNet_f1({f1_test:.4f})_model.pkl",
#     )
#     print(
#         f"Model Saved at amos--models/TabNet_f1({f1_test:.4f})_model.pkl",
#     )
