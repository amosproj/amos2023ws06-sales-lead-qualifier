<!--
SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>
-->

# Data Field Definitions

This document outlines the data fields obtained for each lead. The data can be sourced from the online _Lead Form_ or be retrieved from the internet using APIs. It is currently unfinished, and will be updated once we finalise what data points will be used for the AI model.

The data types selected are on the assumption that we’re using the PostgreSQL database.

## Data Field Table

| Field Name                       | Data Type | Description                                                                                           | Validation Rules                 |  Data Source   | Sample Data (if available)                                                                                                                                                                                                                  |   Name Convention    |
| -------------------------------- | :-------: | ----------------------------------------------------------------------------------------------------- | -------------------------------- | :------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------: |
| First Name                       |   text    | First name of business owner                                                                          |                                  |   Lead Form    |                                                                                                                                                                                                                                             |      first_name      |
| Last Name                        |   text    | Last name of business owner                                                                           |                                  |   Lead Form    |                                                                                                                                                                                                                                             |      last_name       |
| Email Address                    |   text    | Owner’s email address (doesn’t specify business or personal)                                          |                                  |   Lead Form    |                                                                                                                                                                                                                                             |    email_address     |
| Telephone Number                 |  varchar  | Owner’s telephone number (doesn’t specify business or personal)                                       | Length dependent on country code |   Lead Form    |                                                                                                                                                                                                                                             |     phone_number     |
| Annual Income from Card Payments |   enum    | Enumerated income-ranges that indicate how much of the company’s income is comprised of card payments |                                  |   Lead Form    | Categories:<br />Keine<br />0 – 35.000<br />35.000 - 60.000<br />60.000 - 100.000<br />100.000 - 200.000<br />200.000 - 400.000<br />400.000 - 600.000<br />600.000 - 1 Mio.<br />1 Mio. – 2 Mio.<br />2 Mio. – 5 Mio.<br />Mehr als 5 Mio. |    annual_income     |
| Products of Interest             |   enum    | Enumerated categories indicating SumUp products the owner is interested in                            |                                  |   Lead Form    | Categories:<br />Keine<br />Alle<br />Kartenterminals<br />Kassensystem<br />Geshäftskonto<br />Andere                                                                                                                                      | products_of_interest |
| Email Domain                     |   text    | Domain of the email address provided by the lead form                                                 |                                  | Pre-processing |                                                                                                                                                                                                                                             |        domain        |

## Links to Data Sources:

Lead form: https://www.sumup.com/de-de/kontaktieren-vertriebsteam/ \
Google Places API: https://developers.google.com/maps/documentation/places/web-service/overview \
OpenAI API: https://platform.openai.com/docs/overview \
Meta API: https://developers.facebook.com/docs/graph-api/overview
