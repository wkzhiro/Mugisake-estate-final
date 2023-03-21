import streamlit as st
import numpy as np

# #Googleスプレッドシートからデータ取得し格納(元)
# import pandas as pd
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# from gspread_dataframe import get_as_dataframe
# import os

# scope =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# creds = ServiceAccountCredentials.from_json_keyfile_name('grspread_key_mugisake.json', scope)
# client = gspread.authorize(creds)

# sheet = client.open("Mugisake_KA01").worksheet('sheet5')
# df = get_as_dataframe(sheet)

# #Googleスプレッドシートからデータ取得し格納(Streamlitデプロイ用)
# from google.oauth2 import service_account
# import gspread
# import pandas as pd
# # スプレッドシートの認証
# scopes = [ 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'
# ]
# credentials = service_account.Credentials.from_service_account_info( st.secrets["gcp_service_account"], scopes=scopes
# )
# gc = gspread.authorize(credentials)
# # スプレッドシートからデータ取得
# SP_SHEET_KEY = st.secrets.SP_SHEET_KEY.key # スプレッドシートのキー
# sh = gc.open_by_key(SP_SHEET_KEY)
# SP_SHEET = 'sheet5' # シート名「シート1」を指定
# worksheet = sh.worksheet(SP_SHEET)
# data = worksheet.get_all_values() # シート内の全データを取得
# df = pd.DataFrame(data[1:], columns=data[0]) # 取得したデータをデータフレームに変換
# st.table(df[:3])

#Googleスプレッドシートからデータ取得し格納(Streamlitデプロイ用2)
from google.oauth2 import service_account
from gsheetsdb import connect
import pandas as pd
# Create a connection object.
credentials = service_account.Credentials.from_service_account_info( st.secrets["gcp_service_account"], scopes=[ "https://www.googleapis.com/auth/spreadsheets", ],
)
conn = connect(credentials=credentials)
def run_query(query):
    rows = conn.execute(query, headers=1)
    return rows
sheet_url = st.secrets["private_gsheets_url"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')
# データフレームに変換し表示する
row_list = []
for row in rows: row_list.append(row)
df=pd.DataFrame(row_list)



#------------------------page-Main------------------------

st.set_page_config(page_title="物件アプリby麦酒の一味", page_icon="👒")
st.title('お得な物件探せ〜る＆勝手に通知く〜る')


#データの洗浄
NaN_dell_column = ["name","price","address","layout","age","area","traffic_tx"] #欠損値の削除
df = df.dropna(subset = NaN_dell_column,axis = 0)

df["price"] = df["price"]/10000 #価格を（万円）に変更
df['station'] = df['traffic_tx'].str.split(pat='「',expand=True)[1].str.split(pat='」',expand=True)[0] #駅名取得
df['name'] = df['name'].str.replace('【マンション】','')
df['layout'] = df['layout'].str.replace('（納戸）','')

int_convert_column = ["level_0","price","age","area","floor","time_walk"] #整数型に変換
df[int_convert_column] = df[int_convert_column].astype('int')



#------------------------page-Main-sidebar------------------------

st.sidebar.write('### 絞り込み条件')

# 駅名でフィルター
column_station = 'station'
station_list = list(df[column_station].unique())
selected_station = st.sidebar.multiselect('駅名でフィルター', station_list, default = '北千住')
df = df[(df[column_station].isin(selected_station))]

if df.empty:
    st.write("!!駅名が選択されていません")
else:
    # 価格でフィルター
    column_filter = 'price'
    max_value = int(df[column_filter].max())
    min_value = int(df[column_filter].min())
    slider = st.sidebar.slider('価格(万円)でフィルター', min_value, max_value, max_value, None)
    df = df[df[column_filter] <= slider]

    # 広さでフィルター
    column_filter = 'area'
    max_value = int(df[column_filter].max())
    min_value = int(df[column_filter].min())
    slider = st.sidebar.slider('広さ(m2)でフィルター', min_value, max_value, max_value, None)
    df = df[df[column_filter] <= slider]

    # 築年でフィルター
    column_filter = 'age'
    max_value = int(df[column_filter].max())
    min_value = int(df[column_filter].min())
    slider = st.sidebar.slider('築年(年)でフィルター', min_value, max_value, max_value, None)
    df = df[df[column_filter] <= slider]

    # 最寄駅からの時間でフィルター
    column_filter = 'time_walk'
    max_value = int(df[column_filter].max())
    min_value = int(df[column_filter].min())
    slider = st.sidebar.slider('最寄駅からの徒歩時間(分)でフィルター', min_value, max_value, max_value, None)
    df = df[df[column_filter] <= slider]



#------------------------page-Main------------------------


    st.write('### 物件リスト')
    #表の表示
    df_main = df.reindex(columns=['name','price','layout','area','floor','age','station','time_walk','url']) #表示する列の指定
    df_main = df_main.set_axis(["マンション名","価格(万円)","間取り","面積(m2)","階数","築年","最寄駅","徒歩分数","suumo Link"],axis=1) #列名の変更
    st.dataframe(df_main, width=2000,height=500)

    st.write('### 物件マップ')
    #地図の表示
    import folium
    from streamlit_folium import folium_static
    from folium.plugins import MarkerCluster

    # 緯度と経度の平均値を計算する
    center_lat = np.mean(df['Ido'])
    center_lon = np.mean(df['Keido'])
    # 地図を作成する
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    # MarkerClusterを作成する
    marker_cluster = MarkerCluster().add_to(m)
    # マーカーを追加する
    for index, row in df.iterrows():
        # ポップアップの内容を設定する
        popup_text = f'<table><tr><td>物件ID：</td><td>{row["level_0"]}</td></tr>' + \
                    f'<tr><td>マンション名：</td><td>{row["name"]}</td></tr>' + \
                    f'<tr><td>価格(万円)：</td><td>{row["price"]}</td></tr></table>'
        marker = folium.Marker(location=[row['Ido'], row['Keido']], popup=f'<div style="width: 400px; font-size: 10pt;">{popup_text}</div>').add_to(m)
            # MarkerClusterに追加する
        marker_cluster.add_child(marker)    
    # マップを自動的にズームする
    m.fit_bounds(marker_cluster.get_bounds())
    # 地図情報を表示
    folium_static(m)
