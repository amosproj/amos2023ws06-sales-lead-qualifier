<!--
SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2024 Felix Zailskas <felixzailskas@gmail.com>
-->

# Classifier Comparison

This document compares the results of the following classifiers on the enriched and
preprocessed data set from the 22.01.2024.

- Quadratic Discriminant Analysis (QDA)
- Ridge Classifier
- K Nearest Neighbor Classifier (KNN)
- Bernoulli Naive Bayes Classifier

Each model type was tested on two splits of the data set. The used data set has five
classes for prediction corresponding to different merchant sizes, namely XS, S, M, L, and XL.
The first split of the data set used exactly these classes for the prediction corresponding
to the exact classes given by SumUp. The other data set split grouped the classes S, M, and L
into one new class resulting in three classes of the form {XS}, {S, M, L}, and {XL}. While
this does not exactly correspond to the given classes from SumUp, this simplification of
the prediction task generally resulted in a better F1-score across models.

## QDA & Ridge Classifier

Both of these classifiers could not produce a satisfactory performance on either data set
split. While the prediction on the XS class was satisfactory (F1-score of ~0.84) all other
classes had F1-scores of ~0.00-0.15. For this reason we are not considering these predictors
in future experiments. This resulted in an overall F1-score of ~0.11, which is significantly
outperformed by the other tested models.

## KNN & NB

### Overall Results

In the following table we can see the model's overall weighted F1-score on the 3-class and
5-class data set split.

|               | KNN          | Naive Bayes |
|---------------|--------------|-------------|
| 5-Class       | 0.6314       | 0.6073      |
| 3-Class       | 0.6725       | 0.6655      |

We can see that both classifiers perform better on the 3-class data set split and that the
KNN classifier outperforms the Naive Bayes classifier. The KNN classifier used a distance
based weighting for the evaluated neighbors and considered 10 neighbors in the 5-class split
and 19 neighbors for the 3-class split. These values were found to be optimal based on
empirical analysis.

### Results for each class

#### 5-class split

In the following table we can see the F1-score of each model for each class in the 5-class split:

| Class    | KNN        | Naive Bayes |
|----------|------------|-------------|
| XS       | 0.82       | 0.83        |
| S        | 0.15       | 0.02        |
| M        | 0.08       | 0.02        |
| L        | 0.06       | 0.00        |
| XL       | 0.18       | 0.10        |

Just like in the overall results we can observe that the KNN classifier generally performs
better for each class except the XS class, where both models perform roughly the same.
Interestingly, it predicts almost equally well for the S and XL classes and for the M and L classes respectively. This trend cannot be seen for the Naive Bayes classifier.

#### 3-class split

In the following table we can see the F1-score of each model for each class in the 3-class split:

| Class    | KNN        | Naive Bayes |
|----------|------------|-------------|
| XS       | 0.83       | 0.82        |
| S,M,L    | 0.27       | 0.28        |
| XL       | 0.16       | 0.07        |

For the 3-class split we observe similar performance for the XS and {S, M, L} classes for
each model. However, the KNN classifier performs significantly better on the XL class.
Furthermore, we observe that the performance on the XS class was barely affected by the
merging of the S, M, and L classes, while the performance on the XL class decreased due
to this preprocessing step.
