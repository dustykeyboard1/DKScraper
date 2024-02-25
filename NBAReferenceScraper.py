import requests
from bs4 import BeautifulSoup
from scipy.stats import percentileofscore
import pandas as pd
import time
import re


class PlayerStatsScraper:
    def __init__(self):
        self.player_stats_cache = {}

    def generate_player_url(self, player_name):
        search_url = f"https://www.basketball-reference.com/search/search.fcgi?search={player_name.replace(' ', '+')}"
        response = requests.get(search_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            players_div = soup.find("div", id="players")
            player_url_div = (
                players_div.find("div", class_="search-item-url")
                if players_div
                else None
            )
            if player_url_div:
                player_page_url = f"https://www.basketball-reference.com{player_url_div.text[:-5]}/gamelog/2024"
                return player_page_url
            else:
                emergency_url = (
                    soup.find("link", rel="canonical")["href"][:-5] + "/gamelog/2024"
                )
                return emergency_url
        else:
            print("Failed to make a request to Basketball Reference.")
            return None

    def calculate_over_percentage(self, ou, game_stats, multiple=True):
        games_over = (
            sum(1 for stats in game_stats if sum(stats) > ou)
            if multiple
            else sum(1 for stat in game_stats if stat > ou)
        )
        percentage_over = games_over / len(game_stats) * 100 if game_stats else -99
        return percentage_over

    def calculate_percentile(self, ou, stats_list, multiple=True):
        combined_stats = (
            [sum(game_stat) for game_stat in stats_list]
            if multiple
            else [stat for stat in stats_list]
        )
        return percentileofscore(combined_stats, ou, kind="strict")

    def fetch_player_stats(self, player_name):
        if player_name not in self.player_stats_cache:
            url = self.generate_player_url(player_name)
            time.sleep(7)
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                game_rows = soup.findAll(
                    "tr", {"id": lambda x: x and x.startswith("pgl_basic")}
                )
                game_stats = [
                    (
                        int(row.find("td", {"data-stat": "pts"}).text or 0),
                        int(row.find("td", {"data-stat": "trb"}).text or 0),
                        int(row.find("td", {"data-stat": "ast"}).text or 0),
                    )
                    for row in game_rows
                ]
                player_team = (
                    soup.findAll("td", {"data-stat": "team_id"})[-1].text
                    if soup.findAll("td", {"data-stat": "team_id"})
                    else "Free Agent"
                )
                player_position = "Position parsing needs adjustment"  # Adjust position parsing based on your requirements
                self.player_stats_cache[player_name] = [
                    game_stats,
                    player_team,
                    player_position,
                ]
            else:
                print(f"Failed to fetch data for {player_name}")
                self.player_stats_cache[player_name] = []

    def return_Cache_value(self, Player):
        return self.player_stats_cache[Player]

    # Additional methods to integrate DataFrame creation and analysis would go here


# Example usage:
# scraper = PlayerStatsScraper()
# scraper.fetch_player_stats("LeBron James")
# Implement DataFrame creation and analysis methods as needed