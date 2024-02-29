import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
from NBAReferenceScraper import PlayerStatsScraper
import tqdm


class BasketballStatsProcessor:
    def __init__(self, data_frames):
        self.scraper = PlayerStatsScraper()
        self.data_frames = data_frames
        self.stat_types = {
            "PRA": ["PTS", "REB", "AST"],
            "PR": ["PTS", "REB"],
            "PA": ["PTS", "AST"],
            "P": ["PTS"],
            "R": ["REB"],
            "A": ["AST"],
        }

    def get_most_recent_game_stats(self, player_name):
        self.scraper.get_most_recent_game_stats(player_name)
        return self.scraper.return_last_night_cache(player_name)

    def update_data_frames(self):
        # Map from stat names to their indices in the last_night_stats list
        stat_to_index = {"PTS": 0, "REB": 1, "AST": 2}

        for stat_type, df in self.data_frames.items():
            print(f"Processing {stat_type}...")
            new_column_name = f"Last Night {stat_type}"

            # Add a new column to the DataFrame to store last night's performance
            df[new_column_name] = 0.0

            for index, row in tqdm.tqdm(
                df.iterrows(), total=df.shape[0], desc=f"Updating {stat_type}"
            ):
                player_name = row["Player Name"]
                try:
                    # Get the most recent game stats
                    last_night_stats = self.get_most_recent_game_stats(player_name)

                    if last_night_stats:
                        # Calculate the sum of relevant stats for the current stat type
                        relevant_stats_sum = sum(
                            last_night_stats[stat_to_index[stat]]
                            for stat in self.stat_types[stat_type]
                        )
                        df.at[index, new_column_name] = relevant_stats_sum
                except Exception as e:
                    print(f"Error Processing {player_name}: {e}")
                    continue

        # At this point, all DataFrames have been updated with last night's performance
        self.write_dataframe()

    def write_dataframe(self, dict=None, path=None):
        if dict is None and path is None:
            with pd.ExcelWriter(
                "DataFrames/FinishedOutput.xlsx", engine="xlsxwriter"
            ) as writer:
                for stat_type, df in self.data_frames.items():
                    df.to_excel(writer, sheet_name=stat_type)
        else:
            with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
                for stat_type, df in dict.items():
                    df.to_excel(writer, sheet_name=stat_type)


# Usage Example:
# Assuming 'data_frames' is a dictionary of DataFrames where keys are stat types
# and each DataFrame has a "Player Name" column

# # Initialize the processor with the data frames
# processor = BasketballStatsProcessor(data_frames)

# # Update the data frames with last night's stats
# updated_data_frames = processor.update_data_frames()
