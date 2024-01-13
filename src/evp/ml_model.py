# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>


import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split

data_path = "s3://amos--data--features/preprocessed_data_files/preprocessed_data.csv"
df = pd.read_csv(data_path)

# Assuming 'features' is a list of feature columns and 'target' is the target column
features = df.drop("MerchantSizeByDPV", axis=1)
class_labels = df["MerchantSizeByDPV"]

# split the data into training (80%), validation (10%), and testing (10%) sets
X_train, X_temp, y_train, y_temp = train_test_split(
    features, class_labels, test_size=0.2, random_state=42
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42
)

# Train the model on the training set
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions on the testing set (unseen data during training)
y_test_pred = model.predict(X_test)

# Calculate F1 score on the testing set
f1_test = f1_score(y_test, y_test_pred, average="weighted")
print(f"F1 Score on Testing Set: {f1_test:.4f}")

# Optionally, print other metrics for the testing set
print("Classification Report on Testing Set:")
print(classification_report(y_test, y_test_pred))
