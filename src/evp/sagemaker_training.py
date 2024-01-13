# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>


import boto3
import pandas as pd
from sagemaker import get_execution_role
from sagemaker.sklearn import SKLearn

region = "eu-central-1"

s3_bucket = "amos--data--features"
s3_key = "preprocessed_data_files/preprocessed_data.csv"

role = get_execution_role()

# Download the CSV file from S3
s3 = boto3.client("s3", region_name=region)
s3.download_file(s3_bucket, s3_key, "preprocessed_data.csv")

df = pd.read_csv("preprocessed_data.csv")

script_path = ""
sklearn_estimator = SKLearn(
    entry_point=script_path,
    role=role,
    train_instance_count=1,
    train_instance_type="ml.m5.large",
    sagemaker_session=boto3.Session(region_name=region),
)

# train the model on SageMaker
sklearn_estimator.fit({"train": "s3://{}/{}".format(s3_bucket, s3_key)})
