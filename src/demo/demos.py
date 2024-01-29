# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech  <f.utech@gmx.net>
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <Ruchita.nathani@fau.de>
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>


from sklearn.metrics import classification_report

from bdc import DataCollector
from bdc.pipeline import Pipeline
from database import get_database
from demo.console_utils import (
    get_int_input,
    get_multiple_choice,
    get_string_input,
    get_yes_no_input,
)
from demo.pipeline_utils import (
    get_all_available_pipeline_json_configs,
    get_pipeline_additional_steps,
    get_pipeline_config_from_json,
    get_pipeline_initial_steps,
)
from evp import EstimatedValuePredictor
from evp.predictors import MerchantSizeByDPV, Predictors
from logger import get_logger
from preprocessing import Preprocessing

log = get_logger()

# Constants and configurations
LEADS_TRAIN_FILE = "data/leads_train.csv"
LEADS_TEST_FILE = "data/leads_test.csv"
INPUT_FILE_BDC = "../data/sumup_leads_email.csv"
OUTPUT_FILE_BDC = "../data/collected_data.json"


# bdc_demo
def bdc_demo():
    dc = DataCollector()
    try:
        choice = get_int_input("(1) Read CSV\n(2) Dummy API\n", range(1, 3))
        if choice == 1:
            dc.get_data_from_csv(file_path=INPUT_FILE_BDC)
        elif choice == 2:
            dc.get_data_from_api(file_path=OUTPUT_FILE_BDC)
        else:
            print("Invalid choice")
    except ValueError:
        print("Invalid choice")


# evp demo
def evp_demo():
    data = get_database().load_preprocessed_data()

    model_type_choices = [e for e in Predictors]
    print("Which model type do you want to load")
    for i, p in enumerate(Predictors):
        print(f"({i}) : {p.value}")

    choice = get_int_input("", range(0, len(model_type_choices)))
    model_type = model_type_choices[choice]

    model_name = None
    if get_yes_no_input("Load model from file? (y/N)\n"):
        model_name = get_string_input("Provide model file name\n")

    limit_classes = False
    if get_yes_no_input(
        "Use 3 classes ({XS}, {S, M, L}, {XL}) instead of 5 classes ({XS}, {S}, {M}, {L}, {XL})? (y/N)\n"
    ):
        limit_classes = True

    feature_subsets = [
        ["Include all features"],
        [
            "google_places_rating",
            "google_places_user_ratings_total",
            "google_places_confidence",
            "regional_atlas_regional_score",
        ],
    ]
    print("Do you want to train on a subset of features?")

    for i, p in enumerate(feature_subsets):
        print(f"({i}) : {p}")
    feature_choice = get_int_input("", range(0, len(feature_subsets)))
    feature_choice = None if feature_choice == 0 else feature_subsets[feature_choice]

    evp = EstimatedValuePredictor(
        data=data,
        model_type=model_type,
        model_name=model_name,
        limit_classes=limit_classes,
        selected_features=feature_choice,
    )

    while True:
        choice = get_int_input(
            "(1) Train\n(2) Test\n(3) Predict on single lead\n(4) Save model\n(5) Exit\n",
            range(1, 6),
        )
        if choice == 1:
            evp.train()
        elif choice == 2:
            test_evp_model(evp)
        elif choice == 3:
            predict_single_lead(evp)
        elif choice == 4:
            evp.save_model()
        elif choice == 5:
            break
        else:
            print("Invalid choice")


def test_evp_model(evp: EstimatedValuePredictor):
    predictions = evp.predict(evp.X_test)
    if len(predictions) == 1 and predictions[0] == MerchantSizeByDPV.Invalid:
        log.info("Untrained model results in no displayable data")
        return
    true_labels = evp.y_test

    print(classification_report(true_labels, predictions))


def predict_single_lead(evp: EstimatedValuePredictor):
    leads = evp.X_test
    lead_id = get_int_input(
        f"Choose a lead_id in range [0, {len(leads) - 1}]\n", range(len(leads))
    )
    if 0 <= lead_id < len(leads):
        prediction = evp.predict([leads[lead_id]])
        if prediction[0] == MerchantSizeByDPV.Invalid:
            log.info("Untrained model results in no displayable data")
            return
        print(
            f"Lead has predicted value of {prediction} and true value of {evp.y_test[lead_id]}"
        )
    else:
        print("Invalid Choice")


# db_demo
def db_demo():
    amt_leads = get_database().get_cardinality()
    lead_id = get_int_input(
        f"Choose a lead_id in range [1, {amt_leads}]\n", range(1, amt_leads + 1)
    )
    if 1 <= lead_id <= amt_leads:
        print(get_database().get_lead_by_id(lead_id))
    else:
        print("Invalid Choice")


def add_step_if_requested(steps, step_class, step_desc, step_warning_message: str = ""):
    if get_yes_no_input(f"Run {step_desc} {step_warning_message}(y/N)?\n"):
        force = get_yes_no_input("Force execution if data is present? (y/N)\n")
        steps.append(step_class(force_refresh=force))


# pipeline_demo
def pipeline_demo():
    """
    Demonstrates the execution of a pipeline.

    The function prompts the user to select a pipeline configuration or create a custom one.
    It then sets a limit for the number of data points to be processed, if specified.
    Finally, it runs the pipeline with the selected configuration and limit.

    Args:
        None

    Returns:
        None
    """
    continue_with_custom_config = True
    if get_yes_no_input(f"Do you want to list all available pipeline configs? (y/N)\n"):
        # Create the formatted string using list comprehension and join
        all_pipeline_configs = get_all_available_pipeline_json_configs()
        if len(all_pipeline_configs) > 0:
            prompt = "Please enter the index of requested pipeline config:\n"
            choices = all_pipeline_configs + ["Exit"]
            choice = get_multiple_choice(prompt, choices)
            if choice != "Exit":
                steps = get_pipeline_config_from_json(config_name=choice)
                continue_with_custom_config = False
            else:
                print("Exiting...\n")
        else:
            print("No pipeline configs found.\n")

    if continue_with_custom_config:
        print("Continuing with custom pipeline config...\n\n")
        steps = []
        # get default steps and optional steps attrs
        initial_steps_attr = get_pipeline_initial_steps()
        additional_steps_attr = get_pipeline_additional_steps()

        # create step instances from default steps attrs and add them to steps list
        for step_class, desc, warning_message in initial_steps_attr:
            steps.append(step_class(force_refresh=True))

        # add optional steps to steps list if requested
        for step_class, desc, warning_message in additional_steps_attr:
            add_step_if_requested(steps, step_class, desc, warning_message)

    limit = get_int_input("Set limit for data points to be processed (0=No limit)\n")
    limit = limit if limit > 0 else None

    if (
        limit is not None
        and get_database().DF_OUTPUT == "s3://amos--data--events/leads/enriched.csv"
    ):
        if get_yes_no_input(
            f"The output cannot be limited when uploading to {get_database().DF_OUTPUT}.\nThe limit will be removed, and the pipeline will be executed on the full database.\n\nWould you like to continue? (y/n)\n"
        ):
            limit = None
        else:
            return

    steps_info = "\n".join([str(step) for step in steps])
    log.info(
        f"Running Pipeline with steps:\n{steps_info}\ninput_location={get_database().get_input_path()}\noutput_location={get_database().get_output_path()}"
    )

    pipeline = Pipeline(
        steps=steps,
        limit=limit,
    )

    pipeline.run()


def preprocessing_demo():
    if get_yes_no_input("Filter out the API-irrelevant data? (y/n)"):
        filter_bool = True
    else:
        filter_bool = False
    if get_yes_no_input(
        "Run on historical data ? (y/n)\nNote: DATABASE_TYPE should be S3!"
    ):
        historical_bool = True
    else:
        historical_bool = False
    preprocessor = Preprocessing(
        filter_null_data=filter_bool, historical_data=historical_bool
    )
    df = preprocessor.implement_preprocessing_pipeline()
    preprocessor.save_preprocessed_data()
