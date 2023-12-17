# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech <f.utech@gmx.net>


import geopandas as gpd
import osmnx
import pandas as pd
from geopandas.tools import sjoin
from pandas import DataFrame
from tqdm import tqdm

from bdc.steps.step import Step, StepError
from logger import get_logger

log = get_logger()


class RegionalAtlas(Step):
    """
    The RegionalAtlas step will query the RegionalAtlas database for location based geographic and demographic
        information, based on the address that was found for a business (currently through Google API) or the
        area provided by the phonenumber (preprocess_phonenumbers.py).

    Attributes:
        name: Name of this step, used for logging
        reagionalatlas_feature_keys: Dictionary to translate between the keys in the merged.geojson and the used column names in the df
        df_fields: the keys of the merged.geojson
        added_cols: List of fields that will be added to the main dataframe by executing this step
        required_cols: List of fields that are required in the input dataframe before performing this step

        regions_gdfs: dataframe that includes all keys/values from the merged.geojson
        empty_result: empty result that will be used in case there are problems with the data
        epsg_code_etrs: 25832 is the standard used by RegionAtlas
    """

    name: str = "Regional_Atlas"
    reagionalatlas_feature_keys: dict = {
        "pop_density": "ai0201",
        "pop_development": "ai0202",
        "age_0": "ai0203",
        "age_1": "ai0204",
        "age_2": "ai0205",
        "age_3": "ai0206",
        "age_4": "ai0207",
        "pop_avg_age": "ai0218",
        "per_service_sector": "ai0706",
        "per_trade": "ai0707",
        "employment_rate": "ai0710",
        "unemployment_rate": "ai0801",
        "per_long_term_unemployment": "ai0808",
        "investments_p_employee": "ai1001",
        "gross_salary_p_employee": "ai1002",
        "disp_income_p_inhabitant": "ai1601",
        "tot_income_p_taxpayer": "ai1602",
        "gdp_p_employee": "ai1701",
        "gdp_development": "ai1702",
        "gdp_p_inhabitant": "ai1703",
        "gdp_p_workhours": "ai1704",
        "pop_avg_age_zensus": "ai_z01",
        "unemployment_rate": "ai_z08",
    }

    df_fields: list[str] = reagionalatlas_feature_keys.values()

    # Weirdly the expression [f"{name}_{field}" for field in df_fields] gives an error as name is not in the scope of the iterator
    added_cols = [
        name + field
        for (name, field) in zip(
            [f"{name.lower()}_"] * (len(df_fields)),
            ([f"{field}" for field in reagionalatlas_feature_keys.keys()]),
        )
    ] + [f"{name.lower()}_regional_score"]

    required_cols = ["google_places_formatted_address"]

    regions_gdfs = gpd.GeoDataFrame()
    empty_result: dict = dict.fromkeys(reagionalatlas_feature_keys.values())

    # Adjust the EPSG code from the osmnx search query to the regionalatlas specific code
    # epsg_code 4326 [WGS 84 (used by osmnx)]=> epsg_code_etrs = 25832 [ETRS89 / UTM zone 32N (used by regionalatlas)]
    epsg_code_etrs = 25832

    def load_data(self) -> None:
        pass

    def verify(self) -> bool:
        # Load the data file
        try:
            self.regions_gdfs = gpd.read_file("data/merged_geo.geojson")
        except:
            raise StepError(
                "The path for the geojson for regional information (Regionalatlas) is not valid!"
            )
        return super().verify()

    def run(self) -> DataFrame:
        tqdm.pandas(desc="Getting social data")

        # Add the new fields to the df
        self.df[self.added_cols[:-1]] = self.df.progress_apply(
            lambda lead: pd.Series(self.get_data_from_address(lead)), axis=1
        )

        tqdm.pandas(desc="Computing Regional Score")
        self.df[f"{self.name.lower()}_regional_score"] = self.df.progress_apply(
            lambda lead: pd.Series(self.calculate_regional_score(lead)), axis=1
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
        """
        Retrieve the regional features for every lead. Every column of reagionalatlas_feature_keys is added.

        Based on the google places address or the phonenumber area. Checks if the centroid of the
        searched city is in a RegionalAtlas region.

        Possible extensions could include:
        - More RegionalAtlas features

        :param row: Lead for which to retrieve the features

        :return: dict - The retrieved features if the necessary fields are present for the lead. Empty dictionary otherwise.
        """

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

        search_gdf_reprojected = search_gdf.to_crs("EPSG:" + str(self.epsg_code_etrs))

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

        return return_values

    def calculate_regional_score(self, lead) -> float | None:
        """
        Calculate a regional score for a lead based on information from the RegionalAtlas API.

        This function uses population density, employment rate, and average income to compute
        the buying power of potential customers in the area in millions of euro.

        The score is computed as:
            (population density * employment rate * average income) / 1,000,000

        Possible extensions could include:
        - Population age groups

        :param lead: Lead for which to compute the score

        :return: float | None - The computed score if the necessary fields are present for the lead. None otherwise.
        """

        if (
            lead[f"{self.name.lower()}_pop_density"] is None
            or lead[f"{self.name.lower()}_employment_rate"] is None
            or lead[f"{self.name.lower()}_disp_income_p_inhabitant"] is None
        ):
            return None

        regional_score = (
            lead[f"{self.name.lower()}_pop_density"]
            * lead[f"{self.name.lower()}_employment_rate"]
            * lead[f"{self.name.lower()}_disp_income_p_inhabitant"]
        ) / 1000000

        return regional_score
