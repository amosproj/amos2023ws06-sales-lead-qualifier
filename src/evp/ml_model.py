# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>

"""
NOTE THIS IS A TEST FILE AND IS NOT IN USE BY THE DEMO PROCESS
"""

import os

import boto3
import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight, resample
from tqdm import tqdm

data_path = "s3://amos--data--features/preprocessed_data_files/preprocessed_data.csv"
df = pd.read_csv(data_path)


features = df.drop("MerchantSizeByDPV", axis=1)
class_labels = df["MerchantSizeByDPV"]

# split the data into training (80%), validation (10%), and testing (10%) sets
X_train, X_temp, y_train, y_temp = train_test_split(
    features, class_labels, test_size=0.2, random_state=42
)

# Class weights to tackle the class imbalance
class_weights = class_weight.compute_class_weight(
    "balanced", classes=np.unique(y_train), y=y_train
)
class_weight_dict = dict(zip(np.unique(y_train), class_weights))

# Undersampling for the extreme class imbalance
# X_train_resampled, y_train_resampled = resample(X_train[y_train != 0], y_train[y_train != 0],
#                                                 n_samples=len(y_train[y_train == 0]), random_state=42)

# X_train = pd.concat([X_train[y_train == 0], X_train_resampled])
# y_train = pd.concat([y_train[y_train == 0], y_train_resampled])

# Oversampling option for the extreme class imbalance
# smote = SMOTE(random_state=42)
# X_train, y_train = smote.fit_resample(X_train, y_train)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42
)

# train the model on the training set
model = RandomForestClassifier(
    n_estimators=100, class_weight=class_weight_dict, random_state=42
)


epochs = 10
batch_size = 10000
for epoch in range(epochs):
    with tqdm(total=len(X_train), desc=f"Epoch {epoch + 1}/{epochs}") as pbar:
        for i in range(0, len(X_train), batch_size):
            batch_X = X_train[i : i + batch_size]
            batch_y = y_train[i : i + batch_size]

            model.fit(batch_X, batch_y)

            # inference
            y_pred = model.predict(X_test)

            # metrics
            accuracy = accuracy_score(y_test, y_pred)
            f1_test = f1_score(y_test, y_pred, average="weighted")

            # metrics visualized
            pbar.set_postfix(accuracy=accuracy, f1_score=f1_test)
            # update the progress bar every 10,000 elements
            pbar.update(batch_size)

        print(f"F1 Score on Testing Set: {f1_test:.4f}")

        print("Classification Report on Testing Set:")
        c = classification_report(y_test, y_pred)
        print(classification_report(y_test, y_pred))


# calculate F1 score on the testing set
f1_test = f1_score(y_test, y_pred, average="weighted")
print(f"F1 Score on Testing Set: {f1_test:.4f}")

print("Classification Report on Testing Set:")
print(classification_report(y_test, y_pred))

# save the model
model_type = type(model).__name__
local_directory = "../data/models/"
os.makedirs(local_directory, exist_ok=True)
local_save_path = os.path.join(
    local_directory,
    f"{model_type.lower()}_epochs({epochs})_f1({f1_test:.4f})_model.joblib",
)
# local_save_path = "../data/models/{model_type.lower()}_epochs({epochs})_f1({f1_test})_model.joblib"
s3_save_path = f"s3://amos--models/{model_type.lower()}_epochs({epochs})_f1({f1_test})_model.joblib"
joblib.dump(model, local_save_path)

# upload to s3 bucket
s3_client = boto3.client("s3")
with open(local_save_path, "rb") as data:
    s3_client.upload_fileobj(
        data,
        "amos--models",
        f"{model_type.lower()}_epochs({epochs})_f1({f1_test:.4f})_model.joblib",
    )
