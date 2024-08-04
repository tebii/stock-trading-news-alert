import requests
from datetime import datetime, timedelta
from twilio.rest import Client
import os

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

twilio_phone = os.environ.get("TWILIO_PHONE")
my_phone = os.environ.get("PHONE")
account_sid = os.environ.get("TWILIO_SSID")
auth_token = os.environ.get("TWILIO_AUTH")
stock_api = os.environ.get("STOCK_API")
news_api = os.environ.get("NEWS_API")

stock_params = {
    "function" : "TIME_SERIES_DAILY",
    "symbol" : STOCK_NAME,
    "apikey" : stock_api,
}

stock_response = requests.get(STOCK_ENDPOINT, params=stock_params)
stock_response.raise_for_status()
stock_data = stock_response.json()
last_refresh = stock_data["Meta Data"]["3. Last Refreshed"]
yesterday = datetime.strptime(last_refresh, '%Y-%m-%d') - timedelta(1)
b4yest = yesterday - timedelta(1)

#convert to string
yesterday = datetime.strftime(yesterday, "%Y-%m-%d")
b4yest = datetime.strftime(b4yest, "%Y-%m-%d")

yest_stock_price = stock_data["Time Series (Daily)"][yesterday]["4. close"]
b4yest_stock_price = stock_data["Time Series (Daily)"][b4yest]["4. close"]

diff = abs(float(yest_stock_price) - float(b4yest_stock_price))
is_pos = yest_stock_price > b4yest_stock_price
perc_diff = diff / ((float(yest_stock_price) + float(b4yest_stock_price)) / 2 ) * 100

get_news = False
if perc_diff > 5:
    get_news = True 

news_params = {
    "q" : COMPANY_NAME,
    "from" : yesterday,
    "sortBy" : "popularity",
    "apiKey" : news_api,
}

if is_pos:
    stock_str = STOCK_NAME + " 🔺" + perc_diff + "\n"
else:
    stock_str = STOCK_NAME + " 🔻" + perc_diff + "\n"

news_response = requests.get(NEWS_ENDPOINT, news_params)
news_data = news_response.json()
news_slice = slice(3)
news = news_data["articles"][news_slice]

if get_news: 
    for article in news:
        news_message = stock_str + "Headline: " + article["title"] + '\nBrief: ' + article["description"] + '\n'
        client = Client(account_sid, auth_token)
        message = client.messages.create(
                body=news_message,
                from_=twilio_phone,
                to=my_phone,
        )


