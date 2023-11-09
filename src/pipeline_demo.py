# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech  <f.utech@gmx.net>
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <Ruchita.nathani@fau.de>
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>


from bdc.pipeline import Pipeline
from bdc.steps import EnrichCustomDomains
from bdc.steps.google_places import GooglePlaces

if __name__ == "__main__":
    enrich_domain_step = EnrichCustomDomains()
    google_places_step = GooglePlaces()
    # scrape_address_step = ScrapeAddress()

    pipeline = Pipeline(
        steps=[enrich_domain_step, google_places_step],
        input_location="src/data/sumup_leads_email.csv",
        output_location="src/data/leads_enriched.csv",
        limit=25,
    )
    pipeline.run()
