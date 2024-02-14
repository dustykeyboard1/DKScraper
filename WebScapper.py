import requests
from bs4 import BeautifulSoup  # Only if you need to parse HTML
import pandas as pd
import tqdm
import time
import re
from scipy.stats import percentileofscore
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver_path = "/Users/michaelscoleri/Downloads/chromedriver_mac_arm64(1)/chromedriver"  # Update this path
browser = webdriver.Chrome()


def check_proxy(proxy):
    """
    Checks the proxy server by sending a GET request to httpbin.
    Returns False if there is an error from the `get` function
    """

    return requests.get("http://httpbin.org/ip", proxy) is not None


def make_request_debug():
    url = "https://sportsbook.draftkings.com/leagues/basketball/nba?category=player-combos&subcategory=pts-%2B-reb"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }
    response = requests.get(url, headers=headers)
    print(response.text)
    if response.history:
        print("Request was redirected.")
        for resp in response.history:
            print(resp.status_code, resp.url)
        print("Final destination:", response.status_code, response.url)
    else:
        print("Request was not redirected.")

    if response.status_code == 200:
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            return data
        except requests.exceptions.JSONDecodeError:
            print("Error decoding JSON from response")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
    return None


def find_games(soup_object):
    game_list = soup_object.findAll(
        "div", class_="sportsbook-event-accordion__wrapper expanded"
    )
    print(game_list)
    return game_list


def make_PAR_request():
    url = "https://sportsbook.draftkings.com/nba-player-props?category=player-combos&subcategory=pts-%2B-reb-%2B-ast"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }
    response = requests.get(url, headers=headers)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    print("Gathered Soup...")
    return soup


def make_PA_request():
    url = "https://sportsbook.draftkings.com/nba-player-props?category=player-combos&subcategory=pts-%2B-reb-%2B-ast"
    # headers = {
    #     "User-Agent": "Mozilla/5.0",
    #     "Accept": "application/json",
    # }
    # response = requests.get(url, headers=headers)
    # html_content = response.text
    # soup = BeautifulSoup(html_content, "html.parser")
    # print("Gathered Soup...")

    # Navigate to the page
    browser.get(url)
    wait = WebDriverWait(browser, 180)  # Waits for 10 seconds maximum
    class_name_to_wait_for = (
        ".sportsbook-event-accordion__wrapper.expanded"  # CSS selector for your class
    )
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, class_name_to_wait_for))
    )
    updated_html = browser.page_source
    soup = BeautifulSoup(updated_html, "html.parser")
    PARsoup = find_games(soup)

    # Wait for an element that indicates the page has loaded
    button = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable(
            (By.ID, "subcategory_Pts + Reb")
        )  # Update with actual criteria
    )
    button.click()
    wait = WebDriverWait(browser, 180)  # Waits for 10 seconds maximum
    class_name_to_wait_for = (
        ".sportsbook-event-accordion__wrapper.expanded"  # CSS selector for your class
    )
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, class_name_to_wait_for))
    )

    updated_html = browser.page_source
    soup = BeautifulSoup(updated_html, "html.parser")
    PRsoup = find_games(soup)

    button = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable(
            (By.ID, "subcategory_Pts + Ast")
        )  # Update with actual criteria
    )
    button.click()
    wait = WebDriverWait(browser, 180)  # Waits for 10 seconds maximum
    class_name_to_wait_for = (
        ".sportsbook-event-accordion__wrapper.expanded"  # CSS selector for your class
    )
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, class_name_to_wait_for))
    )
    updated_html = browser.page_source
    soup = BeautifulSoup(updated_html, "html.parser")
    PAsoup = find_games(soup)
    browser.close()
    return PARsoup, PRsoup, PAsoup


def create_data_table(game_list):
    data = []
    for game in game_list:
        team_names_div = game.find(
            "div", {"aria-label": re.compile(r"^Event Accordion for.*")}
        )
        if team_names_div:
            # The team names are in the 'aria-label' attribute
            teams = team_names_div["aria-label"].replace("Event Accordion for ", "")
        else:
            teams = "Teams not found"
        rows = game.findAll("tr")
        for row in rows:
            player_name = (
                row.find("span", class_="sportsbook-row-name").text
                if row.find("span", class_="sportsbook-row-name")
                else "N/A"
            )

            # Variables to store over and under odds and O/U values, initializing them to 'N/A'
            ou_value_over, odds_over = "N/A", "N/A"
            ou_value_under, odds_under = "N/A", "N/A"

            # Find all outcomes in the row (assuming one for over and one for under)
            outcomes = row.find_all("div", class_="sportsbook-outcome-cell__body")
            for outcome in outcomes:
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

                # Check if the outcome is over or under and assign values accordingly
                if label.startswith("O"):
                    ou_value_over = ou_value
                    odds_over = odds
                elif label.startswith("U"):
                    ou_value_under = ou_value
                    odds_under = odds

            # Append the data for the current row to the list
            data.append(
                {
                    "Teams": teams,
                    "Player Name": player_name,
                    "O/U": ou_value_over,
                    "Odds for Over": odds_over,
                    "Odds for Under": odds_under,
                }
            )

    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(data)
    print("Created df, now saving...")
    # df.to_excel("Dataframes/Finaloutput.xlsx")
    return df


# def generate_player_slug(full_name):
#     # Split the full name into first and last names
#     if isinstance(full_name, (float)):
#         return None

#     names = full_name.split()
#     first_name, last_name = (
#         names[0],
#         names[1],
#     )  # Assumes the last word is the last name

#     # Extract the first 5 letters of the last name (or the entire last name if it's shorter than 5 letters)
#     last_name_part = last_name[:5]

#     # Extract the first 2 letters of the first name
#     first_name_part = first_name[:2]

#     # Combine them with '01' at the end
#     player_slug = (
#         f"{last_name_part}{first_name_part}01".lower()
#     )  # Convert to lowercase as in the example URL

#     return player_slug


def generate_player_url(player_name):
    search_url = f"https://www.basketball-reference.com/search/search.fcgi?search={player_name.replace(' ', '+')}"
    response = requests.get(search_url)
    # If the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the div containing player search results
        players_div = soup.find("div", id="players")

        # Within this div, find the first div with class 'search-item-url'
        player_url_div = (
            players_div.find("div", class_="search-item-url") if players_div else None
        )

        # If a div was found, extract the URL
        if player_url_div:
            player_page_url = player_url_div.text[:-5]
            # Construct the full URL
            player_page_url = (
                f"https://www.basketball-reference.com{player_page_url}/gamelog/2024"
            )
            return player_page_url
        else:
            emergency_url = (
                soup.find("link", rel="canonical")["href"][:-5] + "/gamelog/2024"
            )
            return emergency_url
    else:
        print("Failed to make a request to Basketball Reference.")
        return None


# Function to calculate the percentage of games over the O/U
def calculate_over_percentage(ou, game_stats):
    # Count how many games the player covered the O/U
    games_over = sum(1 for stats in game_stats if sum(stats) > float(ou))
    # Calculate the percentage
    percentage_over = games_over / len(game_stats) * 100 if game_stats else 0
    return percentage_over


def calculate_percentile(ou, stats_list):
    # This function calculates the percentile rank of the O/U value within the given stats list.
    combined_stats = [sum(game_stat) for game_stat in stats_list]
    return percentileofscore(combined_stats, ou, kind="strict")


# def add_stats(df):

#     df["Season Over Covered %"] = 0
#     df["Last 10 Games Over Covered %"] = 0
#     df["Last 5 Games Over Covered %"] = 0
#     df["Season O/U Percentile"] = 0
#     df["Last 10 Games O/U Percentile"] = 0
#     df["Last 5 Games O/U Percentile"] = 0
#     # Example DataFrame column access: assuming df is your DataFrame and it has a column 'Player Name'
#     for index, row in tqdm.tqdm(df.iterrows(), total=df.shape[0]):
#         try:
#             player_name = row["Player Name"]
#             url = generate_player_url(player_name)

#             # Make the request
#             time.sleep(7)
#             response = requests.get(url)

#             # Check if the request was successful
#             if response.status_code == 200:
#                 html_content = response.text
#                 soup = BeautifulSoup(html_content, "html.parser")
#                 game_rows = [
#                     r for r in soup.findAll("tr") if r.find("td", {"data-stat": "trb"})
#                 ]
#                 game_stats = []
#                 for game_row in game_rows:
#                     trb = int(game_row.find("td", {"data-stat": "trb"}).text.strip())
#                     pts = int(game_row.find("td", {"data-stat": "pts"}).text.strip())
#                     ast = int(game_row.find("td", {"data-stat": "ast"}).text.strip())
#                     game_stats.append((trb, pts, ast))

#                 # Calculate the total for points, rebounds, and assists

#                 # Update the DataFrame with the new calculations
#                 ou_value = row["O/U"]
#                 ou_value = row["O/U"]
#                 df.at[index, "Season Over Covered %"] = calculate_over_percentage(
#                     ou_value, game_stats
#                 )
#                 df.at[index, "Last 10 Games Over Covered %"] = (
#                     calculate_over_percentage(ou_value, game_stats[-10:])
#                 )
#                 df.at[index, "Last 5 Games Over Covered %"] = calculate_over_percentage(
#                     ou_value, game_stats[-5:]
#                 )
#                 df.at[index, "Season O/U Percentile"] = calculate_percentile(
#                     ou_value, game_stats
#                 )
#                 df.at[index, "Last 10 Games O/U Percentile"] = calculate_percentile(
#                     ou_value, game_stats[-10:]
#                 )
#                 df.at[index, "Last 5 Games O/U Percentile"] = calculate_percentile(
#                     ou_value, game_stats[-5:]
#                 )
#         except Exception as e:
#             print(e, player_name)
#             continue


#     df.to_excel("Dataframes/Finaloutput.xlsx")
def add_stats(df, stat_type):
    """
    Enhances the DataFrame with statistics based on the stat_type.
    :param df: DataFrame - The player stats DataFrame.
    :param stat_type: str - Specifies the stat combination ('P+R+A', 'P+R', 'P+A').
    """
    df["Season Over Covered %"] = 0
    df["Last 10 Games Over Covered %"] = 0
    df["Last 5 Games Over Covered %"] = 0
    df["Season O/U Percentile"] = 0
    df["Last 10 Games O/U Percentile"] = 0
    df["Last 5 Games O/U Percentile"] = 0

    for index, row in tqdm.tqdm(df.iterrows(), total=df.shape[0]):
        player_name = row["Player Name"]
        url = generate_player_url(player_name)
        time.sleep(7)
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            soup = BeautifulSoup(response.content, "html.parser")

            game_rows = soup.findAll(
                "tr", {"id": lambda x: x and x.startswith("pgl_basic")}
            )
            game_stats = []

            for game_row in game_rows:
                # Adjust stat extraction based on stat_type
                pts = int(game_row.find("td", {"data-stat": "pts"}).text.strip())
                trb = (
                    int(game_row.find("td", {"data-stat": "trb"}).text.strip())
                    if stat_type in ["P+R+A", "P+R"]
                    else 0
                )
                ast = (
                    int(game_row.find("td", {"data-stat": "ast"}).text.strip())
                    if stat_type in ["P+R+A", "P+A"]
                    else 0
                )

                game_stats.append((pts, trb, ast))

            # Calculate the total for points, rebounds, and assists
            ou_value = row["O/U"]

            # Update the DataFrame with the new calculations
            df.at[index, "Season Over Covered %"] = calculate_over_percentage(
                ou_value, game_stats
            )
            df.at[index, "Last 10 Games Over Covered %"] = calculate_over_percentage(
                ou_value, game_stats[-10:]
            )
            df.at[index, "Last 5 Games Over Covered %"] = calculate_over_percentage(
                ou_value, game_stats[-5:]
            )
            df.at[index, "Season O/U Percentile"] = calculate_percentile(
                ou_value, game_stats
            )
            df.at[index, "Last 10 Games O/U Percentile"] = calculate_percentile(
                ou_value, game_stats[-10:]
            )
            df.at[index, "Last 5 Games O/U Percentile"] = calculate_percentile(
                ou_value, game_stats[-5:]
            )
        except Exception as e:
            print(f"Error processing {player_name}: {e}")

    return df


def create_multisheet(df1, df2, df3):
    # First, enhance each DataFrame with additional stats
    enhanced_df1 = add_stats(df1, "P+R+A")
    enhanced_df2 = add_stats(df2, "P+R")
    enhanced_df3 = add_stats(df3, "P+A")

    # Then, write them to an Excel file with multiple sheets
    with pd.ExcelWriter(
        "Dataframes/multiple_sheets.xlsx", engine="xlsxwriter"
    ) as writer:
        enhanced_df1.to_excel(writer, sheet_name="P+R+A")
        enhanced_df2.to_excel(writer, sheet_name="P+R")
        enhanced_df3.to_excel(writer, sheet_name="P+A")


def main():
    # soup = make_request()
    # prop_soup = find_games(soup)
    # df = create_data_table(prop_soup)
    # df = pd.read_excel("Dataframes/Finaloutput.xlsx")
    # add_stats(df)
    # make_request_debug()
    PARsoup, PRsoup, PAsoup = make_PA_request()
    PARdf, PRdf, PAdf = (
        create_data_table(PARsoup),
        create_data_table(PRsoup),
        create_data_table(PAsoup),
    )
    create_multisheet(PARdf, PRdf, PAdf)


# print(soup)
# prop_soup = find_games(soup)
# print(prop_soup)


main()
