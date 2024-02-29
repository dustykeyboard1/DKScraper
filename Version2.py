import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib
from DKbetscraper import DraftKingsScraper
from data_structure import PlayerPerformanceAnalyzer
from LastNightStats import BasketballStatsProcessor
from model import StatTypeModel


def fetch_daily_data():
    """
    Scrape daily NBA player prop odds, player statistics, and team defensive ratings.
    """
    DKS = DraftKingsScraper()
    odds_data = DKS.scrape_odds()
    odds_info = DKS.create_data_table(odds_data)
    return odds_info


def process_data(odds_df):
    """
    Process scraped data into a structured format for analysis.
    """
    PPA = PlayerPerformanceAnalyzer(odds_df)
    # PPA.write_dataframe(odds_df, "Dataframes/DKFrame.xlsx")
    # PPA.write_dataframe()
    PPA.fetch_player_yearly_data()
    PPA.enrich_with_coverage()
    PPA.write_dataframe()
    # return PPA


def generate_predictions(model, data):
    """
    Use a pre-trained model to generate predictions for the current day's games.
    """
    # Implement prediction logic here
    pass


def evaluate_predictions(predictions, actual_outcomes):
    """
    Compare predictions with actual game outcomes to assess performance.
    """
    # Implement evaluation logic here
    pass


def update_model(data, targets=None):
    model_trainer = StatTypeModel()
    model_trainer.train_model(data)
    model_trainer.save_model()

    # Implement model updating logic here
    return model_trainer


def make_predictions(model_object, model_path, todays_data):
    model_object.predict_model(model_path, todays_data)


def save_predictions(predictions):
    """
    Save predictions to a file or database for later comparison.
    """
    # Implement save logic here
    pass


def update_data(dict_to_add):
    updater = BasketballStatsProcessor(dict_to_add)
    updater.update_data_frames()


def load_DKFrame(path):
    excel_path = path
    return pd.read_excel(path, sheet_name=None)


def main():
    """
    Main function to orchestrate the daily data collection, prediction, and adjustment process.
    """

    # yesterdays_data = load_DKFrame("DataFrames/testoutput.xlsx")
    # update_data(yesterdays_data)
    updated_yest_data = load_DKFrame("DataFrames/FinishedOutput.xlsx")
    model = update_model(updated_yest_data)

    # Step 1: Fetch Daily Data
    # daily_data = fetch_daily_data()
    # daily_data = load_DKFrame("Dataframes/DKFrame.xlsx")
    # Step 2: Process Data
    # process_data(daily_data)
    # yesterdays_data = load_DKFrame("DataFrames/testoutput.xlsx")

    # updated_stats = update_data(processed_data)
    # updated_stats = load_DKFrame("DataFrames/FinishedOutput.xlsx")
    # model = update_model(updated_stats)

    # model = StatTypeModel()

    processed_data = load_DKFrame("DataFrames/testoutput.xlsx")
    make_predictions(model, "Models/model1.joblib", processed_data)

    # # Step 3: Load Existing Model or Initialize New One
    # try:
    #     model = joblib.load("model.pkl")
    # except FileNotFoundError:
    #     model = RandomForestRegressor()

    # # Step 4: Generate Predictions
    # predictions = generate_predictions(model, processed_data)

    # # Step 5: Save Predictions
    # save_predictions(predictions)

    # # Step 6: (Next Day) Evaluate Predictions Against Actual Outcomes
    # actual_outcomes = "Fetch actual outcomes"  # Placeholder
    # evaluate_predictions(predictions, actual_outcomes)

    # # Step 7: Update Model Based on Evaluation
    # update_model(processed_data, actual_outcomes)

    # # Save updated model
    # joblib.dump(model, "model.pkl")


if __name__ == "__main__":
    main()
