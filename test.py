import pandas as pd
from imp import reload
import datetime
import fengzhi_utils
reload(fengzhi_utils)
from functools import reduce

def inner(df1, df2):
    return pd.merge(df1, df2, how='inner', on=['code', 'name'])

factors_by_year = {}
start = 2016
end = 2017
today = datetime.datetime.now().strftime('%Y-%m-%d')
start_date = str(start) + '-04-30'
for i in range(start, end):
    factors_by_year[i] = fengzhi_utils.load_data(i, 4, 3)

for key, value in factors_by_year.items():
    value["factor"] = 2 * (value.roe_rate + value.bi_rate + value.ne_rate) + (value.eps_rate + value.epcf_rate + value.bvps_rate + value.interest_rate)
    value = value.sort_values("factor", ascending=False)[0:500]
    #print(value)
    factors_by_year[key] = value

result = reduce(inner, list(factors_by_year.values()))
#result['original_price'] = result.code.apply(lambda x: fengzhi_utils.get_day_close(x, 'close', start_date))
#result['now_price'] = result.code.apply(lambda x: fengzhi_utils.get_day_close(x, 'close', today))
#result['increase_ratio'] = (result['now_price'] - result['original_price'])/result['original_price']
print(result)
#result.to_csv("result.csv")
writer = pd.ExcelWriter(str(end-start) + '_output.xlsx')
result.to_excel(writer,'Sheet1')
writer.save()
