import requests
from bs4 import BeautifulSoup
from scipy.stats import percentileofscore
import pandas as pd
import time
import re


class EspnScraper:
    def __init__(self):
        self.team_stats_cash = {}

    def find_team_record(self, team):
        if team not in self.team_stats_cash:
            url = f"https://www.basketball-reference.com/teams/{team}/2024_games.html"
            time.sleep(7)
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                game_rows = soup.findAll("tr")
                result = [
                    (
                        1
                        if game_row.find("td", {"data-stat": "game_result"})
                        and game_row.find(
                            "td", {"data-stat": "game_result"}
                        ).text.strip()
                        == "W"
                        else (
                            0
                            if game_row.find("td", {"data-stat": "game_result"})
                            and game_row.find(
                                "td", {"data-stat": "game_result"}
                            ).text.strip()
                            == "L"
                            else None
                        )
                    )
                    for game_row in game_rows
                ]

                result = list(filter(None.__ne__, result))
                self.team_stats_cash[team] = result
            else:
                print(
                    f"Error in Team Record Scraping for {team}, repsonse code: {response.status_code}"
                )

    def return_cache_value(self, team):
        return self.team_stats_cash[team]
