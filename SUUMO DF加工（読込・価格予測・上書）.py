import pandas as pd
import numpy as np
import re
from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import json
import gspread
import pickle
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe
from gspread_dataframe import set_with_dataframe

## Googleスプレッドシートからデータ取得し格納
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe
scope =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('grspread_key_mugisake.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Mugisake_KA01").worksheet('sheet2')
df = get_as_dataframe(sheet)
df2 = get_as_dataframe(sheet)

if_null_dell_column = ["name","price","address","layout","age","area","traffic_tx"]
df = df.dropna(subset=if_null_dell_column,axis = 0)

def get_station_info(item):
  dict = {}   
  if re.findall('バス',item) == ['バス']:
    dict["station"] = item.split('「')[1].split('」')[0]
    dict["time_walk"] = item.split('」')[1].split('歩')[1].split('分')[0]
    dict["time_bus"] = item.split('」')[1].split('バス')[1].split('分')[0]
  elif re.findall('km',item) == ['km']:
    dict["station"] = item.split('「')[1].split('」')[0]
    dict["time_walk"] = 0
    dict["time_bus"] = float(item.split('」')[1].split('車')[1].split('km')[0])/20*60
  else:
    dict["station"] = item.split('「')[1].split('」')[0]
    dict["time_walk"] = item.split('」')[1].split('歩')[1].split('分')[0]
    dict["time_bus"] = 0
  return dict

df["train_station"] = df["traffic_tx"].apply(lambda x :get_station_info(x)["station"])
df["time_walk"] = df["traffic_tx"].apply(lambda x :get_station_info(x)["time_walk"]).astype(float)
df["time_bus"] = df["traffic_tx"].apply(lambda x :get_station_info(x)["time_bus"]).astype(float)
df["age"] = df["age"].str[:4].replace("-","0").astype(float)
df["reform"] = df["reform"].str[:4].replace("-","0").astype(float)

def cal_room_num(text,s=0.5):
    if text.find("ワンルーム") >= 0:
        if text.find("S") >= 0:
            return 1+s
        else:
            return 1
    if text.find("1K") >= 0:
        if text.find("S") >= 0:
            return 1+s
        else:
            return 1
    if text.find("S") >=0:
        return int(re.sub(r'[^0-9]','',text))+1+s

    if text.find("2S") >=0:
        return int(re.sub(r'[^0-9]','',text))+2+s

    if text.find("3S") >=0:
        return int(re.sub(r'[^0-9]','',text))+3+s

    else:
        return int(re.sub(r'[^0-9]','',text))+1

df["room_num"] = df["layout"].apply(lambda x :cal_room_num(x))

def land_price(text):
    if text.find("秋葉原")>=0:
        return 742.9
    elif text.find("新御徒町")>=0:
        return 441
    elif text.find("浅草")>=0:
        return 390.3
    elif text.find("本所吾妻橋")>=0:
        return 90
    elif text.find("蔵前")>=0:
        return 103
    elif text.find("南千住")>=0:
        return 218.6
    elif text.find("北千住")>=0:
        return 238.7
    elif text.find("青井")>=0:
        return 164.4
    elif text.find("六町")>=0:
        return 127.8
    elif text.find("八潮")>=0:
        return 77.8
    elif text.find("三郷中央")>=0:
        return 50.9
    elif text.find("南流山")>=0:
        return 62.9
    elif text.find("流山セントラルパーク")>=0:
        return 60.1
    elif text.find("流山おおたかの森")>=0:
        return 81
    elif text.find("柏の葉キャンパス")>=0:
        return 60.1
    elif text.find("柏たなか")>=0:
        return 56.5
    elif text.find("守谷")>=0:
        return 41.2
    else:
        return 100
df["train_station_price"] = df["train_station"].apply(lambda x: land_price(x)).astype(float)

def direction_price(text):
    if text.find("南")>=0:
        return 1
    if text.find("東")>=0:
        return 0.95
    if text.find("西")>=0:
        return 0.95
    if text.find("北")>=0:
        return 0.90
df["direction_price"] = df["direction"].apply(lambda x: direction_price(x)).astype(float)

x = df.loc[:,['price_kanri','price_tsumitate','age','floor','time_walk','time_bus','room_num','train_station_price','direction_price']]
with open('SUUMO_random_forest_regressor_model.pkl','rb') as f:
    model = pickle.load(f)
df['predicted_price'] = model.predict(x).astype(int)
df['discounted_price'] = (df['predicted_price']-df['price']).astype(int)

df3 = pd.concat([df2,df['predicted_price'],df['discounted_price']],axis=1)
drop_column = ['Unnamed: 25']
df3 = df3.drop(drop_column,axis = 1)

sheet3 = client.open("Mugisake_KA01").worksheet('sheet3')
set_with_dataframe(sheet3,df3)