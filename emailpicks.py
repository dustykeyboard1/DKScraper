import pandas as pd
import smtplib
from email.message import EmailMessage
import mimetypes


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
        df["Bet Type"] = sheet_name
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
    df_unique = df.sort_values(by="Model Edge", ascending=False).drop_duplicates(
        subset=["Player Name", "Bet Type"], keep="first"
    )
    straight_bets = df_unique.head(straight_bet_count)
    remaining_for_parlay = df_unique[~df_unique.index.isin(straight_bets.index)]
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


def send_email_with_attachment(
    subject, body, attachment_path, receiver, sender, password
):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content(body)

    mime_type, _ = mimetypes.guess_type(attachment_path)
    mime_type, mime_subtype = mime_type.split("/")

    with open(attachment_path, "rb") as file:
        file_content = file.read()
        msg.add_attachment(
            file_content,
            maintype=mime_type,
            subtype=mime_subtype,
            filename=attachment_path,
        )

    with smtplib.SMTP("smtp-mail.outlook.com", port=587) as smtp:
        smtp.starttls()
        smtp.login(sender, password)
        smtp.send_message(msg)
        print("Email Sent!")


def main():
    file_path = "DataFrames/NN_Predictions_for_today.xlsx"
    all_bets = read_and_process_excel(file_path)

    daily_budget = 20  # Define the daily budget for betting
    parlay_budget = daily_budget * 0.3  # 30% of the daily budget goes to parlay bets
    straight_bet_budget = daily_budget - parlay_budget  # The rest goes to straight bets

    straight_bets, parlay_candidates = select_straight_and_parlay_bets(all_bets, 5, 4)
    parlay_odds = calculate_parlay_odds(parlay_candidates)
    parlay_return = parlay_budget * (
        parlay_odds - 1
    )  # Calculate potential return from parlay bets

    # Prepare the email content
    email_subject = "Today's Betting Picks"
    email_body = "Selected Straight Bets:\n"
    email_body += straight_bets[
        [
            "Teams",
            "Player Name",
            "Bet Type",
            "Prediction",
            "Odds for Over",
            "Odds for Under",
            "Adjusted Confidence",
        ]
    ].to_string(index=False)
    email_body += (
        f"\n\nBudget per Straight Bet: {straight_bet_budget / len(straight_bets):.2f}\n"
    )
    email_body += "\nParlay Bet Candidates:\n"
    email_body += parlay_candidates[
        [
            "Teams",
            "Player Name",
            "Bet Type",
            "Prediction",
            "Odds for Over",
            "Odds for Under",
            "Adjusted Confidence",
        ]
    ].to_string(index=False)
    email_body += f"\nParlay Budget: {parlay_budget:.2f}\n"
    email_body += f"Expected Parlay Return (if successful): {parlay_return:.2f}"

    send_email_with_attachment(
        subject=email_subject,
        body=email_body,
        attachment_path=file_path,
        receiver="mikesyanks02@icloud.com",
        sender="michael.scoleri@outlook.com",
        password="Has2sister$",  # Remember to replace with your actual password
    )


if __name__ == "__main__":
    main()
