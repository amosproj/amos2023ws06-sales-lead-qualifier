<!--
SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>
-->

# Limitations of Twitter API for user information retrieval and biased sentiment analysis

This documentation highlights the research and the limitations regarding customer information retrieval and unbiased sentiment analysis when using Twiiter API (tweepy). Two primary constraints include the absence of usernames in provided customer data and inherent biases in tweet content, which significantly impact the API's utility for these purposes.

## Limitation 1: Absence of usernames in provided customer data:

A fundamental shortfall within the Twitter API (tweepy) lies in the unavailability of usernames in the customer information obtained through its endpoints. Twitter (X) primarily uses usernames as identifiers to retrieve user information, on the other hand we only have the Full Names of the customers as indicators.

## Limitation 2: Inherent Biases in Tweet Content for Sentiment Analysis:

Conducting sentiment analysis on tweets extracted via the Twitter API poses challenges due to inherent biases embedded in tweet done by the customer themselves. Sentiment analysis on something like reviews would be definitely helpful. However, sentiment analysis done on tweet written by customer themselves would deeply imposes biases.

## Links to Twitter's API documentation:

tweepy documentaion: https://docs.tweepy.org/en/stable/
