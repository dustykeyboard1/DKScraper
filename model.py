import pandas as pd
from sklearn.linear_model import SGDRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from math import sqrt
from joblib import dump, load
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

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
    def __init__(
        self,
        load_existing=True,
        model_path="Models/model1.joblib",
        scaler_path="Models/scaler1.joblib",
        imputer_path="Models/imputer1.joblib",
    ):
        """
        Initialize the model. Optionally load an existing model, scaler, and imputer.
        """
        if load_existing:
            self.model = load(model_path)
            self.scaler = load(scaler_path)
            self.imputer = load(imputer_path)
            print(
                f"Model, scaler, and imputer loaded from {model_path}, {scaler_path}, and {imputer_path}, respectively."
            )
        else:
            self.model = SGDRegressor(verbose=1, random_state=42)
            self.scaler = StandardScaler()
            self.imputer = SimpleImputer(strategy="mean")
            print("New model, scaler, and imputer initialized.")

    def train_model(self, dataframes, incremental=True):
        """
        Train or incrementally train the model on the provided dataframes.
        """
        self.dataframes = dataframes
        self._preprocess_and_combine_data(incremental=incremental)

    def _preprocess_and_combine_data(self, incremental):
        """
        Preprocess each dataframe by selecting the relevant features and target,
        and then combine them into a single dataframe.
        """
        combined_df = pd.DataFrame()

        for stat_type, df in self.dataframes.items():
            df_filtered = df[df[f"Last Night {stat_type}"] != 0].copy()
            df_filtered.loc[:, "Target"] = df_filtered[f"Last Night {stat_type}"]
            combined_df = pd.concat(
                [combined_df, df_filtered[features + ["Target"]]], ignore_index=True
            )

        # Handle missing values and scale features
        if not incremental:
            # Fit and transform for initial training
            X = combined_df[features]
            self.imputer.fit(X)
            X_imputed = self.imputer.transform(X)
            self.scaler.fit(X_imputed)
            X_scaled = self.scaler.transform(X_imputed)
        else:
            # Only transform for incremental training
            X_imputed = self.imputer.transform(combined_df[features])
            X_scaled = self.scaler.transform(X_imputed)

        y = combined_df["Target"]
        self._train_model(X_scaled, y, incremental)

    def _train_model(self, X, y, incremental):
        """
        Train or incrementally train the model using the processed data.
        """
        if incremental:
            self.model.partial_fit(X, y)
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            self.model.fit(X_train, y_train)
            # Evaluate the model with the test set
            self._evaluate_model(X_test, y_test)

    def _evaluate_model(self, X_test, y_test):
        predictions = self.model.predict(X_test)
        rmse = sqrt(mean_squared_error(y_test, predictions))
        print(f"Root Mean Squared Error: {rmse}")

    def save_model(
        self,
        model_filename="Models/model1.joblib",
        scaler_filename="Models/scaler1.joblib",
        imputer_filename="Models/imputer1.joblib",
    ):
        dump(self.model, model_filename)
        dump(self.scaler, scaler_filename)
        dump(self.imputer, imputer_filename)
        print(f"Model saved to {model_filename}")
        print(f"Scaler saved to {scaler_filename}")
        print(f"Imputer saved to {imputer_filename}")

    # Adjust the predict_model method to include imputation and scaling
    def predict_model(self, model_path, todays_data):
        # Load the model, scaler, and imputer if not already loaded
        model = self.model if self.model else load(model_path)
        # Assume the scaler and imputer are loaded in __init__ if using an existing model

        with pd.ExcelWriter("DataFrames/Predictions_for_today.xlsx") as writer:
            for stat_type, df in todays_data.items():
                # Preprocess features: Impute NaNs and scale
                X_today = df[features]
                X_today_imputed = self.imputer.transform(X_today)
                X_today_scaled = self.scaler.transform(X_today_imputed)

                # Make predictions with preprocessed data
                df["Prediction"] = model.predict(X_today_scaled)

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
                df_to_save.to_excel(writer, sheet_name=stat_type, index=False)

        print("Predictions saved in 'Predictions_for_today.xlsx'")
