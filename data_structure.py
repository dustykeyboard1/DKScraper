import requests
from bs4 import BeautifulSoup
import pandas as pd
from scipy.stats import percentileofscore
from NBAReferenceScraper import PlayerStatsScraper
import tqdm
import traceback


class PlayerPerformanceAnalyzer:
    def __init__(self, dataframe):
        self.stats_Scraper = PlayerStatsScraper()
        self.df = dataframe
        # Additional attributes for storing team records, defensive ratings, etc.

    def fetch_player_yearly_data(self):
        # Iterate over DataFrame to fetch yearly data for each player
        for key, df in self.df.items():
            df["Team"] = ""
            df["Position"] = ""
            df["Season Over Covered %"] = 0.0
            df["Last 10 Games Over Covered %"] = 0.0
            df["Last 5 Games Over Covered %"] = 0.0

    def gather_relevant_stats(self, stat_type, game_stats):
        if stat_type == "PRA":
            relevant_stats = game_stats
        elif stat_type == "PR":
            relevant_stats = [(pts, trb) for pts, trb, _ in game_stats]
        elif stat_type == "PA":
            relevant_stats = [(pts, ast) for pts, _, ast in game_stats]
        elif stat_type == "P":
            relevant_stats = [(pts,) for pts, _, _ in game_stats]
        elif stat_type == "R":
            relevant_stats = [(trb,) for _, trb, _ in game_stats]
        elif stat_type == "A":
            relevant_stats = [(ast,) for _, _, ast in game_stats]
        else:
            relevant_stats = None
        return relevant_stats

    def add_new_columns(
        self,
        row,
        ou_value,
        relevant_stats,
        stat_type,
        player_position,
        player_team,
    ):
       row["Season Over Covered %"] = self.calculate_coverage(
            ou_value,
            relevant_stats,
            multiple=False if stat_type in ["P", "R", "A"] else True,
        )
       
        row["Last 10 Games Over Covered %"] = self.calculate_coverage(
            ou_value,
            relevant_stats[-10:],
            multiple=False if stat_type in ["P", "R", "A"] else True,
        )
        row["Last 5 Games Over Covered %"] = self.calculate_coverage(
            ou_value,
            relevant_stats[-5:],
            multiple=False if stat_type in ["P", "R", "A"] else True,
        )

        row["Position"] = player_position
        row["Team"] = player_team

    def enrich_with_coverage(self):
        for stat_type, df in self.df.items():
            for index, row in tqdm.tqdm(
                df.iterrows(), total=df.shape[0], desc=f"Processing {stat_type}"
            ):
                try:
                    player_name = row["Player Name"]
                    ou_value = float(row["O/U"])
                    self.stats_Scraper.fetch_player_stats(player_name)
                    player_stats = self.stats_Scraper.return_Cache_value(player_name)
                    game_stats = player_stats[0]
                    player_team = player_stats[1]
                    player_position = player_stats[2]
                    relevant_stats = self.gather_relevant_stats(stat_type, game_stats)
                    self.add_new_columns(
                        row,
                        ou_value,
                        relevant_stats,
                        stat_type,
                        player_position,
                        player_team,
                    )
                except Exception as e:
                    print(f"Error Processing stats for {player_name}.")
                    print(traceback.format_exc())

    def calculate_coverage(self, ou, game_stats, multiple):

        if multiple:
            games_over = sum(1 for stats in game_stats if sum(stats) > ou)
        else:
            games_over = sum(1 for stat in game_stats if stat[0] > ou)
        # Calculate the percentage
        percentage_over = games_over / len(game_stats) * 100 if game_stats else -99
        return percentage_over

    def enrich_with_defensive_ratings(self):
        # Add logic to fetch defensive ratings against player's position and enrich DataFrame
        pass

    def enrich_with_team_records(self):
        # Fetch and add team records to DataFrame
        pass

    def analyze_and_score_bets(self):
        # Based on gathered data, calculate scores for each bet
        # Consider factors like coverageS percentages, defensive ratings, team records
        pass

    # Additional methods as needed for analysis, fetching data, etc.
    def return_dataframe(self):
        return self.df

    def write_dataframe(self):
        with pd.ExcelWriter(
            "Dataframes/Testoutput.xlsx", engine="xlsxwriter"
        ) as writer:
            for stat_type, df in self.df.items():
                df.to_excel(writer, sheet_name=stat_type)


# # Example usage:
# # Assuming df is your initial DataFrame loaded with data
# analyzer = PlayerPerformanceAnalyzer(df)
# analyzer.fetch_player_yearly_data()
# analyzer.calculate_coverage()
# analyzer.enrich_with_defensive_ratings()
# analyzer.enrich_with_team_records()
# analyzer.analyze_and_score_bets()
