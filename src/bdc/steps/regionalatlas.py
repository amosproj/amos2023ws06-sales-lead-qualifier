# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech <f.utech@gmx.net>


import geopandas as gpd
import osmnx
import pandas as pd
from pandas import DataFrame
from shapely.geometry import Point
from tqdm import tqdm

from bdc.steps.step import Step
from logger import get_logger
from shapely.geometry import shape
from geopandas.tools import sjoin

log = get_logger()


class RegionalAtlas(Step):
    name: str = "Regional-Atlas"
    reagionalatlas_feature_keys = {"gdp": "ai1701"}
    df_fields: list[str] = reagionalatlas_feature_keys.keys()
    #germany_gdf = osmnx.geocode_to_gdf("Germany")

    def __init__(self, force_refresh: bool = False) -> None:
        self._df = None
        self._force_refresh = force_refresh

    def load_data(self) -> None:
        pass

    def verify(self) -> bool:
        return "google_places_formatted_address" in self._df

    def run(self) -> DataFrame:
        tqdm.pandas(desc="Getting info from geo data")
        self.df[
            [f"{self.name.lower()}_{field}" for field in self.df_fields]
        ] = self.df.progress_apply(
            lambda lead: self.get_data_from_address(lead), axis=1
        )
        return self.df

    def finish(self) -> None:
        log.info("RegionalAtlas: I am done")

    def get_data_from_address(self, row):
        if row["google_places_formatted_address"] is None:
            return pd.Series([None])

        google_location = str(row["google_places_formatted_address"]).split(",")[-2:]
        google_location = [name.strip() for name in google_location]

        # CHECK THE PHONENUMBER AS 2nd CRITERIUM FOR COUNTRY / CITY

        country = google_location[-1].lower()

        # the 'regionalatlas' data is specific to germany
        if country not in ['deutschland','germany','allemagne','tyskland','germania']:
            return pd.Series([None])
        
        # Alternative to the if 'if country not in ...'
        # if not self.germany_gdf.intersects(row_gdf):
        #     return pd.Series([None])

        # Get the polygon of the city, to find the corresponding region
        try:
            search_gdf = osmnx.geocode_to_gdf(",".join(google_location))            
        except:
            log.info('Google location not found!')
            return pd.Series([None])
        
        # Load the data file
        try:
            regions_gdfs = {"gdp": gpd.read_file("data/gdp.geojson")}
        except:            
            log.info("File does not exist!")
            return pd.Series([None])
                
        # WGS 84 (used by osmnx)
        epsg_code_ll = 4326

        #ETRS89 / UTM zone 32N (used by regionalatlas)
        epsg_code_etrs = 25832

        search_gdf.crs = {"init": "epsg:{}".format(epsg_code_ll)}
        search_gdf_reprojected = search_gdf.to_crs(epsg_code_etrs)      

        area_key = None

        return_values = []
        # For every feature we want to add ...
        # AS A PREPROCESS STEP. PUT ALL GEOJSON TOGETHER BY LEFT JOINING THEM ON THE BASE AND THEN JUST USE THIS FILE (NO NEED TO LOOP THROUGH ALL COLUMNS)
        # CREATE FUNCTION JOIN FOR GEOJSON (geojson,[list_geojson],key=[...,...]) [create as standard keys the ones we use]

        for col in self.df_fields:
            regions_gdf = regions_gdfs[col]

            # go through all regions of germany ...
            for idx, region in regions_gdf.iterrows():

                if area_key is not None:
                    if region["schluessel"] != area_key:
                        continue
                    else:
                        return_values.append(
                            region[self.reagionalatlas_feature_keys[col]]
                        )
                        break
                else:                    

                    #search_polygon = search_gdf_reprojected["geometry"].item()
                    #b_intersect = search_polygon.intersects(region["geometry"])

                    # Use the centroid of the city, to check if a region 
                    search_centroid = search_gdf_reprojected.centroid                    
                    region_polygon = region["geometry"]
                    b_contains = region_polygon.contains(search_centroid).item()

                    if b_contains:
                        area_key = region["schluessel"]
                        return_values.append(
                            region[self.reagionalatlas_feature_keys[col]]
                        )
                        break


        return pd.Series(return_values)
