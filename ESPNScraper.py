import requests
from bs4 import BeautifulSoup
from scipy.stats import percentileofscore
import pandas as pd
import time
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


nba_teams = {
    "Atlanta": "ATL",
    "Boston": "BOS",
    "Brooklyn": "BKN",
    "Charlotte": "CHO",
    "Chicago": "CHI",
    "Cleveland": "CLE",
    "Dallas": "DAL",
    "Denver": "DEN",
    "Detroit": "DET",
    "Golden State": "GSW",
    "Houston": "HOU",
    "Indiana": "IND",
    "LA": "LAC",  # This could be LAC or LAL depending on the context
    "Memphis": "MEM",
    "Miami": "MIA",
    "Milwaukee": "MIL",
    "Minnesota": "MIN",
    "New Orleans": "NOP",
    "New York": "NYK",
    "Oklahoma City": "OKC",
    "Orlando": "ORL",
    "Philadelphia": "PHI",
    "Phoenix": "PHX",
    "Portland": "POR",
    "Sacramento": "SAC",
    "San Antonio": "SAS",
    "Toronto": "TOR",
    "Utah": "UTA",
    "Washington": "WAS",
}


class EspnScraper:
    def __init__(self):
        self.team_stats_cash = {}
        self.team_defensive_stats = {}
        self.position_stats = {}

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

    def find_team_defensive_stats(self, team):
        if team not in self.team.defensive_stats:
            url = f"https://www.basketball-reference.com/teams/{team}/2024_games.html"
            time.sleep(7)
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                table = soup.find("div", {"id": "div_team_and_opponent"})
                field_goal_percentage = table.find("tr", {"data-row": "1"}).find(
                    "td", {"data-stat": "fg_pct"}
                )
                field_goal_rank = table.find("tr", {"data-row": "2"}).find(
                    "td", {"data-stat": "fg_pct"}
                )
                rebounds_per_game = table.find("tr", {"data-row": "1"}).find(
                    "td", {"data-stat": "trb_per_g"}
                )
                rebound_rank = table.find("tr", {"data-row": "2"}).find(
                    "td", {"data-stat": "trb_per_g"}
                )
                assists_per_game = table.find("tr", {"data-row": "1"}).find(
                    "td", {"data-stat": "ast_per_g"}
                )
                assists_rank = table.find("tr", {"data-row": "2"}).find(
                    "td", {"data-stat": "ast_per_g"}
                )
                self.find_team_defensive_stats[team] = [
                    field_goal_percentage,
                    field_goal_rank,
                    rebounds_per_game,
                    rebound_rank,
                    assists_per_game,
                    assists_rank,
                ]

    def return_position_xpath(self, pos):
        for index, value in enumerate(["PG", "SG", "SF", "PF", "C"]):

            if value == pos:

                return f"/html/body/div[1]/div/div/div[1]/div/main/div[1]/section[2]/div/div[1]/div/ul/li[{str(index + 2)}]"

    def return_time_xpath(self, time):
        if time == "last7":
            return "/html/body/div[1]/div/div/div[1]/div/main/div[1]/section[2]/div/div[2]/div/ul/li[2]"
        else:
            return "/html/body/div[1]/div/div/div[1]/div/main/div[1]/section[2]/div/div[2]/div/ul/li[3]"

    def scrape_table_to_dataframe(self, driver, table_xpath):
        # Navigate to the page containing the table (assuming driver.get('URL') has been called earlier)

        # Find the table by its XPath
        table = driver.find_element(By.XPATH, table_xpath)

        # Initialize lists to hold column headers and the row data
        columns = []
        data = []

        # Extract column names
        headers = table.find_elements(By.XPATH, ".//thead/tr/th")
        for header in headers:
            columns.append(header.text.strip())

        # Extract rows
        rows = table.find_elements(By.XPATH, ".//tbody/tr")
        for row in rows:
            row_data = []
            cells = row.find_elements(
                By.XPATH, "./*[self::td or self::th]"
            )  # Match both td and th
            for cell in cells:
                row_data.append(cell.text.strip())
            data.append(row_data)

        # Create a DataFrame from the extracted data
        df = pd.DataFrame(data, columns=columns)

        return df

    def clean_column_names(self, df):
        cleaned_columns = {}
        for col in df.columns:
            # Remove unwanted text and assign new names to a dictionary
            cleaned_columns[col] = col.split("\n")[0].strip()
        # Rename the columns using the dictionary
        df.rename(columns=cleaned_columns, inplace=True)

    def match_team_name_to_code(self, full_team_name):
        # Remove any trailing numbers and extra spaces
        team_name = re.sub(r"\d+-\d+", "", full_team_name).strip()
        # Match the team name to its code using the dictionary
        for full_name, code in nba_teams.items():
            if team_name in full_name:
                return code
        return "Unknown"

    def find_position_opponent_stats(self, position):
        if position not in self.position_stats:
            browser = webdriver.Edge()
            browser.get("https://www.bettingpros.com/nba/defense-vs-position/")

            wait = WebDriverWait(browser, 10)

            button_xpath = "/html/body/div[1]/div/div/div[1]/div/main/div[1]/section[2]/div/div[1]/div/button"
            button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, button_xpath))
            )
            button.click()

            xpath = self.return_position_xpath(position)
            # xpath = f"//li[contains(@class, 'menu__option') and contains(@data-value, '{position}')]"
            position_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            position_element.click()

            table_xpath = (
                "/html/body/div[1]/div/div/div[1]/div/main/div[2]/div[2]/div/table"
            )
            WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.XPATH, table_xpath))
            )

            season_df = self.scrape_table_to_dataframe(browser, table_xpath)

            button_xpath = "/html/body/div[1]/div/div/div[1]/div/main/div[1]/section[2]/div/div[2]/div/button"
            button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, button_xpath))
            )
            button.click()

            xpath = "/html/body/div[1]/div/div/div[1]/div/main/div[1]/section[2]/div/div[2]/div/ul/li[2]"
            position_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            position_element.click()
            WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.XPATH, table_xpath))
            )
            last7df = self.scrape_table_to_dataframe(browser, table_xpath)

            button_xpath = "/html/body/div[1]/div/div/div[1]/div/main/div[1]/section[2]/div/div[2]/div/button"
            button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, button_xpath))
            )
            button.click()

            xpath = "/html/body/div[1]/div/div/div[1]/div/main/div[1]/section[2]/div/div[2]/div/ul/li[3]"
            position_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            position_element.click()
            WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.XPATH, table_xpath))
            )
            last15df = self.scrape_table_to_dataframe(browser, table_xpath)

            self.position_stats[position] = {
                "Season": season_df,
                "Last7": last7df,
                "Last15": last15df,
            }

            browser.quit()

    def write_excel(self):
        path = "Dataframes/TeamStats.xlsx"
        with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
            for stat_type, dict in self.position_stats.items():
                for time, df in dict.items():
                    df.to_excel(writer, sheet_name=stat_type + time)

    def return_defensive_cache(self, pos):
        return self.position_stats[pos]

    def return_cache_value(self, team):
        return self.team_stats_cash[team]


scraper = EspnScraper()
scraper.find_position_opponent_stats("SG")
dict = scraper.return_defensive_cache("SG")
scraper.write_excel()
