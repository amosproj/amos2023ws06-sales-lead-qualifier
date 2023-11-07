<!--
SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2023 Simon Zimmermann
SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>
-->

# Software Architecture

The goal of this project is to qualify sales leads in different ways, both in terms of
their likelihood of becoming customers and the size of their potential revenue.

## External Software

### Lead Form (LF)

The _Lead Form_ is submitted by every new lead and provides a small set of data about the lead.

### Customer Relationship Management (CRM)

The project output is made available to the sales team.
This can be done in different ways, e.g. writing to a Google Sheet or pushing directly to SalesForce.

## Components

### Base Data Collector (BDC)

The _Base Data Collector_ fullfills the task of collecting data about a lead from various online sources.
All collected data is then stored in a database for later retrieval in a standardized manner.

### Expected Value Predictor (EVP)

The _Expected Value Predictor_ estimates the expected value of a lead by analyzing the collected data of that lead.
This is done using a machine learning approach, where the EVP is trained on historical data.
Preprocessing of both the collected and the historical data should be done inside the EVP,
if it goes beyond the scope of standardization.

### Controller

The _Controller_ is an optional component, which coordinates BDC, EVP and the external components as a centralized control instance.
That said, another (more advanced) approach would be to use a pipelined control flow, driven by web hooks or similar signals.

## Diagrams

### Component Diagram

![Component Diagram](Media/component-diagram.svg)

### Sequence Diagram

![Sequence Diagram](Media/sequence-diagram.svg)

### Controller Workflow Diagram

![Controller Workflow Diagram](Media/controller-workflow-diagram.jpg)
