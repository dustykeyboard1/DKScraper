import requests
from bs4 import BeautifulSoup
import pandas as pd
from scipy.stats import percentileofscore
from NBAReferenceScraper import PlayerStatsScraper
from tqdm import tqdm
from tqdm.auto import tqdm
import traceback
import statistics as st
from ESPNScraper import EspnScraper

tqdm.pandas()

nba_teams = {
    "ATL Hawks": "ATL",
    "BOS Celtics": "BOS",
    "BKN Nets": "BKN",
    "CHA Hornets": "CHO",
    "CHI Bulls": "CHI",
    "CLE Cavaliers": "CLE",
    "DAL Mavericks": "DAL",
    "DEN Nuggets": "DEN",
    "DEWT Pistons": "DET",
    "GS Warriors": "GSW",
    "HOU Rockets": "HOU",
    "IND Pacers": "IND",
    "LA Clippers": "LAC",
    "LA Lakers": "LAL",
    "MEM Grizzlies": "MEM",
    "MIA Heat": "MIA",
    "MIL Bucks": "MIL",
    "MIN Timberwolves": "MIN",
    "NO Pelicans": "NOP",
    "NK Knicks": "NYK",
    "OKC Thunder": "OKC",
    "ORL Magic": "ORL",
    "PHI 76ers": "PHI",
    "Phoenix Suns": "PHX",
    "POR Trail Blazers": "POR",
    "SAC Kings": "SAC",
    "SA Spurs": "SAS",
    "TOR Raptors": "TOR",
    "UTA Jazz": "UTA",
    "WAS Wizards": "WAS",
}


class PlayerPerformanceAnalyzer:
    def __init__(self, dataframe):
        self.stats_Scraper = PlayerStatsScraper()
        self.team_Scraper = EspnScraper()
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
            df["Game Average Minutes"] = 0.0
            df["Last 10 Games Average Minutes"] = 0.0
            df["Last 10 Games Average Minutes"] = 0.0
            df["Team Win Percentage"] = 0.0
            df["Last 10 Games Win Percentage"] = 0.0
            df["Last 5 Games Win Percentage"] = 0.0
            df["Opponents Team Win Percentage"] = 0.0
            df["Opponents Last 10 Games Win Percentage"] = 0.0
            df["Opponents Last 5 Games Win Percentage"] = 0.0

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

    def get_opposing_team_code(self, game_row, team):
        # Split the game row into home team and away team
        home_team, away_team = game_row.split(" @ ")
        print(home_team, away_team)
        # Look up team codes
        home_team_code = nba_teams.get(home_team.strip(), "Team not found")
        away_team_code = nba_teams.get(away_team.strip(), "Team not found")
        if home_team_code == team:
            return away_team_code
        else:
            return home_team_code

    def calculate_win_percentage(self, result_list):
        return sum(result_list) / len(result_list)

    def add_new_columns(self, row, stat_type):
        # Assuming stats_scraper is an instance of a class that has the necessary methods
        try:
            player_name = row["Player Name"]
            if player_name == "N/A":
                return row  # Return the row unchanged if player name is not available

            ou_value = float(row["O/U"])
            self.stats_Scraper.fetch_player_stats(player_name)
            player_stats = self.stats_Scraper.return_Cache_value(player_name)
            game_stats, player_team, player_position, minute_stats = (
                player_stats[0],
                player_stats[1],
                player_stats[2],
                player_stats[3],
            )

            relevant_stats = self.gather_relevant_stats(
                stat_type, game_stats
            )  # Assuming this function exists and is defined elsewhere
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

            row["Game Average Minutes"] = st.mean(minute_stats)
            row["Last 10 Games Average Minutes"] = st.mean(minute_stats[-10:])
            row["Last 5 games average minutes"] = st.mean(minute_stats[-5:])
            print(player_team)
            self.team_Scraper.find_team_record(player_team)
            team_record = self.team_Scraper.return_cache_value(player_team)
            row["Team Win Percentage"] = self.calculate_win_percentage(team_record)
            row["Last 10 Games Win Percentage"] = self.calculate_win_percentage(
                team_record[-10:]
            )
            row["Last 5 Games Win Percentage"] = self.calculate_win_percentage(
                team_record[-5:]
            )

            opposing_team = self.get_opposing_team_code(row["Teams"], player_team)
            print(f"opposing_team: {opposing_team}")
            self.team_Scraper.find_team_record(opposing_team)
            opposing_team_record = self.team_Scraper.return_cache_value(opposing_team)
            row["Opponents Team Win Percentage"] = self.calculate_win_percentage(
                team_record
            )
            row["Opponents Last 10 Games Win Percentage"] = (
                self.calculate_win_percentage(team_record[-10:])
            )
            row["Opponents Last 5 Games Win Percentage"] = (
                self.calculate_win_percentage(team_record[-5:])
            )

            return row
        except Exception as e:
            print(f"Error Processing {player_name}.")
            print(Exception, e)
            return row

    def enrich_with_coverage(self):
        for stat_type, df in self.df.items():
            print(f"Processing {stat_type}.")
            # Limit the operation to the first 5 rows for easier testing and demonstration
            # Ensure to reassign the processed DataFrame slice back to the original DataFrame
            self.df[stat_type].iloc[:5] = df.iloc[:5].progress_apply(
                lambda row: self.add_new_columns(row, stat_type), axis=1
            )

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
            "DataFrames/testoutput.xlsx", engine="xlsxwriter"
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
