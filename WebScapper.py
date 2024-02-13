import requests
from bs4 import BeautifulSoup  # Only if you need to parse HTML
import pandas as pd
import tqdm
import time
import re


def check_proxy(proxy):
    """
    Checks the proxy server by sending a GET request to httpbin.
    Returns False if there is an error from the `get` function
    """

    return requests.get("http://httpbin.org/ip", proxy) is not None


def make_request_debug():
    url = "https://sportsbook.draftkings.com/nba-player-props?category=player-combos&subcategory=pts-+-reb"
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
            data = response.json()
            return data
        except requests.exceptions.JSONDecodeError:
            print("Error decoding JSON from response")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
    return None


def make_request():
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


def find_games(soup_object):
    game_list = soup_object.findAll(
        "div", class_="sportsbook-event-accordion__wrapper expanded"
    )
    return game_list


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
    df.to_excel("Dataframes/Finaloutput.xlsx")
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
    games_over = sum(1 for stats in game_stats if sum(stats) > ou)
    # Calculate the percentage
    percentage_over = games_over / len(game_stats) * 100 if game_stats else 0
    return percentage_over


def add_stats(df):

    df["Season Over Covered %"] = 0
    df["Last 10 Games Over Covered %"] = 0
    df["Last 5 Games Over Covered %"] = 0
    # Example DataFrame column access: assuming df is your DataFrame and it has a column 'Player Name'
    for index, row in tqdm.tqdm(df.iterrows(), total=df.shape[0]):
        try:
            player_name = row["Player Name"]
            url = generate_player_url(player_name)

            # Make the request
            time.sleep(7)
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")
                game_rows = [
                    r for r in soup.findAll("tr") if r.find("td", {"data-stat": "trb"})
                ]
                game_stats = []
                for game_row in game_rows:
                    trb = int(game_row.find("td", {"data-stat": "trb"}).text.strip())
                    pts = int(game_row.find("td", {"data-stat": "pts"}).text.strip())
                    ast = int(game_row.find("td", {"data-stat": "ast"}).text.strip())
                    game_stats.append((trb, pts, ast))

                # Calculate the total for points, rebounds, and assists

                # Update the DataFrame with the new calculations
                ou_value = row["O/U"]
                ou_value = row["O/U"]
                df.at[index, "Season Over Covered %"] = calculate_over_percentage(
                    ou_value, game_stats
                )
                df.at[index, "Last 10 Games Over Covered %"] = (
                    calculate_over_percentage(ou_value, game_stats[-10:])
                )
                df.at[index, "Last 5 Games Over Covered %"] = calculate_over_percentage(
                    ou_value, game_stats[-5:]
                )
        except Exception as e:
            print(e, player_name)
            continue

    df.to_excel("Dataframes/Finaloutput.xlsx")


def main():
    soup = make_request()
    prop_soup = find_games(soup)
    df = create_data_table(prop_soup)
    df = pd.read_excel("Dataframes/Finaloutput.xlsx")
    add_stats(df)


main()
