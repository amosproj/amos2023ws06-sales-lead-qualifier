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

log = get_logger()


class RegionalAtlas(Step):
    name: str = "Regional-Atlas"
    added_cols: list[str] = ["gdp"]
    reagionalatlas_feature_keys = {"gdp": "ai1701"}
    germany_gdf = osmnx.geocode_to_gdf("Germany")

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

        row_gdf = osmnx.geocode_to_gdf(",".join(google_location))

        # if not self.germany_gdf.contains(row_gdf):
        #     return pd.Series([None])

        all_gdfs = {"gdp": gpd.read_file("data/gdp.geojson")}

        area_key = None

        return_values = []
        for col in self.added_cols:
            curr_gdf = all_gdfs[col]
            for idx, feature in curr_gdf.iterrows():
                if area_key is not None:
                    if feature["schluessel"] != area_key:
                        continue
                    else:
                        return_values.append(
                            feature[self.reagionalatlas_feature_keys[col]]
                        )
                        break
                else:
                    # coordinates = feature["coordinates"]
                    # geometry = [Point(coodinate[0], coodinate[1]) for coodinate in coordinates]
                    # gdf = gpd.GeoDataFrame(geometry=[feature["geometry"]])
                    gdf = osmnx.geocode_to_gdf(feature["gen"])
                    intersection = gpd.sjoin(gdf, row_gdf, how="inner", op="intersects")
                    if not intersection.empty:
                        # if gdf.contains(row_gdf):
                        return_values.append(
                            feature[self.reagionalatlas_feature_keys[col]]
                        )
                        area_key = feature["schluessel"]
                        break

        return pd.Series(return_values)
