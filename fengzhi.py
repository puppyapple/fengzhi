import tushare as ts
import pandas as pd 
import numpy as np 
from pandas import DataFrame
from sklearn import preprocessing
import sys

def grow_factor(end_year, season, num_year):
    '''
    计算成长因子
    '''
    # 成长因子：主营业务三年复合增长率，净利润三年复合增长率，内部收益率
    df_profit_old = ts.get_profit_data(end_year-num_year, season)[["name", "code", "roe", "business_income", "net_profits"]]
    df_profit_new = ts.get_profit_data(end_year, season)[["name", "code", "roe", "business_income", "net_profits"]]
    df_profit_old.columns = ["name", "code", "roe_old", "business_income_old", "net_profits_old"]
    df_profit_new.columns = ["name", "code", "roe_new", "business_income_new", "net_profits_new"]

    data = pd.merge(df_profit_new, df_profit_old, how='inner')

    # 去掉ST股
    data = data[data.name.map(lambda x: "ST" not in x)]

    # 去掉上市时间距今未满三年的股票
    #list_new_stocks = list(ts.new_stocks().code)
    #df_profit = df_profit[df_profit.name.map(lambda x: x not in list_new_stocks)]

    data["roe_rate"] = (data["roe_new"]/data["roe_old"])**(1.0/num_year) - 1
    data["bi_rate"] = (data["business_income_new"]/data["business_income_old"])**(1.0/num_year) - 1
    data["ne_rate"] = (data["net_profits_new"]/data["net_profits_old"])**(1.0/num_year) - 1
    return data[["name", "code", "roe_rate", "bi_rate", "ne_rate"]]

def value_factor(end_year, season):
    '''
    计算价值因子
    '''
    #价值因子：每股收益与价格比率、每股经营现金流与价格比率、每股净资产与价格比率、股息收益率
    df_report_new = ts.get_report_data(end_year, season)[["name", "code", "esp", "epcf", "bvps"]]
    df_new_price = ts.get_today_all()[["name", "code", "close"]]
    file = "2005_2011.csv" if end_year in range(2005,2012) else "2012_2018.csv"
    df_interest = pd.read_csv(file, header=True)["code", str(end_year)]
    df_interest.columns = ["code", "interest_rate"]
    data = pd.merge(df_report_new, df_new_price, how='inner')
    data = pd.merge(data, df_interest, how='inner')

    # 去掉ST股
    data = data[data.name.map(lambda x: "ST" not in x)]

    data["esp_rate"] = data["esp"]/data["close"]
    data["epcf_rate"] = data["epcf"]/data["close"]
    data["bvps_rate"] = data["bvps"]/data["close"]
    return data[["name", "code", "esp_rate", "epcf_rate", "bvps_rate", "interest_rate"]]

def process_data(df_grow, df_value):
    '''
    合并因子数据并作处理
    '''
    def extreme_cut(a,p,q) : return  p*(a<p) + q*(a>q) + a*((a<=q)&(a>=p))
    
    data = pd.merge(df_grow, df_value, how='inner')
    df_index = data[["code", "name"]]
    df_factor = data[["roe_rate", "bi_rate", "ne_rate", "esp_rate", "epcf_rate", "bvps_rate"]]
    quantile_05 = dict(df_factor.quantile(0.05))
    quantile_95 = dict(df_factor.quantile(0.95))

    #上下极值用0.05和0.95分位数替换
    df_factor = df_factor.apply(lambda x: extreme_cut(x, quantile_05[x.name], quantile_95[x.name]))
    
    #Z-score处理
    df_factor = DataFrame(preprocessing.scale(df_factor.values), index=df_factor.index, columns=df_factor.columns)
    final = pd.concat([df_index, df_factor])
    return final

def load_data(end_year, season, num_year):
    return process_data(grow_factor(end_year, season, num_year), value_factor(end_year, season))

test = load_data(2016, 4, 3)    
print(test)
    