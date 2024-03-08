from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, InputLayer
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pandas as pd
import numpy as np
from joblib import dump, load

# from tensorflow.keras.wrappers.scikit_learn import KerasClassifier


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

callbacks = [
    EarlyStopping(monitor="val_loss", patience=30, verbose=1),
    ModelCheckpoint(
        filepath="best_model.h5", monitor="val_loss", save_best_only=True, verbose=1
    ),
    ReduceLROnPlateau(
        monitor="val_loss", factor=0.2, patience=15, min_lr=0.001, verbose=1
    ),
]


class StatTypeNNModel:

    def __init__(
        self, excel_path="DataFrames/old_data.xlsx", model_path="Models/nn_model.h5"
    ):
        self.excel_path = excel_path
        self.model_path = model_path
        self.preprocessor = ColumnTransformer(
            transformers=[
                ("num", SimpleImputer(strategy="mean"), features),
            ],
            remainder="passthrough",
        )
        print("Preprocessing pipeline initialized.")

    def build_nn_model(self, input_shape):
        """Define and compile the neural network model."""
        model = Sequential(
            [
                InputLayer(input_shape=(input_shape,)),
                Dense(256, activation="relu"),
                Dense(128, activation="relu"),
                Dense(64, activation="relu"),
                Dense(32, activation="relu"),
                Dense(1, activation="sigmoid"),  # Sigmoid for binary classification
            ]
        )
        model.compile(
            optimizer=Adam(), loss="binary_crossentropy", metrics=["accuracy"]
        )
        return model

    def load_existing_data(self):
        try:
            return pd.read_excel(self.excel_path)
        except FileNotFoundError:
            print(
                f"No existing data file found at {self.excel_path}. Starting with an empty DataFrame."
            )
            return pd.DataFrame()

    def train_model(self, new_data, target_column):
        old_data = self.load_existing_data()
        combined_df = pd.DataFrame()
        for stat_type, df in new_data.items():
            df_filtered = df[df["O/U"].notna()].copy()
            combined_df = pd.concat(
                [combined_df, df_filtered[features + [target_column]]],
                ignore_index=True,
            )
        old_data = pd.concat([old_data, combined_df], ignore_index=True)
        old_data.to_excel(self.excel_path, index=False)

        X = old_data[features]
        y = old_data[target_column].astype(int)

        # Splitting the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Preprocessing: Fit and transform the training data
        X_train_preprocessed = self.preprocessor.fit_transform(X_train)
        X_test_preprocessed = self.preprocessor.transform(X_test)

        # Initialize the model
        self.model = self.build_nn_model(X_train_preprocessed.shape[1])
        # Train the model
        self.model.fit(
            X_train_preprocessed,
            y_train,
            epochs=500,
            batch_size=32,
            verbose=1,
            validation_data=(X_test_preprocessed, y_test),
            callbacks=callbacks,
        )

        # Save the trained model
        self.model.save(self.model_path)
        print(f"Neural network model saved to {self.model_path}.")

    def train_with_existing_data(self, target_column):
        """Load old data, preprocess it, and train the neural network model."""
        data = pd.read_excel(self.excel_path)

        # Preprocess the data
        X = self.preprocessor.fit_transform(data[features])
        y = data[target_column].astype(int)

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Build the model
        self.model = self.build_nn_model(X_train.shape[1])

        # Train the model
        self.model.fit(
            X_train,
            y_train,
            epochs=100,
            batch_size=32,
            verbose=1,
            validation_data=(X_test, y_test),
        )

        # Save the trained model
        self.model.save(self.model_path)
        print("Neural network model trained and saved.")

    def predict_and_proba(self, X_raw):
        """Make predictions with probabilities based on the raw input features."""
        X_processed = self.preprocessor.transform(X_raw)
        probabilities = self.model.predict(X_processed).flatten()
        predictions = (probabilities > 0.5).astype(
            int
        )  # Convert probabilities to 0 or 1 predictions
        return predictions, probabilities

    def predict_model(self, todays_data):
        # Ensure todays_data is structured correctly for preprocessing
        with pd.ExcelWriter("DataFrames/NN_Predictions_for_today.xlsx") as writer:
            for stat_type, df in todays_data.items():
                # Directly pass df with features to preserve DataFrame structure

                # The predict_and_proba method is adjusted to handle DataFrame directly
                predictions, probabilities = self.predict_and_proba(df[features])

                # Assign predictions and their corresponding probabilities
                df["Prediction"] = predictions
                df["Confidence"] = probabilities

                # Prepare only the relevant columns to be saved
                df_to_save = df[
                    ["Teams", "Player Name", "O/U", "Prediction", "Confidence"]
                ]
                df_to_save.to_excel(writer, sheet_name=stat_type, index=False)

        print("Predictions saved in 'NN_Predictions_for_today.xlsx'")


# Utility functions like load_model need to be imported if used outside of the training context
from tensorflow.keras.models import load_model
