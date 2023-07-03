import requests

url = 'https://www.alphavantage.co/query?function=EARNINGS&symbol=IBM&apikey=demo'
r = requests.get(url)
data = r.json()
quarterlydata = data['quarterlyEarnings']
latestdata = quarterlydata[0]
latestreported = latestdata['reportedDate']
surprisepercentage = latestdata['surprisePercentage']

print(latestdata)
print(surprisepercentage)