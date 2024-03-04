from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
from sklearn.metrics import log_loss
from joblib import dump, load

features = [
    "O/U",
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
        # Define preprocessing pipeline
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", SimpleImputer(strategy="mean"), features),
            ],
            remainder="passthrough",  # Keep other features unchanged
        )

        # Define the complete pipeline
        self.model = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    SGDClassifier(loss="log_loss", random_state=42, verbose=1),
                ),
            ]
        )
        print("New model pipeline initialized.")

    def load_existing_data(self):
        """
        Load existing data from an Excel file.
        """
        try:
            return pd.read_excel(self.excel_path)
        except FileNotFoundError:
            print(
                f"No existing data file found at {self.excel_path}. Starting with an empty DataFrame."
            )
            return pd.DataFrame()

    def train_model(self, data, target_column):
        self.excel_path = "DataFrames/old_data.xlsx"
        self.dataframes = data
        self._preprocess_and_combine_data(target_column)
        self.save_model()

    def _preprocess_and_combine_data(self, target_column):
        combined_df = pd.DataFrame()
        old_data = self.load_existing_data()
        for stat_type, df in self.dataframes.items():
            df_filtered = df[
                (df[target_column] != "NAN") & df["O/U"].notna()
            ].copy()  # Ensure this line correctly filters out unwanted rows
            combined_df = pd.concat(
                [combined_df, df_filtered[features + [target_column]]],
                ignore_index=True,
            )
        old_data = pd.concat([old_data, combined_df], ignore_index=True)
        old_data.to_excel("DataFrames/old_data.xlsx")

        X = old_data[features]
        y = old_data[target_column].astype(
            int
        )  # Ensure y is of integer type for classification

        self.model.fit(X, y)

    def _evaluate_model(self, X_test, y_test):
        # For classification, using log loss as evaluation metric
        predictions_proba = self.model.predict_proba(X_test)
        loss = log_loss(y_test, predictions_proba)
        print(f"Log Loss: {loss}")

    def save_model(self, model_filename="Models/model1.joblib"):
        dump(self.model, model_filename)
        print(f"Model saved to {model_filename}")

    def predict_and_proba(self, X):
        # Ensure the pipeline is used for predictions to include preprocessing steps
        # This method assumes the last step of the pipeline is the classifier
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)[
            :, 1
        ]  # Probability for class '1' (over)
        return predictions, probabilities

    def predict_model(self, model_path, todays_data):
        # Ensure model is loaded; this might be redundant if you ensure the model is loaded or initialized in __init__
        model = (
            self.model if hasattr(self, "model") and self.model else load(model_path)
        )

        with pd.ExcelWriter("DataFrames/Predictions_for_today.xlsx") as writer:
            for stat_type, df in todays_data.items():
                # Directly use the pipeline to preprocess (impute and scale) and predict
                X_today = df[features]

                # Using the predict_and_proba method to get predictions and probabilities
                predictions, probabilities = self.predict_and_proba(X_today)

                # Assign predictions and their corresponding probabilities
                df["Prediction"] = predictions
                df["Confidence"] = probabilities

                # Prepare the DataFrame to be saved in Excel format
                df_to_save = df[
                    ["Teams", "Player Name", "O/U", "Prediction", "Confidence"]
                ]
                df_to_save.to_excel(writer, sheet_name=stat_type, index=False)

        print("Predictions saved in 'Predictions_for_today.xlsx'")
