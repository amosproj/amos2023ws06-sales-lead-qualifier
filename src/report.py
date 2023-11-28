# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech <f.utech@gmx.net>

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import ParagraphStyle


def create_pdf(output_filename, groups):
    """
    Input: str:output_filename, str[]:groups
           groups: [{'group_title': 'group_title', 'key1': 'value1', 'key2': 'value2','key3 (dictionary)': {'i_key1':'element1','i_key2':'element2'}},...]
    Description: Function is there to create reports. 
                 A report consists of tables of features.                    
    Output: 'output_filename'.pdf
    """
    
    if not isinstance(groups,list):
        groups = [groups]
        
    doc = SimpleDocTemplate(output_filename, pagesize=A4)

    # List for the 'Flowable' objects
    elements = []

    # Styles for tables and paragraphs
    styles = getSampleStyleSheet()

    for data in groups:  
        
        title_paragraph = Paragraph(data['group_title'], styles['Title'])
        elements.append(title_paragraph)  
        
        tmp_data = data.copy()
        del tmp_data['group_title']
        
        # Create a table with the given data        
        table_data = [[key for key in tmp_data.keys()]]  # Header row
        row = [Paragraph(str(value), styles['Normal']) for value in tmp_data.values()]
        table_data.append(row)
        
        for k,v in tmp_data.items():
            if isinstance(v, dict):
                
                ul_items=[]
                for key,val in v.items():  
                    bolded_text = f'<b>{key}:</b>{val}'
                    ul_items.append(Paragraph(bolded_text,styles['Normal']))
                
                col_index = list(tmp_data.keys()).index(k)
                table_data[1][col_index] = ul_items
                
        table = Table(table_data)#[doc.width / len(table_data[0])]*len(table_data[0])
        
        # Center the table on the page
        table_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), # center the text
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), # put the text in the middle of the cell
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('SPLITBYROWS', (0, 0), (-1, -1), True),  # Ensure rows are not split between pages
        ])

        # Set left alignment for all non-header cells
        for col in range(len(table_data[0])):
            table_style.add('FONTNAME', (col, 0), (col, 0), 'Helvetica-Bold')
            table_style.add('ALIGN', (col, 1), (col, -1), 'LEFT')

        table.setStyle(table_style)

        # Add the table to the elements
        elements.append(table)

        # Add an empty line between tables
        elements.append(Spacer(1, 25))

    # Build the PDF document
    doc.build(elements)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ EXAMPLE
output_filename = "report.pdf"

groups = [
    {'group_title': 'group_title', 'key1': 'value1', 'key2': 'value2','key3 (dictionary)': {'i_key1':'element1','i_key2':'element2'}},
    {'group_title': 'Contact', 'contact_date': '17.11.2023', 'contact_name': 'Christopher M. Bauder',
     'contact_email': 'info@darkmatter.berlin', 'contact_number': '+49 30 123123', 'contact_number_valid': False,
     'contact_timezone': 'UTC +1'},
    {'group_title': 'Another Group', 'contact_date': '18.11.2023', 'contact_name': 'Lorem ipsum dolor ipsum dolor sit amet.',
     'contact_email': 'john.doe@example.com', 'contact_number': '+1 123 456789', 'contact_number_valid': True,
     'contact_timezone': {'1':'UTC -5','2':'UTC -5','3':'UTC -5'}}
]

# Call the function to generate the PDF
create_pdf(output_filename, [groups[0],groups[1],groups[2],groups[1],groups[2],groups[1],groups[1],groups[2]])