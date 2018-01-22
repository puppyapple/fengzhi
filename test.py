import fengzhi_utils
import pandas as pd
from functools import reduce

def inner(df1, df2):
    return pd.merge(df1, df2, how='inner', on='code')

factors_by_year = {}
for i in range(2012, 2017):
    factors_by_year[i] = fengzhi_utils.load_data(i, 4, 3)

for key, value in factors_by_year.items():
    value["factor"] = 2 * (value.roe_rate + value.bi_rate + value.ne_rate) + (value.eps_rate + value.epcf_rate + value.bvps_rate + value.interest_rate)
    value.sort_values("factor", ascending=False)[0:500]
    #print(value)
    factors_by_year[key] = value

result = reduce(inner, list(factors_by_year.values()))
print(result)