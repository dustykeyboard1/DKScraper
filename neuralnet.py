from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Dense,
    InputLayer,
    Dropout,
    ELU,
    Activation,
)
from tensorflow.keras.activations import swish
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.optimizers.schedules import PolynomialDecay, ExponentialDecay
from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pandas as pd
import numpy as np
import tensorflow as tf
from joblib import dump, load
import matplotlib.pyplot as plt

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
    EarlyStopping(
        monitor="val_loss",
        patience=20,  # Increased patience from 30 to 100
        verbose=1,
        restore_best_weights=True,  # Add this to restore model weights from the epoch with the best value of the monitored quantity.
    ),
    ModelCheckpoint(
        filepath="best_model.h5", monitor="val_loss", save_best_only=True, verbose=1
    ),
    ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=25,  # Increased patience from 15 to 50
        min_lr=0.0001,
        verbose=1,
    ),
]

initial_learning_rate = 0.001

# Assuming you have 500 epochs and you want the learning rate to update every epoch
decay_steps = 100000  # Adjust this based on your dataset size and training behavior

# Let's make the decay a bit more aggressive.
decay_rate = 0.96  # Now the rate decreases by 10% every decay step

lr_schedule = ExponentialDecay(
    initial_learning_rate,
    decay_steps=decay_steps,
    decay_rate=decay_rate,
    staircase=True,  # You can set this to False for a smoother decay
)

optimizer = Adam(learning_rate=lr_schedule)


class StatTypeNNModel:

    def __init__(
        self, excel_path="DataFrames/old_data.xlsx", model_path="Models/nn_model.h5"
    ):
        self.excel_path = excel_path
        self.model_path = model_path
        # Adjust the preprocessor to include scaling
        self.preprocessor = ColumnTransformer(
            transformers=[
                (
                    "num",
                    Pipeline(
                        steps=[
                            ("imputer", SimpleImputer(strategy="mean")),
                            ("scaler", StandardScaler()),
                        ]
                    ),
                    features,
                ),
            ],
            remainder="passthrough",
        )
        print("Preprocessing pipeline initialized.")

    def build_nn_model(self, input_shape):
        model = Sequential(
            [
                InputLayer(input_shape=(input_shape,)),
                Dense(64, activation="relu"),
                Dropout(0.35),  # Add dropout to reduce overfitting
                Dense(32, activation="relu"),
                Dropout(0.35),  # Add dropout
                Dense(1, activation="sigmoid"),
            ]
        )
        model.compile(
            optimizer=optimizer,  # Adjust learning rate if necessary
            loss="binary_crossentropy",
            metrics=["accuracy"],
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
            epochs=1000,
            batch_size=24,
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
        self.history = self.model.fit(
            X_train,
            y_train,
            epochs=1000,
            batch_size=24,
            verbose=1,
            validation_data=(X_test, y_test),
            callbacks=callbacks,
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

    def predict_model(self, todays_data, load_model=False):
        if load_model:
            self.model = tf.keras.models.load_model("Models/nn_model.h5")
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
                    [
                        "Teams",
                        "Player Name",
                        "Odds for Over",
                        "Odds for Under",
                        "O/U",
                        "Prediction",
                        "Confidence",
                    ]
                ]
                df_to_save.to_excel(writer, sheet_name=stat_type, index=False)

        print("Predictions saved in 'NN_Predictions_for_today.xlsx'")

    def plot_training(self):
        # Plot training & validation accuracy values
        plt.plot(self.history.history["accuracy"])
        plt.plot(self.history.history["val_accuracy"])
        plt.title("Model accuracy")
        plt.ylabel("Accuracy")
        plt.xlabel("Epoch")
        plt.legend(["Train", "Test"], loc="upper left")
        plt.show()

        # Plot training & validation loss values
        plt.plot(self.history.history["loss"])
        plt.plot(self.history.history["val_loss"])
        plt.title("Model loss")
        plt.ylabel("Loss")
        plt.xlabel("Epoch")
        plt.legend(["Train", "Test"], loc="upper left")
        plt.show()


# Utility functions like load_model need to be imported if used outside of the training context
from tensorflow.keras.models import load_model
