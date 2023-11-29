# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech <f.utech@gmx.net>

import geopandas as gpd
import pandas as pd
import regex as re
import os

geojson_directory = './src/data'

# List all GeoJSON files in the directory
geojson_files = [f for f in os.listdir(geojson_directory) if f.endswith('.geojson') and f!='merged_geo.geojson']

# Initialize an empty GeoDataFrame
merged_gdf = gpd.GeoDataFrame()


# Iterate through each GeoJSON file and concatenate to the merged GeoDataFrame
for i,geojson_file in enumerate(geojson_files):

    file_path = os.path.join(geojson_directory, geojson_file)
    gdf = gpd.read_file(file_path)        

    col = next((s for s in gdf.columns if s.startswith('ai')), None)
    print(f'{i+1}/{len(geojson_files)} - file:{geojson_file} col:{col}')
    
    file_name_code = geojson_file.split('--')[1].lower()
    file_name_code = file_name_code.replace('-','_')

    if file_name_code[-4:] != col[-4:]:
        print(f'file: {file_name_code} != {col}')
    if i>0:
        try:
            merged_gdf = merged_gdf.merge(gdf[['schluessel',col]], on='schluessel', how='left', suffixes=(None,None) )  
        except:
            pass 
    else:
        merged_gdf = gdf.copy()

# Save the merged GeoDataFrame to a new GeoJSON file
merged_gdf.to_file( os.path.join(geojson_directory, 'merged_geo.geojson') , driver='GeoJSON')

file = open(os.path.join(geojson_directory, 'merged_geo.geojson.license'), "w")
file.write("SPDX-License-Identifier: DL-DE-BY-2.0\nProvider: Regionalatlas (Statistische Ämter des Bundes und der Länder)\nURI: https://regionalatlas.statistikportal.de/\nSPDX-FileCopyrightText: 2023 Fabian-Paul Utech <f.utech@gmx.net>\n")
file.close( )
