import random
from bdc import DataCollector
from evp import EstimatedValuePredictor
from database import get_database

if __name__ == "__main__":
    dc = DataCollector()
    dc.get_data_from_csv()
    print("Successfully Get Data From the CSV File")
    dc.get_data_from_api()
    print("Successfully Get Data From the API and stored in JSOn file at 'src/data/collected_data.json'")
    
    amt_leads = get_database().get_cardinality()
    lead_id = random.randint(0, amt_leads - 1)
    lead = get_database().get_lead_by_id(lead_id)
    
    evp = EstimatedValuePredictor()
    lead_value = evp.estimate_value(lead_id)
    print(
        f"""
        Dummy prediction for lead#{lead.lead_id}:

        Lead:
        {lead}

        This lead has a predicted probability of {lead_value.customer_probability:.2f} to become a customer.
        This lead has a predicted life time value of {lead_value.life_time_value:.2f}.

        This results in a total lead value of {lead_value.get_lead_value():.2f}.
    """
    )
    