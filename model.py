import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from math import sqrt
from joblib import dump, load


features = [
    "Combined Average Last 10",
    "Combined Average Last 5",
    "Combined Average Season",
    "Game Average Minutes",
    "Last 10 Games Average Minutes",
    "Last 10 Games Over Covered %",
    "Last 10 Games Win Percentage",
    "Last 15 Opponent Stats vs Position",
    "Last 5 Games Over Covered %",
    "Last 5 Games Win Percentage",
    "Last 5 games average minutes",
    "Last 7 Opponent Stats vs Position",
    "Opponents Last 10 Games Win Percentage",
    "Opponents Last 5 Games Win Percentage",
    "Opponents Team Win Percentage",
    "Season Opponent Stats vs Position",
    "Season Over Covered %",
    "Team Win Percentage",
]


class StatTypeModel:
    def __init__(self):
        """
        Initialize the model with a dictionary of dataframes.
        Each key in the dictionary is a stat type, and the value is the dataframe for that stat type.
        """
        self.model = None

    def train_model(self, dataframes):
        self.dataframes = dataframes
        self._preprocess_and_combine_data()
        self._train_model()

    def _preprocess_and_combine_data(self):
        """
        Preprocess each dataframe by selecting the relevant features and target,
        and then combine them into a single dataframe.
        """
        combined_df = pd.DataFrame()

        for stat_type, df in self.dataframes.items():
            # Remove rows where Player Name is N/A
            df_filtered = df[df["Player Name"] != "N/A"].copy()
            # Safely add the "Target" column without triggering the warning
            df_filtered.loc[:, "Target"] = df_filtered[f"Last Night {stat_type}"]
            combined_df = pd.concat(
                [combined_df, df_filtered[features + ["Target"]]], ignore_index=True
            )

        self.combined_df = combined_df

    def _train_model(self):
        """
        Train a Random Forest Regressor using the combined dataframe.
        """
        X = self.combined_df.drop("Target", axis=1)
        y = self.combined_df["Target"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Set verbose to 2 for more detailed output
        self.model = RandomForestRegressor(n_estimators=100, random_state=42, verbose=2)
        self.model.fit(X_train, y_train)

        # Evaluate the model
        predictions = self.model.predict(X_test)
        rmse = sqrt(mean_squared_error(y_test, predictions))
        print(f"Root Mean Squared Error: {rmse}")

    def save_model(self, filename="Models/model1.joblib"):
        """
        Save the trained model to a file.
        """
        dump(self.model, filename)
        print(f"Model saved to {filename}")

    def predict_model(self, model_path, todays_data):
        model = load(model_path)
        with pd.ExcelWriter("DataFrames/Predictions_for_today.xlsx") as writer:
            for stat_type, df in todays_data.items():
                # Assuming features are defined and include the necessary columns for prediction
                X_today = df[
                    features
                ]  # Ensure this doesn't include 'O/U' since it's not a feature but a label

                # Make predictions
                df["Prediction"] = model.predict(X_today)

                # Calculate prediction - O/U and its absolute value
                df["Pred_minus_OU"] = df["Prediction"] - df["O/U"]
                df["Abs_Pred_minus_OU"] = abs(df["Pred_minus_OU"])

                # Select the relevant columns to save, including the new ones
                df_to_save = df[
                    [
                        "Teams",
                        "Player Name",
                        "O/U",
                        "Prediction",
                        "Pred_minus_OU",
                        "Abs_Pred_minus_OU",
                    ]
                ]

                # Save to the respective sheet in the Excel file
                df_to_save.to_excel(writer, sheet_name=stat_type, index=False)

        print("Predictions saved in 'Predictions_for_today.xlsx'")
