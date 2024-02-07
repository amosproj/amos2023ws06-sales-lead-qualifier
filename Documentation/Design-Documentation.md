<!--
SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>
SPDX-FileCopyrightText: 2024 Ahmed Sheta <ahmed.sheta@fau.de>
SPDX-FileCopyrightText: 2024 Simon Zimmermann <tim.simon.zimmermann@fau.de>
-->

# Introduction

This application serves as a pivotal tool employed by our esteemed industry
partner, SumUp, for the enrichment of information pertaining to potential leads
garnered through their sign-up website. The refined data obtained undergoes
utilization in the prediction of potential value that a lead could contribute to
SumUp, facilitated by a sophisticated machine learning model. The application is
branched into two integral components: the Base Data Collector (BDC) and the
Merchant Size Predictor (MSP).

## Component Diagram

![Component Diagram](Media/component-diagram.svg)

## External Software

### Lead Form (LF)

The _Lead Form_ is submitted by every new lead and provides a small set of data
about the lead.

### Customer Relationship Management (CRM)

The project output is made available to the sales team. This can be done in
different ways, e.g. writing to a Google Sheet or pushing directly to
SalesForce.

## Components

## Base Data Collector (BDC)

### General description

The Base Data Collector (BDC) plays a crucial role in enriching the dataset
related to potential client leads. The initial dataset solely comprises
fundamental lead information, encompassing the lead's first and last name, phone
number, email address, and company name. Recognizing the insufficiency of this
baseline data for value prediction, the BDC is designed to query diverse data
sources, incorporating various Application Programming Interfaces (APIs), to
enrich the provided lead data.

### Design

The different data sources are organised as steps in the program. Each step
extends from a common parent class and implements methods to validate that it
can run, perform the data collection from the source and perform clean up and
statistics reports for itself. These steps are then collected in a pipeline
object sequentially performing the steps to enhance the given data with all
chosen data sources. The data sources include:

- inspecting the possible custom domain of the email address.
- retrieving multiple data from the Google Places API.
- analysing the sentiment of Google reviews using GPT.
- inspecting the surrounding areas of the business using the Regional Atlas API.
- searching for company-related data using the OffeneRegisterAPI.
- performing sentiment analysis on reviews using GPT-4 model.

### Data storage

All data for this project is stored in CSV files in the client's AWS S3 storage.
The files here are split into three buckets. The input data and enhanced data
are stored in the events bucket, pre-processed data ready for use of ML models
is stored in the features bucket and the used model and inference is stored in
the model bucket. Data preprocessing Following data enrichment, a pivotal phase
in the machine learning pipeline is data preprocessing, an essential process
encompassing scaling operations, numerical outlier elimination, and categorical
one-hot encoding. This preprocessing stage serves transforms the output
originating from the BDC into feature vectors, thereby rendering them amenable
for predictive analysis by the machine learning model.

## Merchant Size Predictor (MSP) / Estimated Value Predictor (EVP)

### Historical Note

The primary objective of the Estimated Value Predictor was initially oriented
towards forecasting the estimated life-time value of leads. However, this
objective evolved during the project's progression, primarily influenced by
labelling considerations. The main objective has therefore changed to predicting
only the size of a given lead, which can then be used as an indication for their
potential life-time value. As a consequence, the component in questions is now
(somewhat inconsistently) either referred to as the Estimated Value Predictor
(EVP) or as the Merchant Size Predictor (MSP).

### Design

In the context of Merchant Size Prediction, our aim is to leverage pre-trained
ML models on new lead data. By applying these models, we intend to predict the
potential Merchant Size, thereby assisting SumUp in prioritizing leads and
making informed decisions on which leads to contact first. This predictive
approach enhances the efficiency of lead management and optimizes resource
allocation for maximum impact.

The machine learning model, integral to the MSP, undergoes training on
proprietary historical data sourced from SumUp. The training process aims to
discern discriminative features that effectively stratify each class within the
Merchant Size taxonomy. It is imperative to note that the confidentiality of the
underlying data prohibits its public disclosure.
