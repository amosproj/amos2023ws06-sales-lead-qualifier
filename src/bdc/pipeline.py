# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>

from bdc.steps import EnrichCustomDomains
from bdc.steps.google_places import GooglePlacesStep


class Pipeline:
    def __init__(self, steps):
        self.steps = steps

    def run(self):
        # helper to pass the dataframe and/or input location from previous step to next step
        next_df = None
        next_input_location = None
        for step in self.steps:
            # load dataframe and/or input location for this step
            if step.df is None:
                step.df = next_df
            if step.input_location is None:
                step.input_location = next_input_location

            step.load_data()
            if step.verify():
                step.run()

            # save dataframe and/or output location as input for the next step
            next_df = step.df
            next_input_location = step.output_location

            # cleanup
            step.finish()

        print(f"[PIPELINE] - Finished running {len(self.steps)} steps!")
        print(self.steps[-1].df.head())

        self.steps[-1].df.to_csv("../data/leads_enriched.csv")


if __name__ == "__main__":
    enrich_domain_step = EnrichCustomDomains()
    enrich_domain_step.input_location = "../data/sumup_leads_email.csv"

    # scrape_address_step = ScrapeAddress()

    google_places_step = GooglePlacesStep()

    pipeline = Pipeline([enrich_domain_step, google_places_step])
    pipeline.run()