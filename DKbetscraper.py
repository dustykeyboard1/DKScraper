from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json


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
scraper = DraftKingsScraper()
odds_data = scraper.scrape_odds()
for key, value in odds_data.items():
    print(f"Key: {key}")
    print("\n")
    for item in value:
        print(f"Value: {item.text}")
    print("\n")
