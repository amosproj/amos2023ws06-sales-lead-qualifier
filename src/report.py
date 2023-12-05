# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech <f.utech@gmx.net>
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>

import argparse
import os

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

standard_group_format = {
    # 1 pdf per lead (1 row in .csv)
    "Contact": ["Last Name", "First Name", "Company / Account", "Phone", "Email"],
    "Reviews": [
        "google_places_user_ratings_total",
        "google_places_rating",
        "google_places_price_level",
        "reviews_sentiment_score",
    ],
    #'Region':[] starts with regional_atlas
    # Regarding columns names if there are more than one '_' take the split after the second _
}


def process_lead(lead):
    # Input search string (either specific leads or a whole file)
    # Output: pd.series of a lead from leads_enriched.csv
    try:
        df = pd.read_csv("src/data/leads_enriched.csv", delimiter=",")
    except FileNotFoundError:
        raise FileNotFoundError("File not found.")
    if os.path.exists(
        os.path.dirname(lead)
    ):  # If a path was specified (by default the dummy dataset)
        df = pd.read_csv("src/data/dummy_leads_email.csv", delimiter=",")
        return df
    elif isinstance(lead, list):  # A specified group of leads
        rows = df[df["Company / Account"] in lead]
        return rows

    elif isinstance(lead, str):  # One specified lead
        row = df[df["Company / Account"] == lead]
        return row
    else:
        raise ValueError(
            "Invalid type for 'lead'. It should be a single string, a list of strings, or a file path."
        )


def process_format(fmt):
    if isinstance(fmt, list):  # Transform list to dictionary
        new_fmt = {}

        for value in fmt:
            try:
                key = str(standard_group_format[value])
            except:
                key = "Others"
            if key in new_fmt:
                new_fmt[key] = new_fmt[key].append(str(value))
            else:
                new_fmt[key] = [str(value)]

        return new_fmt
    elif isinstance(fmt, dict):
        return fmt
    elif fmt is None:
        return standard_group_format
    else:
        raise ValueError(
            "Invalid type for 'format'. It should be either a list or a dictionary."
        )


def create_pdf(lead, format):
    """
    Input: lead: pd.series
           format: dict
    Description: Function to create reports.
                 A report consists of tables of grouped features.
    Output: '...'.pdf
    """
    doc = SimpleDocTemplate(
        f"src/data/reports/{lead['Company / Account']}.pdf", pagesize=A4
    )

    # Creating a Paragraph with a large font size and centered alignment
    headline_style = getSampleStyleSheet()["Title"]
    headline_style.fontSize = 32
    headline_style.alignment = 0

    headline_paragraph = Paragraph(lead["Company / Account"], headline_style)

    # List for the 'Flowable' objects
    elements = [headline_paragraph]
    elements.append(Spacer(1, 50))

    # Styles for tables and paragraphs
    styles = getSampleStyleSheet()

    groups = format.keys()

    for group in groups:
        title_paragraph = Paragraph(group, styles["Title"])
        elements.append(title_paragraph)

        col_names = format[group]

        # Header row
        split_col = [col_names[i : i + 4] for i in range(0, len(col_names), 5)]

        # Center the table on the page
        table_style = TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # center the text
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),  # put the text in the middle of the cell
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                (
                    "SPLITBYROWS",
                    (0, 0),
                    (-1, -1),
                    True,
                ),  # Ensure rows are not split between pages
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )

        for group_columns in split_col:
            header_row = group_columns
            data_row = []
            for column in group_columns:
                try:
                    if lead[column] == "nan":
                        data_row.append("")
                    else:
                        data_row.append(str(lead[column]))
                except:
                    data_row.append("")

            table = [header_row, data_row]

            pdf_table = Table(table)
            pdf_table.setStyle(table_style)

            # Add the table to the elements
            elements.append(pdf_table)

            # Add an empty line between tables
            elements.append(Spacer(1, 25))

        """for k,v in tmp_data.items():
            if isinstance(v, dict):

                ul_items=[]
                for key,val in v.items():
                    bolded_text = f'<b>{key}:</b>{val}'
                    ul_items.append(Paragraph(bolded_text,styles['Normal']))

                col_index = list(tmp_data.keys()).index(k)
                table_data[1][col_index] = ul_items"""

        """# Set left alignment for all non-header cells
        for col in range(len(table_data[0])):
            table_style.add('FONTNAME', (col, 0), (col, 0), 'Helvetica-Bold')
            table_style.add('ALIGN', (col, 1), (col, -1), 'LEFT')"""

    # Build the PDF document
    doc.build(elements)


def main():
    parser = argparse.ArgumentParser(description="Process lead and format arguments.")
    parser.add_argument(
        "--lead",
        default="src/data/dummy_leads_email.csv",
        help="Lead argument: a single search-string, a list of strings, or a file path.",
    )
    parser.add_argument(
        "--format", nargs="+", help="Format argument: a list or a dictionary."
    )

    args = parser.parse_args()

    # Process lead argument (result: either specific row(/s) or a table)
    # Choose lead with
    processed_lead = process_lead(args.lead)
    print(processed_lead)

    # Process format argument (result: format that is a dictionary)
    processed_format = process_format(args.format)

    # Generate report for every lead

    for index, lead in processed_lead.iterrows():
        create_pdf(lead, processed_format)


if __name__ == "__main__":
    main()
