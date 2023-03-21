# スプレッドシートからデータ取得
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 過去スプレッドシートの複製
def duplicate_sheet(origin_sheet_name, new_sheet_name):
    SS_ID = '1K2b_HpACFq107BRrMEQdRDMidRw78x3-5oBqkwINBEU'
    scope =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # Credentials 情報を取得
    credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    #OAuth2のクレデンシャルを使用してGoogleAPIにログイン
    gc = gspread.authorize(credentials)

    # シートを複製
    wb = gc.open_by_key(SS_ID)
    sheet_id = wb.worksheet(origin_sheet_name).id
    sheet = wb.duplicate_sheet(source_sheet_id = sheet_id, new_sheet_name = new_sheet_name, insert_sheet_index = 3)

    return sheet

origin_sheet_name = 'sheet2'
new_sheet_name = 'sheet2-1'
new_sheet = duplicate_sheet(origin_sheet_name, new_sheet_name)

#データの取得
def get_spreadsheet_as_df(SHEET_NAME):
    SS_ID = '1K2b_HpACFq107BRrMEQdRDMidRw78x3-5oBqkwINBEU'
    scope =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # Credentials 情報を取得
    credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    #OAuth2のクレデンシャルを使用してGoogleAPIにログイン
    gc = gspread.authorize(credentials)
    # IDを指定して、Googleスプレッドシートのワークブックを選択する
    workbook = gc.open_by_key(SS_ID)
    # シート名を指定して、ワークシートを選択
    worksheet = workbook.worksheet(SHEET_NAME)
    # スプレッドシートをDataFrameに取り込む
    df = pd.DataFrame(worksheet.get_all_values()[1:], columns=worksheet.get_all_values()[0])
    return df

df = get_spreadsheet_as_df('sheet1')
df2 = get_spreadsheet_as_df(new_sheet_name)

#緯度経度取得
import urllib
import requests

IdoKeido = []
for Address in df['address']:
    makeUrl = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="
    s_quote = urllib.parse.quote(Address)
    response = response = requests.get(makeUrl + s_quote)
    IdoKeido.append(response.json()[0]["geometry"]["coordinates"])

df['Keido'] = [x[0] for x in IdoKeido]
df['Ido'] = [x[1] for x in IdoKeido]


#trafficデータの処理
import re
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
df["age_fl"] = df["age"].str[:4].replace("-","0").astype(float)
df["reform_fl"] = df["reform"].str[:4].replace("-","0").astype(float)
df["date"] = '更新失敗'

# dateの挿入
import datetime
#指定の列をキーにして新しくデータに入ったindexを検出する
col = 'url'
df_index = df[~df[col].isin(df2[col])].index
#カレンダーのフォーマット指定して本日の日付を取得
date_format = '%Y/%m/%d'
today = datetime.datetime.now().strftime(date_format)
#差分のみ日付を変更する
for i, row in df.iterrows():
    if i in df_index:
        df.loc[i, 'date'] = today
    # else:
        # indices = df2.index[df2[col].isin([df.loc[i, col]])]
        # df.loc[i, 'date'] = df2.loc[indices,'date'][2]

    


#スプレッドシートに戻す
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

# use creds to create a client to interact with the Google Drive API
scope =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

sheet = client.open("Mugisake_KA01").worksheet("sheet2")
set_with_dataframe(sheet, df.reset_index())
list_of_hashes = sheet.get_all_records()
print(list_of_hashes)

