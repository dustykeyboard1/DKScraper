from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import pandas as pd


class DraftKingsScraper:
    def __init__(self):
        self.base_url = "https://sportsbook.draftkings.com/nba-player-props"
        self.browser = webdriver.Chrome()  # Adjust if you're using a different browser
        self.wait = WebDriverWait(self.browser, 180)

    def navigate_and_load(self, catagory, subcategory):
        full_url = f"{self.base_url}?category={catagory}&subcategory={subcategory}"
        self.browser.get(full_url)
        class_name_to_wait_for = ".sportsbook-event-accordion__wrapper.expanded"
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, class_name_to_wait_for))
        )

    def click_button(self, button_id):
        button = self.wait.until(EC.element_to_be_clickable((By.ID, button_id)))
        button.click()
        class_name_to_wait_for = ".sportsbook-event-accordion__wrapper.expanded"
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, class_name_to_wait_for))
        )

    def fetch_data(self):
        updated_html = self.browser.page_source
        soup = BeautifulSoup(updated_html, "html.parser")
        return self.find_games(soup)

    def find_games(self, soup):
        # Implement based on how you identify games in the HTML
        games = soup.find_all(class_="sportsbook-event-accordion__wrapper expanded")
        return games

    def parse_game_data(self, game):
        """Extracts and returns the team names, player names, and odds from a game."""
        data = []
        team_names_div = game.find(
            "div", {"aria-label": re.compile(r"^Event Accordion for.*")}
        )
        teams = (
            team_names_div["aria-label"].replace("Event Accordion for ", "")
            if team_names_div
            else "Teams not found"
        )

        rows = game.findAll("tr")
        for row in rows:
            data.append(self.parse_row_data(row, teams))
        return data

    def parse_row_data(self, row, teams):
        """Extracts data from a single row."""
        player_name = (
            row.find("span", class_="sportsbook-row-name").text
            if row.find("span", class_="sportsbook-row-name")
            else "N/A"
        )
        ou_value_over, odds_over, ou_value_under, odds_under = self.extract_odds(row)

        return {
            "Teams": teams,
            "Player Name": player_name,
            "O/U": ou_value_over,
            "Odds for Over": odds_over,
            "Odds for Under": odds_under,
        }

    def extract_odds(self, row):
        """Extracts over/under values and odds from a row."""
        ou_value_over = ou_value_under = odds_over = odds_under = "N/A"
        outcomes = row.find_all("div", class_="sportsbook-outcome-cell__body")
        for outcome in outcomes:
            label, ou_value, odds = self.parse_outcome(outcome)
            if label.startswith("O"):
                ou_value_over, odds_over = ou_value, odds
            elif label.startswith("U"):
                ou_value_under, odds_under = ou_value, odds
        return ou_value_over, odds_over, ou_value_under, odds_under

    def parse_outcome(self, outcome):
        """Extracts label, over/under value, and odds from an outcome."""
        label = (
            outcome.find("span", class_="sportsbook-outcome-cell__label").text
            if outcome.find("span", class_="sportsbook-outcome-cell__label")
            else "N/A"
        )
        ou_value = (
            outcome.find("span", class_="sportsbook-outcome-cell__line").text
            if outcome.find("span", class_="sportsbook-outcome-cell__line")
            else "N/A"
        )
        odds = (
            outcome.find("span", class_="sportsbook-odds").text
            if outcome.find("span", class_="sportsbook-odds")
            else "N/A"
        )
        return label, ou_value, odds

    def create_data_table(self, odds_data):
        """Creates a DataFrame from the structured odds data."""
        stat_dict = {}
        for key, games in odds_data.items():
            all_data = []
            for game in games:
                all_data.extend(self.parse_game_data(game))
            df = pd.DataFrame(all_data)
            stat_dict[key] = df
        return stat_dict

    def scrape_odds(self):
        url_list = [
            ("player-combos", "pts-%2B-reb-%2B-ast", "PRA"),
            ("player-combos", "pts-%2B-reb", "PR"),
            ("player-combos", "pts-%2B-ast", "PA"),
            ("player-points", "points", "P"),
            ("player-rebounds", "rebounds", "R"),
            ("player-assists", "assists", "A"),
        ]
        data = {}
        for urls in url_list:
            self.navigate_and_load(urls[0], urls[1])
            data[urls[2]] = self.fetch_data()
        self.browser.close()
        return data


# Example usage
# scraper = DraftKingsScraper()
# odds_data = scraper.scrape_odds()
# info = scraper.create_data_table(odds_data)
# print(info.head())
