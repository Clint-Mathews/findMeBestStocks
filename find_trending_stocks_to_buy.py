from typing import Dict, List
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pprint
import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.auth import impersonated_credentials
import json
import gspread

# Load environment variables from .env file
load_dotenv()

def scrape_stock_recommendations() -> Dict[str, List[Dict[str, int]]]:
    url = 'https://www.moneycontrol.com/markets/stock-advice/'
    response = requests.get(url)
    period = ["1 Month", "3 Month", "6 Month", "1 Year", "All"]
    find_me_expert_option_on_stocks = {}

    if response.status_code == 200:
        soup_data = BeautifulSoup(response.content, 'html.parser')
    
        div_with_stock_recommendations = soup_data.find('div', class_='PL15 PR10 PT15')
        div_with_stock_recommendations_based_on_period = div_with_stock_recommendations.find_all('div', class_='equity1')
    
        for index, data_based_on_period in enumerate(div_with_stock_recommendations_based_on_period):

            consolidated_period_based_stock_info = []
            stock_data_found = data_based_on_period.find_all('tr')

            for stock_info in stock_data_found[2:]:
            
                stock_data = stock_info.find_all('td')
            
                if len(stock_data)==5:
                    
                    company = stock_data[0].find("a").get_text()
                    buy = stock_data[1].get_text()
                    sell = stock_data[2].get_text()
                    hold = stock_data[3].get_text()
                    total = stock_data[4].get_text()

                    consolidated_period_based_stock_info.append(
                        {
                            "company":company,
                            "buy":int(buy),
                            "sell":int(sell),
                            "hold":int(hold),
                            "total":int(total)
                        }
                    )
            find_me_expert_option_on_stocks[period[index]] = consolidated_period_based_stock_info
    return find_me_expert_option_on_stocks

def fead_stock_recommendations_to_google_sheet(stock_recommendations: Dict[str, List[Dict[str, int]]]):

    json_key = os.environ.get("GOOGLE_SHEETS_JSON_KEY")
    spreadsheet_title = os.environ.get("GOOGLE_SHEETS_TITLE")
    sheet_title = os.environ.get("GOOGLE_SHEETS_SHEET_TITLE")
    account = os.environ.get("GOOGLE_IMPERSONATED_ACCOUNT")
    target_scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    if not(json_key and spreadsheet_title and sheet_title):
        print("Please update env with required credentials!")
        return

    credentials = json.loads(json_key)
    client = gspread.service_account_from_dict(credentials)

    try:
        spreadsheet = client.open(spreadsheet_title)
    except gspread.SpreadsheetNotFound:
        print("Spreadsheet not found.")
        return
    
    try:
        sheet = spreadsheet.worksheet(sheet_title)
    except gspread.WorksheetNotFound:
        print("Worksheet not found.")
        return

    # Clear the existing data in the sheet (optional)
    sheet.clear()
    
    # Create a date based header
    date_header=["Date: {}".format(datetime.now().strftime("%Y-%m-%d"))]
    # Create header row
    header = ["Period", "Company", "Buy", "Sell", "Hold", "Total"]

    # Create a 2D array containing rows of data
    data_rows = [date_header, header]

    print("Spreadsheet found!")
    for period, stock_info in stock_recommendations.items():
        for stock_detail in stock_info:
            stock_info_row = [period, stock_detail['company'], stock_detail['buy'], stock_detail['sell'], stock_detail['hold'], stock_detail['total']]
            data_rows.append(stock_info_row)

    sheet.append_rows(data_rows)
    print("Spreadsheet updated!")
    pprint.pprint(stock_recommendations)

if __name__ == "__main__":
    stock_recommendations = scrape_stock_recommendations()
    fead_stock_recommendations_to_google_sheet(stock_recommendations)