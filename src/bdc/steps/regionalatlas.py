# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech <f.utech@gmx.net>


import geopandas as gpd
import osmnx
import pandas as pd
from pandas import DataFrame
from tqdm import tqdm

from bdc.steps.step import Step
from logger import get_logger

log = get_logger()


class RegionalAtlas(Step):
    """
    The RegionalAtlas step will query the RegionalAtlas database for location based geographic and demographic
        information, based on the address that was found for a business (currently through Google API).

    Attributes:
        name: Name of this step, used for logging
        added_cols: List of fields that will be added to the main dataframe by executing this step
        required_cols: List of fields that are required to be existent in the input dataframe before performing this
            step
    """

    name: str = "Regional_Atlas"
    reagionalatlas_feature_keys = {
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

    df_fields: list[str] = reagionalatlas_feature_keys.values()

    # Weirdly the expression [f"{name}_{field}" for field in df_fields] gives an error as name is not in the scope of the iterator
    added_cols = [
        name + field
        for (name, field) in zip(
            [f"{name.lower()}_"] * (len(df_fields)),
            ([f"{field}" for field in reagionalatlas_feature_keys.keys()]),
        )
    ]

    required_cols = ["google_places_formatted_address"]
    # germany_gdf = osmnx.geocode_to_gdf("Germany")

    def load_data(self) -> None:
        pass

    def verify(self) -> bool:
        return super().verify()

    def run(self) -> DataFrame:
        tqdm.pandas(desc="Getting social data")
        self.df[
            [f"{self.name.lower()}_{field}" for field in self.df_fields]
        ] = self.df.progress_apply(
            lambda lead: pd.Series(self.get_data_from_address(lead)), axis=1
        )

        self.df = self.df.rename(
            columns={
                f"{self.name.lower()}_{v.lower()}": f"{self.name.lower()}_{k.lower()}"
                for k, v in self.reagionalatlas_feature_keys.items()
            }
        )
        return self.df

    def finish(self) -> None:
        success_rate = (
            1
            - self.df["regional_atlas_pop_density"].isna().sum()
            / len(self.df["regional_atlas_pop_density"])
        ) * 100
        log.info(
            "Percentage of regional information (germany): {:.2f}%".format(
                round(success_rate, 2)
            )
        )

    def get_data_from_address(self, row):
        empty_result = dict.fromkeys(self.reagionalatlas_feature_keys.values())

        if row["google_places_formatted_address"] is None:
            return empty_result

        google_location = str(row["google_places_formatted_address"]).split(",")[-2:]
        google_location = [name.strip() for name in google_location]

        #!!!!! CHECK THE PHONENUMBER AS 2nd CRITERIUM FOR COUNTRY / CITY

        country = google_location[-1].lower()

        # the 'regionalatlas' data is specific to germany
        if country not in [
            "deutschland",
            "germany",
            "allemagne",
            "tyskland",
            "germania",
        ]:
            return empty_result

        # Alternative to the if 'if country not in ...'
        # if not self.germany_gdf.intersects(row_gdf):
        #     return empty_result

        # Get the polygon of the city, to find the corresponding region
        try:
            search_gdf = osmnx.geocode_to_gdf(",".join(google_location))
        except:
            log.info("Google location not found!")
            return empty_result

        # Load the data file
        #!!!!! INTO THE RUN PART
        try:
            regions_gdfs = gpd.read_file(
                "data/merged_geo.geojson"
            )  # {"gdp": gpd.read_file("data/merged_geo.geojson")}
        except:
            log.info("File does not exist!")
            return empty_result

        # WGS 84 (used by osmnx)
        epsg_code_ll = 4326

        # ETRS89 / UTM zone 32N (used by regionalatlas)
        epsg_code_etrs = 25832

        search_gdf.crs = {"init": "epsg:{}".format(epsg_code_ll)}
        search_gdf_reprojected = search_gdf.to_crs(epsg_code_etrs)

        # Use the centroid of the city, to check if a region
        search_centroid = search_gdf_reprojected.centroid

        area_key = None

        return_values = {}

        # go through all regions of germany ...
        for idx, region in regions_gdfs.iterrows():
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

        return return_values
