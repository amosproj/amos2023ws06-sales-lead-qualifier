<!--
SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2024 Felix Zailskas <felixzailskas@gmail.com>
SPDX-FileCopyrightText: 2024 Ahmed Sheta <ahmed.sheta@fau.de>
-->

# Classifier Comparison

This document compares the results of the following classifiers on the enriched and
preprocessed data set from the 22.01.2024.

- Quadratic Discriminant Analysis (QDA)
- Ridge Classifier
- Random Forest
- Support Vecotr Machine (SVM)
- Fully Connected Neural Networks Classifier Model (FCNNC)
- Fully Connected Neural Networks Regression Model (FCNNR)
- XGBoost Classifier Model
- K Nearest Neighbor Classifier (KNN)
- Bernoulli Naive Bayes Classifier

Each model type was tested on two splits of the data set. The used data set has five
classes for prediction corresponding to different merchant sizes, namely XS, S, M, L, and XL.
The first split of the data set used exactly these classes for the prediction corresponding
to the exact classes given by SumUp. The other data set split grouped the classes S, M, and L
into one new class resulting in three classes of the form {XS}, {S, M, L}, and {XL}. While
this does not exactly correspond to the given classes from SumUp, this simplification of
the prediction task generally resulted in a better F1-score across models.

## Experimental Attempts

According to free lunch theorem, there is no universal model or methodology that is top performing on every problem or data, therefore multiple attempts are crucal. In this section, we will document the experiments we tried and their corresponding performance and outputs.

## Models not performing well

### Support Vector Machine Classifier Model

Training Support Vector Machine (SVM) took a while such that the training never ended. It is believed that it is the case because SVMs are very sensitive to the misclassifications and it finds a hard time minimizing them, given the data.

### Fully Connected Neural Networks Classifier Model

Fully Connected Neural Networks (FCNN) achieved overall lower performance than that Random Forest Classifier, mainly it had f1 score 0.84 on the XS class, while having 0.00 f1 scores on the other class, it learned only the XS class. the FCNN consisted of 4 layers overall, RELU activation function in each layer, except in the logits layer the activation function is Softmax. The loss functions investigated were Cross-Entropy and L2 Loss. The Optimizers were Adam and Sctohastic Gradient Descent. Moreover, Skip connections, L1 and L2 Regularization techniques and class weights have been investigated as well. Unfortunately we haven't found any FCNN that outperforms the simpler ML models.

### Fully Connected Neural Networks Regression Model

There has been an idea written in the scientific paper "Inter-species cell detection -
datasets on pulmonary hemosiderophages in equine, human and feline specimens" by Marzahl et al. where they proposed using regression model on a classification task. The idea is to train the regression model on the class values, whereas the model predicts a continous values and learns the relation between the classes. The output is then subjected to threshholds (0-0.49,0.5-1.49,1.5-2.49,2.5-3.49,3.5-4.5) for classes XS, S, M, L, XL respectivly. This yielded better performance than the FCNN classifier but still was worse than that of the Random Forest.

### QDA & Ridge Classifier

Both of these classifiers could not produce a satisfactory performance on either data set
split. While the prediction on the XS class was satisfactory (F1-score of ~0.84) all other
classes had F1-scores of ~0.00-0.15. For this reason we are not considering these predictors
in future experiments. This resulted in an overall F1-score of ~0.11, which is significantly
outperformed by the other tested models.

## Well performing models

### Random Forest Classifier

Random Forest Classifier with 100 estimators has been been able to achieve an overall F1-score of 0.62 and scores of 0.81, 0.13, 0.09, 0.08 and 0.15 for classes XS, S, M, L and XL respectively.

### Overall Results

Note:
The Random Forest Classifier used 100 estimators.
The KNN classifier used a distance based weighting for the evaluated neighbors and considered 10 neighbors in the 5-class split and 19 neighbors for the 3-class split.
The XGBoost was trained for 10000 rounds.

In the following table we can see the model's overall weighted F1-score on the 3-class and
5-class data set split.

|         | KNN    | Naive Bayes | Random Forest | XGBoost |
| ------- | ------ | ----------- | ------------- | ------- |
| 5-Class | 0.6314 | 0.6073      | 0.6150        | 0.6442  |
| 3-Class | 0.6725 | 0.6655      | 0.6642        | 0.6967  |

We can see that all classifiers perform better on the 3-class data set split and that the XGBoost classifier is the best performing for both data set splits.

### Results for each class

#### 5-class split

In the following table we can see the F1-score of each model for each class in the 5-class split:

| Class | KNN  | Naive Bayes | Random Forest | XGBoost |
| ----- | ---- | ----------- | ------------- | ------- |
| XS    | 0.82 | 0.83        | 0.81          | 0.84    |
| S     | 0.15 | 0.02        | 0.13          | 0.13    |
| M     | 0.08 | 0.02        | 0.09          | 0.08    |
| L     | 0.06 | 0.00        | 0.08          | 0.06    |
| XL    | 0.18 | 0.10        | 0.15          | 0.16    |

For every model we can see that the predictions on the XS class are significantly better than every other class. TFor the KNN, Random Forest, and XGBoost all perform similar, having second best classes S and XL and worst classes M and L. The Naive Bayes classifier performs significantly worse on the S, M, and L classes and has second best class XL.

#### 3-class split

In the following table we can see the F1-score of each model for each class in the 3-class split:

| Class | KNN  | Naive Bayes | Random Forest | XGBoost |
| ----- | ---- | ----------- | ------------- | ------- |
| XS    | 0.83 | 0.82        | 0.81          | 0.84    |
| S,M,L | 0.27 | 0.28        | 0.30          | 0.33    |
| XL    | 0.16 | 0.07        | 0.13          | 0.14    |

For the 3-class split we observe similar performance for the XS and {S, M, L} classes for each model, while the XGBoost model slightly outperforms the other models. The KNN classifier is performing the best on the XL class while the Naive Bayes classifier performs worst. Interestingly, we can observe that the performance of the models on the XS class was barely affected by the merging of the s, M, and L classes while the performance on the XL class got worse for all of them. This needs to be considered, when evaluating the overall performance of the models on this data set split.
