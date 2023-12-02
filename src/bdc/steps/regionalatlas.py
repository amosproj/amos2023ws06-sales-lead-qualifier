# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech <f.utech@gmx.net>


import geopandas as gpd
import osmnx
import pandas as pd
from geopandas.tools import sjoin
from pandas import DataFrame
from shapely.geometry import Point, shape
from tqdm import tqdm

from bdc.steps.step import Step
from logger import get_logger

log = get_logger()


class RegionalAtlas(Step):
    name: str = "Regional_Atlas"
    reagionalatlas_feature_keys: dict = {
        "pop_density": "ai0201",
        "pop_development": "ai0202",
        "age_0": "ai0203",
        "age_1": "ai0204",
        "age_2": "ai0205",
        "age_3": "ai0206",
        "age_4": "ai0207",
        "pop_avg_age (Bevölkerung)": "ai0218",
        "per_service_sector": "ai0706",
        "per_trade": "ai0707",
        "employment_rate (Beschäftigt)": "ai0710",
        "unemployment_rate (Arbeitslos)": "ai0801",
        "per_long_term_unemployment": "ai0808",
        "investments_p_employee": "ai1001",
        "gross_salary_p_employee": "ai1002",
        "disp_income_p_inhabitant": "ai1601",
        "tot_income_p_taxpayer": "ai1602",
        "gdp_p_employee": "ai1701",
        "gdp_development": "ai1702",
        "gdp_p_inhabitant": "ai1703",
        "gdp_p_workhours": "ai1704",
        "pop_avg_age (Gesamtbevölkerung)": "ai_z01",
        "unemployment_rate (Erwerbslos)": "ai_z08",
    }

    added_cols: list[str] = reagionalatlas_feature_keys.keys()
    regions_gdfs = gpd.GeoDataFrame()
    empty_result: dict = dict.fromkeys(added_cols)
    # germany_gdf = osmnx.geocode_to_gdf("Germany")

    def __init__(self, force_refresh: bool = False) -> None:
        self._df = None
        self._force_refresh = force_refresh

    def load_data(self) -> None:
        pass

    def verify(self) -> bool:
        return "google_places_formatted_address" in self._df

    def run(self) -> DataFrame:
        tqdm.pandas(desc="Getting social data")

        # Load the data file
        try:
            self.regions_gdfs = gpd.read_file("data/merged_geo.geojson")
        except:
            log.info("File does not exist!")
            return self.empty_result

        # Add the new fields to the df
        self.df[
            [f"{self.name.lower()}_{field}" for field in self.added_cols]
        ] = self.df.progress_apply(
            lambda lead: pd.Series(self.get_data_from_address(lead)), axis=1
        )

        return self.df

    def finish(self) -> None:
        prefix = "regional_atlas"
        matching_columns = [col for col in self.df.columns if col.startswith(prefix)]
        success_rate = 0

        if len(matching_columns) > 0:
            success_rate = (
                1
                - self.df[matching_columns[0]].isna().sum()
                / len(self.df[matching_columns[0]])
            ) * 100
        log.info(
            "Percentage of regional information (germany): {:.2f}%".format(
                round(success_rate, 2)
            )
        )

    def get_data_from_address(self, row):
        # can only get an result if we know the region
        if (
            row["google_places_formatted_address"] is None
            and row["number_area"] is None
        ):
            return self.empty_result

        country = ""

        # the phone number has secondary priority (because it can be a private number), therefore can be overwritten by the google places information
        if row["number_country"] is not None:
            country = row["number_country"]

        if row["google_places_formatted_address"] is not None:
            google_location = str(row["google_places_formatted_address"]).split(",")[
                -2:
            ]
            google_location = [name.strip() for name in google_location]
            country = google_location[-1].lower()

        # the 'regionalatlas' data is specific to germany
        if country not in [
            "deutschland",
            "germany",
            "allemagne",
            "tyskland",
            "germania",
        ]:
            return self.empty_result

        """#Alternative to the if 'if country not in ...'
        if not self.germany_gdf.intersects(row_gdf):
            return self.empty_result"""

        # Get the polygon of the city, to find the corresponding region
        try:
            if row["google_places_formatted_address"] is not None:
                search_gdf = osmnx.geocode_to_gdf(",".join(google_location))
            else:  # at this point we know, that either a google_places_address exists or a number_area
                search_gdf = osmnx.geocode_to_gdf(row["number_area"])
        except:
            log.info("Google location not found!")
            return self.empty_result

        # Adjust the EPSG code from the osmnx search query to the regionalatlas specific code
        # epsg_code 4326 [WGS 84 (used by osmnx)]=> epsg_code_etrs = 25832 [ETRS89 / UTM zone 32N (used by regionalatlas)]
        epsg_code_etrs = 25832
        search_gdf_reprojected = search_gdf.to_crs("EPSG:" + str(epsg_code_etrs))

        # Use the centroid of the city, to check if a region
        search_centroid = search_gdf_reprojected.centroid

        area_key = None

        return_values = {}

        # go through all regions of germany ...
        for idx, region in self.regions_gdfs.iterrows():
            if area_key is not None:
                if region["schluessel"] != area_key:
                    continue
                else:
                    return_values.update(
                        region[self.reagionalatlas_feature_keys.values()].to_dict()
                    )
                    break
            else:
                region_polygon = region["geometry"]
                b_contains = region_polygon.contains(search_centroid).item()

                if b_contains:
                    area_key = region["schluessel"]
                    return_values.update(
                        region[self.reagionalatlas_feature_keys.values()].to_dict()
                    )
                    break

        columns = {}
        for col, value in return_values.items():
            for k, v in self.reagionalatlas_feature_keys.items():
                if col == v:
                    columns[k] = value

        return columns
