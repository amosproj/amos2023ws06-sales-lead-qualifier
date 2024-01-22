<!--
SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>
-->

# ML Experiment Documentation

## Introduction

The Expected Value Predictor (EVP) aims to predict the Merchant Size class of Sumup's costumers.

## Dataset

Given the historical data, the data runs through the collection pipeline, the output of the pipeline is used as feature columns for the EVP, while the Merchant Size is the class labels. The Merchant Size is divided into 5 classes: XS,S,M,L,XL. Since the labels are ordinal data, discrete labeling (0,1,2,3,4) has been adopted. The feature categorical data has been one-hot encoded while the numerical data. It is worth noting tat around 75% of the data is classified as XS, there is an extreme class imbalance in the underlying data.

## Experimental Attempts

According to free lunch theorem, there is no universal model or methodology that is top performing on every problem or data, therefore multiple attempts are crucal. In this section, we will document the experiments we tried and their corresponding performance and outputs.

### Random Forest Classifier

Random Forest Classifier with 100 estimators has been been able to achieve an overall F1 score 0.62 and scores of 0.81,0.13,0.09,0.08 and 0.15 for classes XS, S, M, L and XL repectively.

Classification Report on Testing Set:
precision recall f1-score support

           0       0.74      0.88      0.81      5273
           1       0.21      0.09      0.13      1310
           2       0.14      0.07      0.09       436
           3       0.12      0.06      0.08       193
           4       0.13      0.20      0.15        76

    accuracy                           0.66      7288

macro avg 0.27 0.26 0.25 7288
weighted avg 0.59 0.66 0.62 7288

### Support Vector Machine Classifier Model

Training Support Vector Machine (SVM) took a while such that the training never ended. It is believed that it is the case because SVMs are very sensitive to the misclassifications and it finds a hard time minimizing them, given the data.

### Fully Connected Neural Networks Classifier Model

Fully Connected Neural Networks (FCNN) achieved overall lower performance than that Random Forest Classifier, mainly it had f1 score 0.84 on the XS class, while having 0.00 f1 scores on the other class, it learned only the XS class.

### Fully Connected Neural Networks Regression Model

There has been an idea written in the scientific paper "Inter-species cell detection -
datasets on pulmonary hemosiderophages in equine, human and feline specimens" by Marzahl et al. where they proposed using regression model on a classification task. The idea is to train the regression model on the class values, whereas the model predicts a continous values and learns the relation between the classes. The output is then subjected to threshholds (0-0.49,0.5-1.49,1.5-2.49,2.5-3.49,3.5-4.5) for classes XS, S, M, L, XL respectivly. This yielded better performance than the FCNN classifier but still was worse than that of the Random Forest.

### XGBoost Classifier Model

Until Sprint 11 (22.01.2024), XGBoost is the top performing model, with overall F1 0.64 and relatively better results than that of the Random Forest Classifier. Number of rounds of the results is 10000.

Classification Report on Testing Set:
precision recall f1-score support

           0       0.75      0.96      0.84      5295
           1       0.29      0.08      0.13      1280
           2       0.22      0.05      0.08       454
           3       0.17      0.04      0.06       189
           4       0.22      0.13      0.16        70

    accuracy                           0.72      7288

macro avg 0.33 0.25 0.25 7288
weighted avg 0.62 0.72 0.64 7288

### Reducing the classifying task into 3 classes

The The idea is to group classes S,M,L,XL into one class and to train the model on XS, (S,M,L) and XL class. This way, the XGBoost model achieved better results of overall f1 score 0.7.
Classification Report on Testing Set:
precision recall f1-score support

           0       0.77      0.92      0.84      5295
           1       0.51      0.24      0.33      1923
           2       0.23      0.10      0.14        70

    accuracy                           0.73      7288

macro avg 0.50 0.42 0.43 7288
weighted avg 0.69 0.73 0.70 7288

### Reducing the classifying task into 2 classes

The idea is to group classes S,M,L,XL into one class (1) and to train the model on XS and "others" classes. The model failed to learn the "others" class and didn't yield any satifying results
