<!--
SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2024 Felix Zailskas <felixzailskas@gmail.com>
-->

# Unused Ideas

This document lists ideas and implementations which have either not been tried yet or have been deprecated as they are not used in the current product version but still carry some conceptual value.

## Deprecated

The original implementation of the deprecated modules can be found in the `deprecated/` directory.

### Controller

The controller module was originally planned to be used as a communication device between EVP and BDC. Whenever the salesperson interface would register a new lead the controller is supposed to trigger the BDC pipeline to enrich the data of that lead and preprocess it to create a feature vector. The successful completion of the BDC pipeline is then registered at the controller which will then trigger an inference of the EVP to compute the predicted merchant size and write this back to the lead data. The computed merchant size can then be used to rank the leads and allow the salesperson to decide the value of the leads and which one to call.

The current implementation of the module supports queueing messages from the BDC and EVP as indicated by their type. Depending on the message type the message is then routed to the corresponding module (EVP or BDC). The actual processing of the messages by the modules is not implemented. All of this is done asynchronously by using the python threading library.

## Possible ML improvements

### Creating data subsets

The data collected by the BDC pipeline has not been refined to only include semantically valuable data fields. It is possible that some data fields contain no predictive power. This would mean they are practically polluting the dataset with unnecessary information. A proper analysis of the predictive power of all data fields would allow cutting down on the amount of data for each lead, reducing processing time and possibly make predictions more precise. This approach has been explored very briefly by the subset 1 as described in `Classifier-Comparison.md`. However, the choice of included features has not been justified by experiments making them somewhat arbitrary. Additionally, an analysis of this type could give insights on which data fields to expand on and what new data one might want to collect to increase the EVP's performance in predicting merchant sizes.

Possibly filtering data based on some quality metric could also improve general performance. The regional_atlas_score and google_confidence_score have been tried for this but did not improve performance. However, these values are computed somewhat arbitrarily and implementing a more refined quality metric might result in more promising results.
