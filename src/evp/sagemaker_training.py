# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>


import os

import boto3
import pandas as pd
import sagemaker
from sagemaker import get_execution_role
from sagemaker.pytorch import PyTorch
from sagemaker.sklearn import SKLearn

region = "eu-central-1"

s3_bucket = "amos--data--features"
s3_key = "preprocessed_data_files/preprocessed_data.csv"

role_arn = "arn:aws:iam::502131121246:role/amos-ext-lab-sagemaker-role"

sagemaker_session = sagemaker.Session()


# Download the CSV file from S3
s3 = boto3.client("s3", region_name=region)
s3.download_file(s3_bucket, s3_key, "preprocessed_data.csv")

df = pd.read_csv("preprocessed_data.csv")

script_path = "nn_model.py"

model_dir = "s3://{}/model".format("amos--models")

# sklearn_estimator = SKLearn(
#     entry_point=script_path,
#     role=role,
#     train_instance_count=1,
#     train_instance_type="ml.m5.large",
#     sagemaker_session=boto3.Session(region_name=region),
#     output_path=model_dir,
# )


pytorch_estimator = PyTorch(
    entry_point="nn_model.py",
    source_dir=os.getcwd(),
    role=role_arn,
    framework_version="1.8",
    py_version="py3",
    instance_count=1,
    instance_type="ml.g4dn.xlarge",
    output_path=model_dir,
    sagemaker_session=sagemaker_session,
)

# train the model on SageMaker
pytorch_estimator.fit({"train": "s3://{}/{}".format(s3_bucket, s3_key)})

hyperparameters = {
    "epochs": 1,
    "batch-size": 128,
}

# Start the training job
pytorch_estimator.fit(
    {"training": "s3://{}/{}".format(s3_bucket, s3_key)},
    job_name="job1_NN_model",
    hyperparameters=hyperparameters,
)
