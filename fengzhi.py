import tushare as ts
import pandas as pd 
import numpy as np 
import sys



def grow_factor(end_year,season,num_year):
    # 成长因子：主营业务三年复合增长率，净利润三年复合增长率，内部收益率
    df_profit_old = ts.get_profit_data(end_year-num_year,season)[["name","code","roe","business_income","net_profits"]]
    df_profit_new = ts.get_profit_data(end_year,season)[["name","code","roe","business_income","net_profits"]]
    df_profit_old.columns = ["name","code","roe_old","business_income_old","net_profits_old"]
    df_profit_new.columns = ["name","code","roe_new","business_income_new","net_profits_new"]

    data = pd.merge(df_profit_new, df_profit_old, how='inner')

    # 去掉ST股
    data = data[data.name.map(lambda x: "ST" not in x)]

    # 去掉上市时间距今未满三年的股票
    #list_new_stocks = list(ts.new_stocks().code)
    #df_profit = df_profit[df_profit.name.map(lambda x: x not in list_new_stocks)]

    data["roe_rate"] = (data["roe_new"]/data["roe_old"])**(1/3) - 1
    data["bi_rate"] = (data["business_income_new"]/data["business_income_old"])**(1/3) - 1
    data["ne_rate"] = (data["net_profits_new"]/data["net_profits_old"])**(1/3) - 1
    return data

