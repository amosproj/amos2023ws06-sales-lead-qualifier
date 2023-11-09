
from bdc.steps import EnrichCustomDomains
from bdc.steps.google_places import GooglePlacesStep
from bdc.pipeline import Pipeline

if __name__ == "__main__":
    enrich_domain_step = EnrichCustomDomains()
    google_places_step = GooglePlacesStep()
    # scrape_address_step = ScrapeAddress()


    pipeline = Pipeline(steps=[enrich_domain_step , google_places_step], input_location="./data/sumup_leads_email.csv", output_location="./data/leads_enriched.csv", limit=25)
    pipeline.run()