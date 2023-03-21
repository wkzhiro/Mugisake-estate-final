import streamlit as st
import numpy as np
from datetime import datetime

# Googleスプレッドシートからデータ取得し格納
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import smtplib
from email.mime.text import MIMEText
from email.header import Header

import schedule
from time import sleep

def send_mail(gmail, password, mail, mailText, subject):
    charset = 'utf-8'
    msg = MIMEText(mailText, 'plain', charset)
    msg['Subject'] = Header(subject.encode(charset), charset)
    smtp_obj = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_obj.ehlo()
    smtp_obj.starttls()
    smtp_obj.login(gmail, password)
    smtp_obj.sendmail(gmail, mail, msg.as_string())
    smtp_obj.quit()

#01 定期実行する関数を準備
def mail_task():
    scope =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('grspread_key_mugisake.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open("Mugisake_KA01").worksheet('sheet5')
    df = get_as_dataframe(sheet)

    # データの洗浄
    NaN_dell_column = ["name","price","address","layout","age","area","traffic_tx"] #欠損値の削除
    df = df.dropna(subset = NaN_dell_column,axis = 0)

    df["price"] = df["price"]/10000 #価格を（万円）に変更
    df['station'] = df['traffic_tx'].str.split(pat='「',expand=True)[1].str.split(pat='」',expand=True)[0] #駅名取得
    df['name'] = df['name'].str.replace('【マンション】','')
    df['layout'] = df['layout'].str.replace('（納戸）','')

    int_convert_column = ["price",'price_kanri','price_tsumitate',"area","floor","time_walk"] #整数型に変換
    df[int_convert_column] = df[int_convert_column].astype('int')


    #お気に入りデータの取得
    sheet = client.open("Mugisake_KA01").worksheet('info_mail')
    df2 = get_as_dataframe(sheet)
    df2 = df2.dropna(subset = ["メールアドレス","最寄り駅","価格","広さ","築年","最寄りからの時間"])

    
    station=[]
    
    for index,info in df2.iterrows():
        
        # 駅名でフィルター
        station.append(info["最寄り駅"])
        column_station = 'station'
        df = df[(df[column_station].isin(station))]

        # 価格でフィルター
        column_filter = 'price'
        df = df[df[column_filter] <= int(info["価格"])]

        # 広さでフィルター
        column_filter = 'area'
        df = df[df[column_filter] <= int(info["広さ"])]

        # 築年でフィルター
        column_filter = 'age_int'
        df = df[df[column_filter] <= int(info["築年"])]

        # 最寄駅からの時間でフィルター
        column_filter = 'time_walk'
        df = df[df[column_filter] <= int(info["最寄りからの時間"])]

        # 更新日でフィルター
        d_today = datetime.now()
        from_dt = datetime(d_today.year, d_today.month, d_today.day-4)
        to_dt = datetime(d_today.year, d_today.month, d_today.day+3)
        df = df[(df["date"].map(lambda x:datetime.strptime(x, '%Y/%m/%d'))>= from_dt) & (df["date"].map(lambda x:datetime.strptime(x, '%Y/%m/%d')<= to_dt))]

        

        no=[]
        name=[]
        price=[]
        layout=[]
        url=[]
        mail_text=''
        mail_est_list=[]

        for index, row in df.iterrows():
            no.append("○物件No."+str(index))
            name.append(row["name"].replace('\u3000',''))
            price.append(int(row["price"]))
            layout.append(row["layout"])
            url.append(row["url"])
            
        for i in range(len(df)):
            mail_est_list.append('{} ○物件名：{} ○価格：{}円 ○間取り：{} ○url：{}'.format(no[i],name[i],price[i],layout[i],url[i]))
            mail_text = '\
                        '.join(mail_est_list)

        gmail = '送り主のメアドを入力'
        password = 'gmailのパスワード'
        mail = info['メールアドレス']
        mailText = mail_text
        subject = '新着おすすめ物件'
        send_mail(gmail, password, mail, mailText, subject)
        print("メール完了")


#02 スケジュール登録
schedule.every(10).seconds.do(mail_task)


#03 イベント実行
while True:
    schedule.run_pending()
    sleep(1)