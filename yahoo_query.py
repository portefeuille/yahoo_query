from yahooquery import Ticker
import json
import pandas as pd
import math
import sys

def getGrossProfit(ticker):
    data = ticker.income_statement()
    if isinstance(data, pd.DataFrame):
        lines = data.sort_values(by='asOfDate', ascending=False)
        for index, line in lines.iterrows():
            if hasattr(line, 'GrossProfit') and not math.isnan(line.GrossProfit):
                return {
                    "grossProfit": line.GrossProfit,
                    "grossProfitDate": line.asOfDate
                }
    return{}

def getBasicInfo(ticker,name):
    modules = 'assetProfile summaryDetail defaultKeyStatistics'
    data = ticker.get_modules(modules)
    res = {}
    if not isinstance(data[name], str):
        if 'assetProfile' in data[name] and 'sector' in data[name]['assetProfile']:
            res['sector']=data[name]['assetProfile']['sector']
        if 'summaryDetail' in data[name]:
            details = data[name]['summaryDetail']
            if 'beta' in details:
                res['beta']=details['beta']
            if 'marketCap' in details:
                res['marketCap']=details['marketCap']
            if 'averageVolume' in details:
                res['averageVolume']=details['averageVolume']
            if 'exDividendDate' in details:
                res['exDividendDate']=details['exDividendDate']
        if 'defaultKeyStatistics' in data[name] and 'priceToBook' in data[name]['defaultKeyStatistics']:
            res['priceToBook']=data[name]['defaultKeyStatistics']['priceToBook']
    return res

def getAnnualTotalAssets(ticker):
    res = {}
    mostRecentFound = False
    secondMostRecentFound = False
    data = ticker.balance_sheet()
    if isinstance(data, pd.DataFrame):
        lines = data.sort_values(by='asOfDate', ascending=False)
        for index, line in lines.iterrows():
            if not math.isnan(line.TotalAssets):
                if not mostRecentFound:
                    mostRecentFound = True
                    totalAssets = {
                        "totalAssetsAnnual": line.TotalAssets,
                        "totalAssetsAnnualDate": line.asOfDate
                    }
                    res = {**res, **totalAssets}
                elif not secondMostRecentFound:
                    secondMostRecentFound = True
                    totalAssets = {
                        "totalAssetsAnnualYearBefore": line.TotalAssets,
                        "totalAssetsAnnualYearBeforeDate": line.asOfDate
                    }
                    res = {**res, **totalAssets}
    return res

def getQuarterlyTotalAssets(ticker):
    data = ticker.balance_sheet(frequency='q')
    if isinstance(data, pd.DataFrame):
        lines = data.sort_values(by='asOfDate', ascending=False)
        for index, line in lines.iterrows():
            if not math.isnan(line.TotalAssets):
                return {
                    "totalAssetsQuarterly": line.TotalAssets,
                    "totalAssetsQuarterlyDate": line.asOfDate
                }
    return {}

def getMomentum(ticker):
    data = ticker.history(period='2y', interval='1wk', adj_ohlc=True)
    res = {}
    if isinstance(data, pd.DataFrame) and not data.empty:
        if hasattr(data, 'dividends'):
            data = data[(data.dividends==0)]
        if hasattr(data, 'splits'):
            data = data[(data.splits==0)]
        lines = data.sort_values('date', ascending=False)
        i = 0        
        for index, line in lines.iterrows():
            elem={}
            if i==4 :
                elem = {"oneMonthAgo":line.close, "oneMonthAgoDate":index[1]}
            elif i==(4+3*4) :
                elem = {"fourMonthAgo":line.close, "fourMonthAgoDate":index[1]}
            elif i==(4+6*4) :
                elem = {"sevenMonthAgo":line.close, "sevenMonthAgoDate":index[1]}
            elif i==(4+9*4) :
                elem = {"tenMonthAgo":line.close, "tenMonthAgoDate":index[1]}
            elif i==(4+12*4) :
                elem = {"thirteenMonthAgo":line.close, "thirteenMonthAgoDate":index[1]}
            res = {**res, **elem}
            i = i + 1
    return res  

if len(sys.argv) == 2:
    stock = Ticker(sys.argv[1])
    res = {}

    basicInfo = getBasicInfo(stock,sys.argv[1])
    res = {**res, **basicInfo}

    grossProfit = getGrossProfit(stock)
    res = {**res, **grossProfit}
    
    annualTotalAssets = getAnnualTotalAssets(stock)
    res = {**res, **annualTotalAssets}

    quarterlyTotalAssets = getQuarterlyTotalAssets(stock)
    res = {**res, **quarterlyTotalAssets}

    momentum = getMomentum(stock)
    res = {**res, **momentum}

    print(json.dumps(res, default=str))