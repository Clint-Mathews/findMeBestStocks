from typing import Dict, List
import requests
from bs4 import BeautifulSoup
import pprint

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

def fead_stock_recommendations_to_google_docs():
    return

if __name__ == "__main__":
    stock_recommendations = scrape_stock_recommendations()
    pprint.pprint(stock_recommendations)