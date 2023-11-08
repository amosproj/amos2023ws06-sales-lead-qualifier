# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>

# Dockerfile
FROM python:3.10

# set the working directory
WORKDIR /demo/ml/code

COPY ../../Pipfile .
COPY ../../Pipefile.lock .

# install pipenv the accociated dependencies
RUN pip install pipenv && pipenv install

# copy code, data, and models
COPY ../evp_demo.py /demo/ml/code
COPY ../evp/evp.py /demo/ml/code
COPY ../database/database_dummy.py /demo/ml/code
COPY ../database/models.py /demo/ml/code
COPY ../database/parsers.py /demo/ml/code
COPY ../database/database_leads.json /demo/ml/data
COPY ../evp/probability_model.joblib /demo/ml/model
COPY ../evp/life_time_model.joblib /demo/ml/model

# run the training algorithm for AWS SageMaker
ENV SAGEMAKER_PROGRAM ../evp_demo.py
