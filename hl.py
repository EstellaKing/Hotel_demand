#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import copy
import plotly.express as px

initial_data = pd.read_csv(r'C:\python\hotel_bookings.csv')


# In[2]:


initial_data.info()


# In[3]:


initial_data.head()


# In[4]:


initial_data.isnull().sum(axis=0)


# In[5]:


full_data_cln = copy.deepcopy(initial_data)


# In[6]:


nan_replacements = {"children:": 0.0,"country": "Unknown", "agent": 0, "company": 0}
full_data_cln = full_data_cln.fillna(nan_replacements)


# In[7]:


full_data_cln.isnull().sum()


# In[8]:


full_data_cln['meal'].replace('Undefined', 'SC', inplace = True)


# In[9]:


#去掉异常值
zero_guests = list(full_data_cln['adults']+full_data_cln['children']+full_data_cln['babies']==0)
full_data_cln.drop(full_data_cln.index[zero_guests], inplace=True)
full_data_cln.info()
full_data_cln.shape


# In[10]:


rh = full_data_cln.loc[(full_data_cln['hotel'] == 'Resort Hotel')&(full_data_cln['is_canceled'] == 0)]
ch = full_data_cln.loc[(full_data_cln['hotel'] == 'City Hotel')&(full_data_cln['is_canceled'] == 0)]


# In[11]:


#得出不同国家的顾客人数
country_data = pd.DataFrame(full_data_cln.loc[full_data_cln["is_canceled"] == 0]["country"].value_counts())
country_data.rename(columns={'country':'Number of Guests'}, inplace=True)
total_guests = country_data['Number of Guests'].sum()
country_data['Guests in %'] = round(country_data['Number of Guests']/total_guests*100, 2)
country_data['country'] = country_data.index
print(country_data)

# pie plot 制作饼图





fig = px.pie(country_data,
             values="Number of Guests",
             names="country",
             title="Home country of guests",
             template="seaborn")
fig.update_traces(textposition="inside", textinfo="value+percent+label")# textinfo饼图中显示的信息, textposition文字信息在里面
fig.show()


# In[12]:


# show on map  制作地图



guest_map = px.choropleth(country_data,
                    locations=country_data.index,
                    color=country_data["Guests in %"], 
                    hover_name=country_data.index, #悬停字段名字
                    color_continuous_scale=px.colors.sequential.Plasma,## 颜色变化
                    title="Home country of guests")
guest_map.show()


# In[13]:


#哪家酒店价格平均价格更高些？
rh['adr_pp'] = rh['adr']/(rh['adults']+rh['children'])
ch['adr_pp'] = ch['adr']/(ch['adults']+ch['children'])

print('''计入人数与餐饮得出的人均价格是
Resort hotel: {:.2f} € per night and person.
City hotel: {:.2f} € per night and person.'''.format(rh['adr_pp'].mean(), ch['adr_pp'].mean()))


# In[14]:


#标准化adr字段
full_data_cln['adr_pp'] = full_data_cln['adr']/(full_data_cln['adults']+full_data_cln['children'])
full_data_guests = full_data_cln.loc[full_data_cln['is_canceled']==0]
room_prices = full_data_guests[['hotel', 'reserved_room_type', 'adr_pp']].sort_values('reserved_room_type')#pandas中的sort_values()函数，可以将数据集依照某个字段中的数据进行排序，该函数即可根据指定列数据也可根据指定行的数据排序。
print(room_prices)


# In[15]:


#箱型图
plt.figure(figsize=(12,8))
sns.boxplot(x = 'reserved_room_type',
           y = 'adr_pp',
           hue = 'hotel',
           data = room_prices,
           hue_order = ['City Hotel', 'Resort Hotel'],
           fliersize=0)#hue列名，hue_order条形顺序，fliersize：float，用于指示离群值观察的标记大小，https://blog.csdn.net/qq_39949963/article/details/79387486




plt.title("Price of room types per night and person", fontsize=16)
plt.xlabel("Room type", fontsize=16)
plt.ylabel("Price [EUR]", fontsize=16)
plt.legend(loc="upper right")
plt.ylim(0,160)#设置y轴显示范围,https://blog.csdn.net/weixin_43964993/article/details/108305203?utm_medium=distribute.pc_aggpage_search_result.none-task-blog-2~aggregatepage~first_rank_v2~rank_aggregation-1-108305203.pc_agg_rank_aggregation&utm_term=plt%E8%AE%BE%E7%BD%AE%E5%9D%90%E6%A0%87%E8%8C%83%E5%9B%B4+python&spm=1000.2123.3001.4430
plt.show()


# In[16]:


# 一年中的过夜房价如何变动？
room_prices_monthly = full_data_guests[['hotel', 'arrival_date_month', 'adr_pp']].sort_values('arrival_date_month')
ordered_months = ["January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]
room_prices_monthly['arrival_date_month'] = pd.Categorical(room_prices_monthly['arrival_date_month'], categories=ordered_months, ordered = True)

#制作折线图
plt.figure(figsize=(12, 8))
sns.lineplot(x='arrival_date_month', y='adr_pp', hue='hotel', data=room_prices_monthly, hue_order=['City Hotel', 'Resort Hotel'],
            ci = 'sd', size="hotel", sizes = (2.5, 2.5))#size应该是根据什么调整折线的粗细

plt.title("Room price per night and person over the year", fontsize=16)
plt.xlabel("Month", fontsize=16)
plt.xticks(rotation=45)#rotation标签旋转角度
plt.ylabel("Price [EUR]", fontsize=16)
plt.show()


# In[17]:


resort_guests_monthly = rh.groupby('arrival_date_month')['hotel'].count()
city_guests_monthly = ch.groupby('arrival_date_month')['hotel'].count()

resort_guest_data = pd.DataFrame({'month':list(resort_guests_monthly.index), 'hotel':'Resort hotel', 'guests':list(resort_guests_monthly.values)})
city_guest_data = pd.DataFrame({"month": list(city_guests_monthly.index),
                    "hotel": "City hotel", 
                    "guests": list(city_guests_monthly.values)})
full_guest_data = pd.concat([resort_guest_data, city_guest_data], ignore_index=True)
#生成月份排序列表
ordered_months = ["January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]
full_guest_data["month"] = pd.Categorical(full_guest_data["month"], categories=ordered_months, ordered=True)

full_guest_data.loc[(full_guest_data['month'] == 'July')| (full_guest_data['month'] == 'August'),
                  'guests'] /= 3
full_guest_data.loc[~(full_guest_data['month'] == 'July') | (full_guest_data['month'] == 'August'),
                  'guests'] /= 3
#制作折线图
plt.figure(figsize=(12,8))
sns.lineplot(x = 'month', y = 'guests', hue = 'hotel', data=full_guest_data,
            hue_order = ['City hotel', 'Resort hotel'], size='hotel', sizes = (2.5, 2.5))
plt.title("Average number of hotel guests per month", fontsize=16)
plt.xlabel("Month", fontsize=16)
plt.xticks(rotation=45)
plt.ylabel("Number of guests", fontsize=16)
plt.show()


# In[18]:


#客人一般在酒店住多久
rh['total_nights'] = rh['stays_in_weekend_nights'] + rh['stays_in_week_nights']
ch['total_nights'] = ch['stays_in_weekend_nights'] + ch['stays_in_week_nights']

num_nights_res = list(rh['total_nights'].value_counts().index)
num_bookings_res = list(rh['total_nights'].value_counts())
rel_bookings_res = rh['total_nights'].value_counts()/sum(num_bookings_res) * 100

num_nights_cty =   list(ch["total_nights"].value_counts().index)
num_bookings_cty = list(ch["total_nights"].value_counts())
rel_bookings_cty =      ch["total_nights"].value_counts() / sum(num_bookings_cty) * 100 

res_nights = pd.DataFrame({'hotel':'Resort hotel',
                          'num_nights': num_nights_res,
                          'rel_num_bookings': rel_bookings_res})
cty_nights = pd.DataFrame({"hotel": "City hotel",
                           "num_nights": num_nights_cty,
                           "rel_num_bookings": rel_bookings_cty})

nights_data = pd.concat([res_nights, cty_nights], ignore_index=True)
plt.figure(figsize = (16, 8))
sns.barplot(x = 'num_nights', y = 'rel_num_bookings', hue = 'hotel', data = nights_data,
           hue_order = ['City hotel', 'Resort hotel'])
plt.title('Length of stay', fontsize = 16)
plt.xlabel('Number of nights', fontsize = 16)
plt.ylabel('Guests[%]', fontsize=16)
plt.legend(loc='upper right')
plt.xlim(0, 22)
plt.show()

avg_nights_res = sum(list((res_nights['num_nights'] * (res_nights['rel_num_bookings']/100)).values))
avg_nights_cty = sum(list((cty_nights["num_nights"] * (cty_nights["rel_num_bookings"]/100)).values))
print(f"On average, guests of the City hotel stay {avg_nights_cty:.2f} nights, and {cty_nights['num_nights'].max()}at maximum.")
print(f"On average, guests of the Resort hotel stay {avg_nights_res:.2f} nights, and {res_nights['num_nights'].max()} at maximum.")
#f""格式化必须用双引号


# In[19]:


#订单的市场渠道构成
segments = full_data_cln['market_segment'].value_counts()
#制作饼图
fig = px.pie(segments,
            values = segments.values,
            names = segments.index,
            title="Bookings per market segment",
            template="seaborn")
fig.update_traces(rotation=-90, textinfo="percent+label")
fig.show() 
#制作柱状图
plt.figure(figsize=(12, 8))
sns.barplot(x='market_segment',
           y='adr_pp',
           hue = 'reserved_room_type',
           data = full_data_cln,
           ci = 'sd',
            errwidth=1,
            capsize=0.1)# 误差棒边界横杠的厚度
plt.title("ADR by market segment and room type", fontsize=16)
plt.xlabel("Market segment", fontsize=16)
plt.xticks(rotation=45)
plt.ylabel("ADR per person [EUR]", fontsize=16)
plt.legend(loc="upper left")
plt.show()


# In[20]:


Airline_data = full_data_cln.loc[full_data_cln["market_segment"]== "Aviation"][["is_canceled",
                                                                                "adults",
                                                                                "lead_time",
                                                                                "adr_pp",]].describe()

Non_Airline_data = full_data_cln.loc[full_data_cln["market_segment"]!= "Aviation"][["is_canceled",
                                                                                    "adults",
                                                                                    "lead_time",
                                                                                    "adr_pp",]].describe()


# In[21]:


Airline_data = full_data_cln.loc[full_data_cln['market_segment']=='Aviation'][['is_canceled', 
                                                                               'adults', 
                                                                               'lead_time', 
                                                                               'adr_pp']].describe()
Non_Airline_data = full_data_cln.loc[full_data_cln['market_segment']!='Aviation'][['is_canceled', 
                                                                               'adults', 
                                                                               'lead_time', 
                                                                               'adr_pp']].describe()

print(Airline_data)
print(Non_Airline_data)


# In[22]:


#有多少订单被取消了
total_cancelations = full_data_cln['is_canceled'].sum()
rh_cancelations = full_data_cln.loc[full_data_cln['hotel']=='Resort Hotel']['is_canceled'].sum()
ch_cancelations = full_data_cln.loc[full_data_cln['hotel']=='City Hotel']['is_canceled'].sum()
#计算取消率
rel_cancel = total_cancelations/full_data_cln.shape[0]*100#hg.shape[0]返回的是hg的行数，有几行;hg.shape[1]返回的是hg的列数，有几列
rh_rel_cancel = rh_cancelations/full_data_cln.loc[full_data_cln['hotel'] == 'Resort Hotel'].shape[0]*100
ch_rel_cancel = ch_cancelations/full_data_cln.loc[full_data_cln['hotel'] == 'City Hotel'].shape[0]*100

print(f'Total bookings canceled: {total_cancelations:,} ({rel_cancel:.0f}%)')
print(f'Resort hotel bookings canceled: {rh_cancelations:,}({rh_rel_cancel:.0f}%)')
print(f'City hotel bookings canceled: {ch_cancelations:,}({ch_rel_cancel:.0f}%)')#:,以逗号分隔的数字格式


# In[23]:


# 哪些月份的取消率高
res_book_per_month = full_data_cln.loc[(full_data_cln["hotel"] == "Resort Hotel")].groupby("arrival_date_month")["hotel"].count()
res_cancel_per_month = full_data_cln.loc[(full_data_cln["hotel"] == "Resort Hotel")].groupby("arrival_date_month")["is_canceled"].sum()

cty_book_per_month = full_data_cln.loc[(full_data_cln["hotel"] == "City Hotel")].groupby("arrival_date_month")["hotel"].count()
cty_cancel_per_month = full_data_cln.loc[(full_data_cln["hotel"] == "City Hotel")].groupby("arrival_date_month")["is_canceled"].sum()

res_cancel_data = pd.DataFrame({"Hotel": "Resort Hotel",
                                "Month": list(res_book_per_month.index),
                                "Bookings": list(res_book_per_month.values),
                                "Cancelations": list(res_cancel_per_month.values)})
cty_cancel_data = pd.DataFrame({"Hotel": "City Hotel",
                                "Month": list(cty_book_per_month.index),
                                "Bookings": list(cty_book_per_month.values),
                                "Cancelations": list(cty_cancel_per_month.values)})

full_cancel_data = pd.concat([res_cancel_data, cty_cancel_data], ignore_index=True)
full_cancel_data["cancel_percent"] = full_cancel_data["Cancelations"] / full_cancel_data["Bookings"] * 100

#生成月份排序列表
ordered_months = ["January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]
full_cancel_data["Month"] = pd.Categorical(full_cancel_data["Month"], categories=ordered_months, ordered=True)#有些数据如果不规定排序，就会按照字母排序，所以要重新排序

# 制作柱状图
plt.figure(figsize=(12, 8))
sns.barplot(x = "Month", y = "cancel_percent" , hue="Hotel",
            hue_order = ["City Hotel", "Resort Hotel"], data=full_cancel_data)
plt.title("Cancelations per month", fontsize=16)
plt.xlabel("Month", fontsize=16)
plt.xticks(rotation=45)
plt.ylabel("Cancelations [%]", fontsize=16)
plt.legend(loc="upper right")
plt.show()


# In[24]:


#取消率预测
cancel_corr = initial_data.corr()['is_canceled']
cancel_corr = cancel_corr.abs().sort_values(ascending = False)[1:]
print(cancel_corr)


# In[ ]:




