import pandas as pd


def odds_to_probability(odds):
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return -odds / (-odds + 100)


def read_and_process_excel(file_path):
    xls = pd.ExcelFile(file_path)
    df_list = []
    for sheet_name in xls.sheet_names:
        df = xls.parse(sheet_name)
        df["Bet Type"] = sheet_name  # Add the sheet name as 'Bet Type'
        df["Implied Prob Over"] = df["Odds for Over"].apply(odds_to_probability)
        df["Implied Prob Under"] = df["Odds for Under"].apply(odds_to_probability)
        df["Adjusted Confidence"] = df.apply(
            lambda x: 1 - x["Confidence"] if x["Prediction"] == 0 else x["Confidence"],
            axis=1,
        )
        df["Model Edge"] = df.apply(
            lambda x: x["Adjusted Confidence"]
            - (
                x["Implied Prob Over"]
                if x["Prediction"] == "Over"
                else x["Implied Prob Under"]
            ),
            axis=1,
        )
        df_list.append(df)
    all_bets = pd.concat(df_list, ignore_index=True)
    return all_bets


def select_straight_and_parlay_bets(df, straight_bet_count=5, parlay_bet_count=3):
    # Remove duplicates based on player and bet type
    df_unique = df.sort_values(by="Model Edge", ascending=False).drop_duplicates(
        subset=["Player Name", "Bet Type"], keep="first"
    )

    # Select straight bets
    straight_bets = df_unique.head(straight_bet_count)

    # For parlay, ensure not to pick from already selected straight bets and avoid duplicate players
    remaining_for_parlay = df_unique[~df_unique.index.isin(straight_bets.index)]
    remaining_for_parlay = remaining_for_parlay.sort_values(
        by="Model Edge", ascending=False
    )
    parlay_candidates = remaining_for_parlay.drop_duplicates(
        subset=["Player Name"], keep="first"
    ).head(parlay_bet_count)

    return straight_bets, parlay_candidates


def calculate_parlay_odds(bets):
    total_odds = 1
    for _, bet in bets.iterrows():
        odds = (
            bet["Odds for Over"]
            if bet["Prediction"] == "Over"
            else bet["Odds for Under"]
        )
        decimal_odds = odds / 100 + 1 if odds > 0 else -100 / odds + 1
        total_odds *= decimal_odds
    return total_odds


def main():
    file_path = "DataFrames/NN_Predictions_for_today.xlsx"
    all_bets = read_and_process_excel(file_path)

    daily_budget = 7
    parlay_budget = daily_budget * 0.3
    straight_bet_budget = daily_budget - parlay_budget

    straight_bets, parlay_candidates = select_straight_and_parlay_bets(all_bets, 5, 4)
    parlay_odds = calculate_parlay_odds(parlay_candidates)
    parlay_return = parlay_budget * (parlay_odds - 1)

    print("Selected Straight Bets:")
    print(
        straight_bets[
            [
                "Teams",
                "Player Name",
                "Bet Type",
                "Prediction",
                "Odds for Over",
                "Odds for Under",
                "Adjusted Confidence",
            ]
        ]
    )
    print(f"\nBudget per Straight Bet: {straight_bet_budget / len(straight_bets):.2f}")

    print("\nParlay Bet Candidates:")
    print(
        parlay_candidates[
            [
                "Teams",
                "Player Name",
                "Bet Type",
                "Prediction",
                "Odds for Over",
                "Odds for Under",
                "Adjusted Confidence",
            ]
        ]
    )
    print(f"Parlay Budget: {parlay_budget:.2f}")
    print(f"Expected Parlay Return (if successful): {parlay_return:.2f}")


if __name__ == "__main__":
    main()
