<!--
SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2023 Fabian-Paul Utech <f.utech@gmx.net>
SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>
SPDX-FileCopyrightText: 2024 Simon Zimmermann <tim.simon.zimmermann@fau.de>
-->

# Miscellaneous Content

This file contains content that was moved over from our [Wiki](https://github.com/amosproj/amos2023ws06-sales-lead-qualifier/wiki), which we gave up in favor of having the documentation available more centrally. The contents of this file might to some extend overlap with the contents found in other documentation files.

# Knowledge Base

## AWS

1. New password has to be >= 16 char and contain special chars
2. After changing the password you have to re-login
3. Add MFA (IAM -> Users -> Your Name -> Access Info)
4. MFA device = FirstName.LastName like the credential
5. Re-login
6. Get access keys:
   - IAM -> Users -> Your Name -> Access Info -> Scroll to Access Keys
   - Create new access key (for local development)
   - Accept the warning
   - Copy the secret key to your .env file
   - Don’t add description tags to your key

## PR Management:

1. Create PR
2. Link issue
3. Other SD reviews the PR
   - Modification needed?
     - Fix/Discuss issue in the GitHub comments
   - Make new commit
   - Return to step 3
   - No Modification needed
   - Reviewer approves PR
4. PR creator merges PR
5. Delete the used branch

## Branch-Management:

- Remove branches after merging
- Add reviews / pull requests so others check the code
- Feature branches with dev instead of main as base

## Pre-commit:

```[bash]
# If not installed yet
pip install pre-commit

# pre-commit hooks now automatically are executed before every commit
python -m pre-commit install

# execute pre-commit manually
python pre-commit
```

## Features

- Existing Website (Pingable, SEO-Score, DNS Lookup)
- Existing Google Business Entry (using the [Google Places API](https://developers.google.com/maps/documentation/places/web-service?hl=de)
  - Opening Times
  - Number, Quality of Ratings
  - Overall “completeness” of the entry/# of available datapoints
  - Price category
  - Phone Number (compare with lead form input)
  - Website (compare with lead form input)
  - Number of visitors (estimate revenue from that?)
  - Product recognition from images
  - Merchant Category (e.g. cafe, restaurant, retailer, etc.)
- Performance Indicators (NorthData, some other API)
  - Revenue (as I understodd, this should be > 5000$/month)
  - Number of Employees
  - Bundesanzeiger / Handelsregister (Deutschland API)
- Popularity: Insta / facebook followers or website ranking on google
- Business type: google or website extraction (maybe with ChatGPT)
- Size of business: To categorize leads to decide whether they need to deal with a salesperson or self-direct their solution
- Business profile
- Sentiment Analysis: https://arxiv.org/pdf/2307.10234.pdf

## Storage

- Unique ID for Lead (Felix)?
- How to handle frequent data layout changes at S3 (Simon)?
- 3 stage file systems (Felix) vs. DB (Ruchita)?
- 3 stage file system (Felix):
  - BDC trigger on single new lead entries or batches
  - After BDC enriched the data => store in a parquet file in the events folder with some tag
  - BDC triggers the creation of the feature vectors
  - Transform the data in the parquet file after it was stored in the events file and store them in the feature folder with the same tag
  - Use the data as a input for the model, which is triggered after the creation of the input, and store the results in the model folder
- Maybe the 3 stage file system as a part of the DB and hide the final decision behind the database abstraction layer (Simon)?

## Control flow (Berkay)

- Listener
- MessageQueue
- RoutingQueue

Listener, as the name suggests, listens for incoming messages from other component, such as BDC, EVP, and enqueues these messages in messageQueue to be “read” and processed. If there are not incoming messages, it is in idle status. messageQueue is, where listened messages are being processed. After each message is processed by messageQueue,it is enqueued in routingQueue, to be routed to corresponding component. Both messageQueue and routingQueue are in idle, if there are no elements in queues. Whole concept of Controller is multi-threaded and asynchronous. While it accepts new incoming messages, it processes messages and at the same time routes some other messages.

## AI

> `expected value = life-time value of lead x probability of the lead becoming a customer`

AI models needed that solve a regression or probability problem

### AI Models

- Classification:
  - Decision Trees
  - Random Forest
  - Neural Networks
  - Naïve Bayes

### What data do we need?

- Classification: Labeled data
- Probability: Data with leads and customers

### ML Pipeline

1. Preprocessing
2. Feature selection
3. Dataset split / cross validation
4. Dimensional reduction
5. Training
6. Testing / Evaluation
7. Improve performance
   - Batch Normalization
   - Optimizer
   - L1 / L2 regularization: reduced overfitting by regularize the model
   - Dropout (NN)
   - Depth and width (NN)
   - Initialization techniques (NN: Xavier and He)
     - He: Layers with ReLu activation
     - Xavier: Layers with sigmoid activation

# Troubleshooting

## Build

### pipenv

#### install stuck

```[bash]
pipenv install –dev
```

**Solution**: Remove .lock file + restart PC

### Docker

#### VSCode

Terminal can't run docker image (on windows)

- **Solution**: workaround with git bash or with ubuntu

### Testing

#### Reuse

don't analyze a certain part of the code with reuse
**Solution**:

```[bash]
# REUSE-IgnoreStart
  ...
# REUSE-IgnoreEnd
```

#### Failed checks

1. Go to the specific pull request or Actions [Actions](https://github.com/amosproj/amos2023ws06-sales-lead-qualifier/actions)
2. Click "show all checks"
3. Click "details"
4. Click on the elements with the "red marks"

## BDC

### Google Places API

Language is adjusted to the location from which the API is run

- **Solution**: adjust the language feature, documentation in [Google Solution](https://developers.google.com/places/web-service/search#FindPlaceRequests)

Google search results are based on the location from which the API is run

- **Solution**: Pass a fixed point in the center of the country / city / area of the company (OSMNX) as a location bias, documentation in
  [Google Solution](https://developers.google.com/places/web-service/search#FindPlaceRequests)

## Branch-Management

### Divergent branch

Commits on local and remote are not the same

- **Solution**:
  1. Pull remote changes
  2. Rebase the changes
  3. Solve any conflict during any commit you get from remote
