import streamlit as st
import numpy as np
from datetime import datetime

# # Googleスプレッドシートからデータ取得し格納
# import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
# scope =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# creds = ServiceAccountCredentials.from_json_keyfile_name('grspread_key_mugisake.json', scope)
# client = gspread.authorize(creds)

# sheet = client.open("Mugisake_KA01").worksheet('sheet5')
# df = get_as_dataframe(sheet)


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


# データの洗浄
NaN_dell_column = ["name","price","address","layout","age","area","traffic_tx"] #欠損値の削除
df = df.dropna(subset = NaN_dell_column,axis = 0)

df["price"] = df["price"]/10000 #価格を（万円）に変更
df['station'] = df['traffic_tx'].str.split(pat='「',expand=True)[1].str.split(pat='」',expand=True)[0] #駅名取得
df['name'] = df['name'].str.replace('【マンション】','')
df['layout'] = df['layout'].str.replace('（納戸）','')

int_convert_column = ["price",'price_kanri','price_tsumitate',"age","area","floor","time_walk"] #整数型に変換
df[int_convert_column] = df[int_convert_column].astype('int')


#------------------------page-Detail------------------------

st.title('物件連絡網')

st.write("理想の物件が出たら、メールでお知らせ！物件条件を条件を選択して下さい。")

st.write('### 物件フィルター条件')
# 駅名でフィルター
column_station = 'station'
station_list = list(df[column_station].unique())
selected_station = st.multiselect('駅名でフィルター', station_list, default = ['北千住'])
#df = df[(df[column_station].isin(selected_station))]

# 価格でフィルター
column_filter = 'price'
max_value = int(df[column_filter].max())
min_value = int(df[column_filter].min())
selected_price = st.slider('価格(万円)でフィルター', min_value, max_value, max_value, None)
#df = df[df[column_filter] <= selected_price]

# 広さでフィルター
column_filter = 'area'
max_value = int(df[column_filter].max())
min_value = int(df[column_filter].min())
selected_area = st.slider('広さ(m2)でフィルター', min_value, max_value, max_value, None)
#df = df[df[column_filter] <= selected_area]

# 築年でフィルター
column_filter = 'age'
max_value = int(df[column_filter].max())
min_value = int(df[column_filter].min())
selected_old = st.slider('築年(年)でフィルター', min_value, max_value, max_value, None)
#df = df[df[column_filter] <= selected_old]

# 最寄駅からの時間でフィルター
column_filter = 'time_walk'
max_value = int(df[column_filter].max())
min_value = int(df[column_filter].min())
selected_time = st.slider('最寄駅からの徒歩時間(分)でフィルター', min_value, max_value, max_value, None)
#df = df[df[column_filter] <= selected_time]

#メールアドレス入力
st.write('### 送信先登録')
mail_address = st.text_input('メールアドレスを入力してください。',"")

fav_list = []

if st.button("登録", key=0):
    if mail_address=="" or mail_address==None:
        st.write("エラー！メールアドレスを入力してください。")
    else:

        #Googleスプレッドシートからデータ取得し格納(Streamlit用)
        # from google.oauth2 import service_account
        # import gspread
        # import pandas as pd
        # スプレッドシートの認証
        scopes = [ 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'
        ]
        credentials = service_account.Credentials.from_service_account_info( st.secrets["gcp_service_account"], scopes=scopes
        )
        gc = gspread.authorize(credentials)
        # スプレッドシートからデータ取得
        SP_SHEET_KEY = st.secrets.SP_SHEET_KEY.key # スプレッドシートのキー
        sh = gc.open_by_key(SP_SHEET_KEY)
        SP_SHEET = 'info_mail' # シート名「シート1」を指定
        worksheet = sh.worksheet(SP_SHEET)
        data = worksheet.get_all_values() # シート内の全データを取得
        df2 = pd.DataFrame(data[1:],columns=data[0])
        
        # sheet = client.open("Mugisake_KA01").worksheet('info_mail')
        # df2 = get_as_dataframe(sheet)
        df2 = df2.dropna(subset = ["メールアドレス","最寄り駅","価格","広さ","築年","最寄りからの時間"])
        df3= pd.DataFrame({
            "メールアドレス":mail_address,
            "最寄り駅":selected_station,
            "価格":selected_price,
            "広さ":selected_area,
            "築年":selected_old,
            "最寄りからの時間":selected_time})
        st.write(df3)
        df2 = pd.concat([df2,df3])
        set_with_dataframe(worksheet, df2)
        st.write("登録完了")