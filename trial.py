import streamlit as st
import yfinance as yf
import csv
import requests
import pandas as pd
from st_aggrid import AgGrid

@st.cache_data
def load_data(CSV_URL):
    with requests.Session() as s:
        download = s.get(CSV_URL)
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        companies = list(cr)
        missingtickers = []
        missingvalues = []
        finallist = []
        missingquarterlydata = []
        for row in companies[:100]:
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
                            url = f'https://www.alphavantage.co/query?function=EARNINGS&symbol={tickerSymbol}&apikey=5TO1LWG9QMERUK3S'
                            r = requests.get(url)
                            data = r.json()
                            quarterlydata = data['quarterlyEarnings']
                            latestdata = quarterlydata[0]
                            latestreported = latestdata['reportedDate']
                            surprisepercentage = float(latestdata['surprisePercentage'])
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
df, missingvalues, missingtickers, missingquarterlydata = load_data(CSV_URL)
st.title("Estimated and Surprise Earning Percentage App")

st.markdown("""
This app ranks the top n number of US listed companies in terms of Estimated and Surprise Earning Percentage.
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

AgGrid(df[1:number+1])