import streamlit as st
import yfinance as yf
import csv
import requests
import pandas as pd
import time
from st_aggrid import AgGrid


def get_data(url):
    r = requests.get(url)
    data = r.json()
    quarterlydata = data['quarterlyEarnings']
    latestdata = quarterlydata[0]
    latestreported = latestdata['reportedDate']
    surprisepercentage = float(latestdata['surprisePercentage'])
    return data, latestreported, surprisepercentage
    

keys = ["5TO1LWG9QMERUK3S", "YCZL8A385TIETXH8", "UDDPGI2OD5ZCE3XM", "9FP3024TWMWXAZUK", "JSKI1K4SDKDAFTM7", "TZOR3BHNX5KDHPI7", "K6M8QX9ET7BC6BQY", "DT3F91MQ8YQ2OZA5",
"MJHHMVIVN78KNE3S", "GAB8U42951A9240U",  "Y5PIVYW8480EF4KD", "3L3IT72L1N6HCJHX", "XMN8AKGRWB5PFDSC", "JT2M4TFYTQ3HQ17K", "N4OCLJFH7JG6L41R", "78X2RG0DZ8338BX0",
"9690NSYZL347GGZ2", "QYX25OJG88FQTMEV", "ZL9CMLKWNI7I9MTO"]

@st.cache_data
def load_data(keys, CSV_URL):
    with requests.Session() as s:
        download = s.get(CSV_URL)
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        companies = list(cr)
        missingtickers = []
        missingvalues = []
        finallist = []
        missingquarterlydata = []
        i = 0
        for row in companies:
            if row[5] != 'USD':
                continue
            else: 
                try:
                    tickerSymbol = row[0]
                    estimate = float(row[4])
                    try:
                        tickerData = yf.Ticker(tickerSymbol)
                        todays_data = tickerData.history(period='1d')
                        price = todays_data['Close'][0]
                        estimatedpercentage = estimate/price
                        row.append(estimatedpercentage)
                        del row[5]
                        del row[4]
                        del row[3]
                        try:
                            url = f'https://www.alphavantage.co/query?function=EARNINGS&symbol={tickerSymbol}&apikey={keys[i]}'
                            data, latestreported, surprisepercentage = get_data(url)
                            row.append(latestreported)
                            row.append(surprisepercentage)
                            finallist.append(row)
                        except: 
                            try:
                                error = data['Note']
                                i += 1
                                url = f'https://www.alphavantage.co/query?function=EARNINGS&symbol={tickerSymbol}&apikey={keys[i]}'
                                data, latestreported, surprisepercentage = get_data(url)
                                row.append(latestreported)
                                row.append(surprisepercentage)
                                finallist.append(row)
                            except:    
                                missingquarterlydata.append(tickerSymbol)
                    except:
                        missingtickers.append(tickerSymbol)
                except ValueError:
                    estimatedpercentage = None
                    missingvalues.append(tickerSymbol)

        header = ["Symbol", "Company", "Next Reporting Date", "Estimated Earnings Percentage", "Latest Reporting Date", "Surprise Percentage"]
        df = pd.DataFrame(finallist, columns=header)

        return df, missingvalues, missingtickers, missingquarterlydata
    

CSV_URL = 'https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&horizon=3month&apikey=5TO1LWG9QMERUK3S'
df, missingvalues, missingtickers, missingquarterlydata = load_data(keys, CSV_URL)
st.title("Estimated and Surprise Earning Percentage App")

st.markdown("""
This app ranks the top n number of US listed companies based on Estimated and Surprise Earning Percentage.
The Estimated Earning Percentage is calculated using the Estimated Earnings divided by Current Share Price.
Data is collected from: 
1. Estimated Earnings per Share: https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&horizon=3month&apikey=5TO1LWG9QMERUK3S 
2. Current Share Price: YahooFinance 
3. Surprise Earning Percentage: https://www.alphavantage.co/query?function=EARNINGS&symbol={tickerSymbol}&apikey=5TO1LWG9QMERUK3S
""")
            
st.sidebar.header("User Input Features")
number = st.sidebar.selectbox("Ranking Based on Top", list(reversed(range(1,len(df)+1))))
criteriaoptions = ["Estimated Earnings Percentage", "Surprise Percentage"]
criteria = st.sidebar.selectbox("Criteria", criteriaoptions)
if criteria == "Estimated Earnings Percentage":
    df.sort_values(by = "Estimated Earnings Percentage", ascending = False, inplace = True)
elif criteria == "Surprise Percentage":
    df.sort_values(by = "Surprise Percentage", ascending = False, inplace = True )

st.markdown("The following tickers could not be found on YahooFinance and may have been delisted:")
st.markdown(missingtickers)

st.markdown("The following tickers have no estimated earnings listed")
st.markdown(missingvalues)

st.markdown("The following tickers have no quarterly earnings listed")
st.markdown(missingquarterlydata)

st.subheader(f"Table of Tickers with Top {number} Companies with Highest{criteria} Ranked ")
AgGrid(df[1:number+1])