import pandas as pd
from DKbetscraper import DraftKingsScraper
from data_structure import PlayerPerformanceAnalyzer
from LastNightStats import BasketballStatsProcessor
from model import StatTypeModel
from sendemail import send_email_with_attachment
from neuralnet import StatTypeNNModel

model = StatTypeNNModel()


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


def make_predictions(old_data, todays_data):
    model.train_model(old_data, target_column="Covered")
    model.predict_model(todays_data)


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

    yesterdays_data = load_DKFrame("DataFrames/testoutput.xlsx")
    update_data(yesterdays_data)
    updated_yest_data = load_DKFrame("DataFrames/FinishedOutput.xlsx")
    # model = update_model(updated_yest_data, retrain=True)

    # Step 1: Fetch Daily Data
    daily_data = fetch_daily_data()
    # daily_data = load_DKFrame("Dataframes/DKFrame.xlsx")
    # Step 2: Process Data
    process_data(daily_data)
    todaysdata = load_DKFrame("DataFrames/testoutput.xlsx")
    make_predictions(updated_yest_data, todaysdata)

    send_email_with_attachment()

    #

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
