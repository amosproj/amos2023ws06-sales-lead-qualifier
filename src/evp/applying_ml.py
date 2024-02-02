# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 Ahmed Sheta <ahmed.sheta@fau.de>

import os
import pickle
import sys
from io import BytesIO

import boto3
import joblib
import pandas as pd

######################### preprocessing the leads ##################################
current_dir = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
parent_dir = os.path.join(current_dir, "..")
sys.path.append(parent_dir)
from preprocessing import Preprocessing

preprocessor = Preprocessing(filter_null_data=False, historical_data=False)
leads_enriched_path = "s3://amos--data--events/leads/enriched.csv"
preprocessor.data_path = leads_enriched_path
preprocessor.prerocessed_data_output_path = (
    "s3://amos--data--events/leads/preprocessed_leads_data.csv"
)
df = preprocessor.implement_preprocessing_pipeline()
preprocessor.save_preprocessed_data()

############################## adapting the preprocessing files ###########################
# load the data from the CSV files
historical_preprocessed_data = pd.read_csv(
    "s3://amos--data--features/preprocessed_data_files/preprocessed_data.csv"
)
toBePredicted_preprocessed_data = pd.read_csv(
    "s3://amos--data--events/leads/preprocessed_leads_data.csv"
)

# Get the columns in the order of f2.csv
historical_columns_order = historical_preprocessed_data.columns

# Create missing columns in f1.csv and fill with 0
missing_columns = set(historical_columns_order) - set(
    toBePredicted_preprocessed_data.columns
)
for column in missing_columns:
    toBePredicted_preprocessed_data[column] = 0

for column in toBePredicted_preprocessed_data.columns:
    if column not in historical_columns_order:
        toBePredicted_preprocessed_data = toBePredicted_preprocessed_data.drop(
            column, axis=1
        )

# reorder columns
toBePredicted_preprocessed_data = toBePredicted_preprocessed_data[
    historical_columns_order
]

toBePredicted_preprocessed_data.to_csv(
    "s3://amos--data--events/leads/toBePredicted_preprocessed_data_updated.csv",
    index=False,
)

# check if columns in both dataframe are in same order and same number
assert list(toBePredicted_preprocessed_data.columns) == list(
    historical_preprocessed_data.columns
), "Column names are different"

####################### Applying ML model on lead data ####################################

bucket_name = "amos--models"
file_key = "models/lightgbm_epochs(1)_f1(0.6375)_numclasses(5)_model_updated.pkl"  # adjust according to the desired model

# create an S3 client
s3 = boto3.client("s3")

# download the file from S3
response = s3.get_object(Bucket=bucket_name, Key=file_key)
model_content = response["Body"].read()

# load model
with BytesIO(model_content) as model_file:
    model = joblib.load(model_file)

data_path = "s3://amos--data--events/leads/toBePredicted_preprocessed_data_updated.csv"
df = pd.read_csv(data_path)
input = df.drop("MerchantSizeByDPV", axis=1)

predictions = model.predict(input)
size_mapping = {0: "XS", 1: "S", 2: "M", 3: "L", 4: "XL"}
remapped_predictions = [size_mapping[prediction] for prediction in predictions]

# print(remapped_predictions)

enriched_data = pd.read_csv("s3://amos--data--events/leads/enriched.csv")

# first 5 columns: Last Name,First Name,Company / Account,Phone,Email,
raw_data = enriched_data.iloc[:, :5]
raw_data["PredictedMerchantSize"] = remapped_predictions

raw_data.to_csv(
    "s3://amos--data--events/leads/predicted_MerchantSize_of_leads.csv", index=True
)
print(
    f"Saved the predicted Merchant Size of the leads at s3://amos--data--events/leads/predicted_MerchantSize_of_leads.csv"
)
