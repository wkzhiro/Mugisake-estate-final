import pymongo
import pandas as pd

client = pymongo.MongoClient('mongodb+srv://kazushi:test1991@cluster0.6xm5xsd.mongodb.net/?retryWrites=true&w=majority')
db = client['property02DB']
collection = db['suumo_KA02']

d2={}
df_c=pd.DataFrame(d2)
# df=pd.DataFrame( columns=list(document))

for document in collection.find():
    for k,v in document.items():
        d2[k]=pd.Series(v)
        df=pd.DataFrame(d2)
    df_c = pd.concat([df_c,df])

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

# use creds to create a client to interact with the Google Drive API
scope =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("Mugisake_KA01").sheet1

# sheet.update_cell(1,1,df_c)
set_with_dataframe(sheet, df_c.reset_index())

# Extract and print all of the values
list_of_hashes = sheet.get_all_records()
print(list_of_hashes)
