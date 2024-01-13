# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>


import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split

data_path = "s3://amos--data--features/preprocessed_data_files/preprocessed_data.csv"
df = pd.read_csv(data_path)


features = df.drop("MerchantSizeByDPV", axis=1)
class_labels = df["MerchantSizeByDPV"]

# split the data into training (80%), validation (10%), and testing (10%) sets
X_train, X_temp, y_train, y_temp = train_test_split(
    features, class_labels, test_size=0.2, random_state=42
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42
)

# train the model on the training set
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# inference
y_test_pred = model.predict(X_test)

# calculate F1 score on the testing set
f1_test = f1_score(y_test, y_test_pred, average="weighted")
print(f"F1 Score on Testing Set: {f1_test:.4f}")

print("Classification Report on Testing Set:")
print(classification_report(y_test, y_test_pred))
