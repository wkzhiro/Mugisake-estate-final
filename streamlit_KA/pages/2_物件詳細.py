import streamlit as st
import numpy as np

# # Googleスプレッドシートからデータ取得し格納
# import pandas as pd
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# from gspread_dataframe import get_as_dataframe

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

# df["price"] = df["price"]/10000 #価格を（万円）に変更
df['station'] = df['traffic_tx'].str.split(pat='「',expand=True)[1].str.split(pat='」',expand=True)[0] #駅名取得
df['name'] = df['name'].str.replace('【マンション】','')
df['layout'] = df['layout'].str.replace('（納戸）','')

int_convert_column = ["price",'price_kanri','price_tsumitate',"area","age","floor","time_walk"] #整数型に変換
df[int_convert_column] = df[int_convert_column].astype('int')

#------------------------page-Detail------------------------

st.title('物件詳細')
st.write("気になる物件の詳細に加えて、「お得度」「周辺地図」「ハザード情報」をお知らせ！")

id_home = int(st.text_input('詳細を表示したい物件番号は？', "0"))


# 表の表示
df_detail = df.loc[id_home]

st.write('### 🌟お得度🌟')
df_detail1 = df_detail[['predicted_price','discounted_price']]
df_detail1 = df_detail1.set_axis(["AIが予想した価格(円)","お得度(円)"]) #列名の変更
st.dataframe(df_detail1, width=2000,height=110)

st.write('### 詳細データ')
df_detail1 = df_detail[['name','price','price_kanri','price_tsumitate',
    'layout','area','age','direction','floor',
    'traffic_tx','url']]
df_detail1 = df_detail1.set_axis(["マンション名","価格(円)","管理費(円/月)","修繕積立金(円/月)",
    "間取り","面積(m2)","築年","方角","階数",
    "最寄駅","Link"]) #列名の変更
st.dataframe(df_detail1, width=2000,height=420)


# 地図の表示
import folium
from streamlit_folium import folium_static
# 緯度経度データを作成する
df_map = pd.DataFrame(
    data=[[df_detail['Ido'],df_detail['Keido']]],
    index=[df_detail['name']],
    columns=["x","y"]
)
# データを地図に渡す関数を作成する
def AreaMarker(df,m):
    for index, r in df.iterrows(): 

        # ピンをおく
        folium.Marker(
            location=[r.x, r.y],
            popup=index,
        ).add_to(m)

        # 円を重ねる
        folium.Circle(
            radius=rad*1000,
            location=[r.x, r.y],
            popup=index,
            color="yellow",
            fill=True,
            fill_opacity=0.07
        ).add_to(m)
# 画面作成
st.write('### 周辺地図')
rad = st.slider('拠点を中心とした円の半径（km）',
                value=1,min_value=0, max_value=5) # スライダーをつける
# st.subheader("各拠点からの距離{:,}km".format(rad)) # 半径の距離を表示
m = folium.Map(df_map, zoom_start=15) # 地図の初期設定
AreaMarker(df_map,m) # データを地図渡す
folium_static(m) # 地図情報を表示



#ハザードマップの表示
import os, json, requests, math, sys
from skimage import io
from io import BytesIO
import cv2



def get_tile_num(lat, lon, zoom):
    """
    緯度経度からタイル座標を取得する
    Parameters
    ----------
    lat : number 
        タイル座標を取得したい地点の緯度(deg) 
    lon : number 
        タイル座標を取得したい地点の経度(deg) 
    zoom : int 
        タイルのズーム率
    Returns
    -------
    xtile : int
        タイルのX座標
    ytile : int
        タイルのY座標
    """
    # https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Python
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def get_tile_bbox(xtile, ytile, z):


    """
    タイル座標からバウンディングボックスを取得する
    https://tools.ietf.org/html/rfc7946#section-5
    Parameters
    ----------
    z : int 
        タイルのズーム率 
    x : int 
        タイルのX座標 
    y : int 
        タイルのY座標 
    Returns
    -------
    bbox: tuple of number
        タイルのバウンディングボックス
        (左下経度, 左下緯度, 右上経度, 右上緯度)
    """
    def num2deg(xtile, ytile, z):
        # https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Python
        n = 2.0 ** z
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return (lon_deg, lat_deg)
    
    right_top = num2deg(xtile + 1, ytile, z)
    left_bottom = num2deg(xtile, ytile + 1, z)
    return (left_bottom[0], left_bottom[1], right_top[0], right_top[1])

def get_tile_lonlats(zoom, xtile, ytile):
    """
    タイルの各ピクセルの左上隅の経度緯度を取得する
    Parameters
    ----------
    z : int 
        タイルのズーム率 
    x : int 
        タイルのX座標 
    y : int 
        タイルのY座標 
    Returns
    -------
    lonlats: ndarray
        タイルの各ピクセルの経度緯度
        256*256*2のnumpy配列
        経度、緯度の順
    """
    x = int(xtile * 2**8)
    y = int(ytile * 2**8)
    z = zoom + 8

    lonlats = np.zeros((256,256,2))
    for i in range(256):
        for j in range(256):
            bbox = get_tile_bbox(z, x + j, y + i)
            lonlats[i,j,:] = [bbox[0], bbox[3]]
    return lonlats

def get_flood_image(z, x, y, params={}):
    """
    浸水域のタイル画像を取得する
    Parameters
    ----------
    z : int
        タイルのズーム率
    x : int
        タイルのX座標
    y : int
        タイルのY座標
    option : dict
        APIパスのオプション(entityId)
    params : dict
        クエリパラメータ
    Returns
    -------
    img: ndarray
        タイル画像
        https://disaportal.gsi.go.jp/hazardmap/copyright/opendata.html#l2shinsuishin_kuni
    """
    url = 'https://disaportaldata.gsi.go.jp/raster/01_flood_l2_shinsuishin_data/{}/{}/{}.png'.format(z, x, y)
    r = requests.get(url, params=params)
    if not r.status_code == requests.codes.ok:
        r.raise_for_status()
    return io.imread(BytesIO(r.content))

def get_map_image(z, x, y, params={}):
    """
    浸水域のタイル画像を取得する
    Parameters
    ----------
    z : int
        タイルのズーム率
    x : int
        タイルのX座標
    y : int
        タイルのY座標
    option : dict
        APIパスのオプション(entityId)
    params : dict
        クエリパラメータ
    Returns
    -------
    img: ndarray
        タイル画像
        https://disaportal.gsi.go.jp/hazardmap/copyright/opendata.html#l2shinsuishin_kuni
    """
    url = 'https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{}/{}/{}.jpg'.format(z, x, y)
    r = requests.get(url, params=params)
    if not r.status_code == requests.codes.ok:
        r.raise_for_status()
    return io.imread(BytesIO(r.content))

def get_combined_image(get_image_func, z, topleft_x, topleft_y, size_x=1, size_y=1, params={}):
    """
    結合されたタイル画像を取得する
    Parameters
    ----------
    get_image_func : function
        タイル画像取得メソッド
        引数はz, x, y, option, params
    z : int
        タイルのズーム率
    topleft_x : int
        左上のタイルのX座標
    topleft_y : int
        左上のタイルのY座標
    size_x : int
         タイルを経度方向につなぎわせる枚数
    size_y : int
        タイルを緯度方向につなぎわせる枚数
    option : dict
        APIパスのオプション(z,x,y除く)
    params : dict
        クエリパラメータ
    Returns
    -------
    combined_image: ndarray
        結合されたタイル画像
    """
    rows = []
    blank = np.zeros((256, 256, 4), dtype=np.uint8)
    for y in range(size_y):
        row = []
        for x in range(size_x):
            try:
                img = get_image_func(z, topleft_x + x-math.floor(size_x/2), topleft_y + y-math.floor(size_y/2), params)
            except Exception as e:
                img = blank
            row.append(img)
        rows.append(np.hstack(row))
    return  np.vstack(rows)

def make_hazard_map(z, y_lat, x_lon, size_x=1.0, size_y=1.0,x_offset=0 ,y_offset=0 , params={}):
    x,y = get_tile_num(y_lat, x_lon, z)
    
    # 浸水域を取得して描画
    combined_flood = get_combined_image(get_flood_image, z, x, y,size_x,size_y)
    combined_flood = combined_flood[:,:,0:3]
    combined_flood  = np.where(combined_flood==[0,0,0],[255,255,255],combined_flood)
    combined_flood = np.array(combined_flood, dtype=np.uint8)

    # 写真を取得して描画
    combined_base = get_combined_image(get_map_image, z, x, y,size_x,size_y)
    
    #　画像を合成
    blended = cv2.addWeighted(src1=combined_base,alpha=0.5,src2=combined_flood,beta=0.5,gamma=0)
    
    bbox_nw = get_tile_bbox(x-math.floor(size_x/2),y-math.floor(size_y/2),z) #結合された画像の左上のタイル座標の緯度経度
    bbox_se = get_tile_bbox(x-math.floor(size_x/2)+size_x-1,y-math.floor(size_y/2)+size_y-1,z) #結合された画像の右下のタイル座標の緯度経度
    min_lon = bbox_nw[0]
    min_lat = bbox_se[1] 
    
    longitudes = []
    latitudes = []
    longitudes.append(x_lon - min_lon)
    latitudes.append(y_lat - min_lat)
    
    diff_long_range = bbox_se[2] - bbox_nw[0] # 経度の範囲上限
    diff_lat_range = bbox_nw[3] - bbox_se[1] # 緯度の範囲上限
    x_img_size = blended.shape[0] #画像のサイズを求める（x軸方向）
    y_img_size = blended.shape[1] #画像のサイズを求める（y軸方向）

    onepix_degree_long = diff_long_range/x_img_size
    onepix_degree_lat = diff_lat_range/y_img_size
    
    pixel_x = longitudes[0]/onepix_degree_long
    pixel_y = latitudes[0]/onepix_degree_lat
    pixel_x = np.array(pixel_x,dtype = 'int16')
    pixel_y = np.array(pixel_y,dtype = 'int16')
    
    from urllib.request import urlopen
    def urlread(url, flags=cv2.IMREAD_UNCHANGED):
        response = urlopen(url)
        img = np.asarray(bytearray(response.read()), dtype=np.uint8)
        img = cv2.imdecode(img, flags)
        return img

    legend_img = urlread('https://disaportal.gsi.go.jp/hazardmap/copyright/img/shinsui_legend2-1.png')    
    # legend_img = cv2.imread('shinsui_legend2-1.png')
    legend_img = cv2.cvtColor(legend_img, cv2.COLOR_BGR2RGB)
    
    blended_mix = blended 
    blended_mix[y_offset:y_offset+legend_img.shape[0], x_offset:x_offset+legend_img.shape[1]] = legend_img
    cv2.circle(blended_mix, center=(int(pixel_x), y_img_size - int(pixel_y)), radius=15, color = (255, 0, 0), thickness=-1, lineType=cv2.LINE_AA,shift=0)

    return blended_mix

def cal_flood_risk(z, y_lat, x_lon, size_x=1.0, size_y=1.0,x_offset=0 ,y_offset=0 , params={}):
    x,y = get_tile_num(y_lat, x_lon, z)
    
    # 浸水域を取得して描画
    combined_flood = get_combined_image(get_flood_image, z, x, y,size_x,size_y)
    combined_flood = combined_flood[:,:,0:3]
    
    bbox_nw = get_tile_bbox(x-math.floor(size_x/2),y-math.floor(size_y/2),z) #結合された画像の左上のタイル座標の緯度経度
    bbox_se = get_tile_bbox(x-math.floor(size_x/2)+size_x-1,y-math.floor(size_y/2)+size_y-1,z) #結合された画像の右下のタイル座標の緯度経度
    min_lon = bbox_nw[0]
    min_lat = bbox_se[1] 

    longitudes = []
    latitudes = []
    longitudes.append(x_lon - min_lon)
    latitudes.append(y_lat - min_lat)
    
    diff_long_range = bbox_se[2] - bbox_nw[0] # 経度の範囲上限
    diff_lat_range = bbox_nw[3] - bbox_se[1] # 緯度の範囲上限
    x_img_size = combined_flood.shape[0] #画像のサイズを求める（x軸方向）
    y_img_size = combined_flood.shape[1] #画像のサイズを求める（y軸方向）

    onepix_degree_long = diff_long_range/x_img_size
    onepix_degree_lat = diff_lat_range/y_img_size
    
    pixel_x = longitudes[0]/onepix_degree_long
    pixel_y = latitudes[0]/onepix_degree_lat
    pixel_x = np.array(pixel_x,dtype = 'int16')
    pixel_y = np.array(pixel_y,dtype = 'int16')
    
    from urllib.request import urlopen
    def urlread(url, flags=cv2.IMREAD_UNCHANGED):
        response = urlopen(url)
        img = np.asarray(bytearray(response.read()), dtype=np.uint8)
        img = cv2.imdecode(img, flags)
        return img

    dtli_img = urlread('https://disaportal.gsi.go.jp/hazardmap/copyright/img/shinsui_legend2-1.png')
    # dtli_img = cv2.imread('shinsui_legend2-1.png')
    dtli_img = cv2.cvtColor(dtli_img, cv2.COLOR_BGR2RGB)
    
    risk_level = {}
    risk_level["0"] = "安全"
    risk_level["1"] = "床下浸水・膝下以下"
    risk_level["2"] = "１階浸水"
    risk_level["3"] = "２階浸水"
    risk_level["4"] = "きわめて危険（5m以上）"
    
    total = 0
    
    for x in range(100):
        for y in range(100):
            print(pixel_x-50+x,pixel_y-50+y)
            if list(combined_flood[pixel_x-50+x,pixel_y-50+y,:]) == [247,245,169]:
                total += 1
            elif list(combined_flood[pixel_x-50+x,pixel_y-50+y,:]) ==  [255,216,192]:
                total += 2
            elif list(combined_flood[pixel_x-50+x,pixel_y-50+y,:]) ==  [255,183,183]:
                total += 3
            elif list(combined_flood[pixel_x-50+x,pixel_y-50+y,:]) ==  [255,145,145]:
                total += 4
            else:
                total +=0
    
    risk = total/10000
    
    return risk_level[str(int(risk))]

def cal_eq_pb(lat, lon):
    position = str(lon)+','+str(lat)
    url_eq='https://www.j-shis.bosai.go.jp/map/api/fltsearch?position={}&epsg=4612&mode=C&version=Y2022&case=AVR&period=P_T30&format=json&ijma=60'.format(position)
    result_eq = requests.get(url_eq).json()
    
    for i in range(len(result_eq['Fault'])):
        if i == 0:
            probability = 1-float(result_eq['Fault'][i]['probability'])
        else:
            probability *=  (1-float(result_eq['Fault'][i]['probability']))

    total_probability = 1- probability
    
    return total_probability*100

if id_home>=0:
    #物件名あるいは最寄り駅で取得
    item_lat = df.iloc[int(id_home),18]
    item_lon = df.iloc[int(id_home),17]

    # st.write("最寄り駅は青丸で表示")
    risk_flood = cal_flood_risk(z=18, y_lat = item_lat, x_lon=item_lon, size_x=4, size_y=4,x_offset=0 ,y_offset=0 , params={})
    risk_eq = cal_eq_pb(item_lat, item_lon)

    st.write('### ハザード情報')
    st.write("50年以内に6強以上の地震発生確率：",format(risk_eq,'.1f'),"％")
    st.write("最大の洪水被害：", risk_flood)
    st.image(make_hazard_map(z=16,  y_lat= item_lat, x_lon = item_lon, size_x=4, size_y=4,x_offset=0 ,y_offset=0 , params={}))

