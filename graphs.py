from dependencies import *
cpidata = pd.read_excel('cpidata.xls',sheet_name='Sheet2')

a = pd.read_stata('table2_1.dta')
b = pd.read_stata('table2_2.dta')
c = pd.read_stata('table3.dta')
d = pd.read_stata('table4.dta')

data = pd.read_stata('table2_1.dta')
data = data.merge(pd.read_stata('table2_2.dta'),on=['month','year','type_fund'])
data = data.merge(pd.read_stata('table3.dta'),on=['month','year','type_fund'])
data = data.merge(pd.read_stata('table4.dta'),on=['month','year','type_fund'])

data['month'] = ['January' if x == 'Janurary' else x for x in data['month']]
data['monthyear'] = [a+str(b) for a,b in zip(data['month'].values,data['year'].values)]
data['date'] = pd.to_datetime(data['monthyear'],infer_datetime_format=True)

data = data.merge(cpidata,on=['date'])
data = data.sort_values(['date','type_fund'])

money_vars = ['new_open_amt', 'new_closed_amt', 'new_interval_amt', 'new_assured_amt', 'exi_open_amt', 'exi_closed_amt', 'exi_interval_amt', 'exi_assured_amt', 'open_red', 'closed_red', 'interval_red', 'assured_re', 'open_aum', 'closed_aum', 'interval_aum', 'assured_aum']

data['new_open_amt'] = data['new_open_amt'].fillna(1)

a1 = [x and y for x,y in zip(data['date'] == 'January2008',data['type_fund'] == 2)]
a2 = [x and y for x,y in zip(data['date'] > 'January2008',data['type_fund'] == 2)]
closednumsum = np.sum(data.loc[a2]['new_closed_no'])
#print('Adding closed num sum', closednumsum)
data.loc[a1,'new_closed_no'] += closednumsum
data.loc[a2,'new_closed_no'] = 0
closedamtsum = np.sum(data.loc[a2]['new_closed_amt'])
#print('Adding closed Amount sum', closedamtsum)
data.loc[a1,'new_closed_amt'] += 4656.147
#data.loc[a1,'new_closed_amt'] += closedamtsum
data.loc[a2,'new_closed_amt'] = 0


for mvar in money_vars:
    data[mvar] = ((data[mvar]/data['cpi9'])*10)/(46.235)

    
data['net_exi_open_amt'] = data['new_open_amt'].values + data['exi_open_amt'].values - data['open_red'].values
data['net_exi_closed_amt'] = data['new_closed_amt'].values + data['exi_closed_amt'].values - data['closed_red'].values

data['equity'] = 0
data.loc[(data['type_fund'] == 2).values + (data['type_fund'] == 3).values + (data['type_fund'] == 6).values,'equity']  = 1
dataequity = data[(data['equity']==1)]

import matplotlib.pyplot as plt


temp = dataequity.groupby('date').sum()[['new_open_no','new_closed_no']]
temp = temp.reset_index()
x1 = (temp['date'] == '2006-05-01').idxmax()
x2 = (temp['date'] == '2008-02-01').idxmax()
plt.bar(range(len(temp)),-temp['new_open_no'].values,color='g',linestyle='-',linewidth=2,label='Open End Starts')
plt.bar(range(len(temp)), temp['new_closed_no'].values,color='b',linestyle='-',linewidth=2,label='Closed End Starts')
plt.axvline(x=x1,color='r',linestyle='--')
plt.axvline(x=x2,color='r',linestyle='--')
plt.axhline(0,color='black',linestyle='-')
plt.legend(loc='best')
plt.xlabel('Timeline')
plt.ylabel('Number of new funds')
plt.show()


temp = dataequity.groupby('date').sum()[['net_exi_open_amt','net_exi_closed_amt']]
temp = temp.reset_index()
x1 = (temp['date'] == '2006-05-01').idxmax()
x2 = (temp['date'] == '2008-02-01').idxmax()
plt.bar(range(len(temp)),-temp['net_exi_open_amt'].values,color='g',linestyle='-',linewidth=2,label='Open End Flows')
plt.bar(range(len(temp)), temp['net_exi_closed_amt'].values,color='b',linestyle='-',linewidth=2,label='Closed End Flows')
plt.axvline(x=x1,color='r',linestyle='--')
plt.axvline(x=x2,color='r',linestyle='--')
plt.axhline(0,color='black',linestyle='-')
plt.legend(loc='best')
plt.xlabel('Timeline')
plt.ylabel('Net flow into equity funds')
plt.show()