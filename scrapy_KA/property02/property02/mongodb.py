import pymongo
import pandas as pd

client = pymongo.MongoClient('mongodb+srv://kazushi:test1991@cluster0.6xm5xsd.mongodb.net/?retryWrites=true&w=majority')
db = client['property02DB']
collection = db['suumo_KA02']

for document in collection.find():
    # print(document)
    df = pd.DataFrame(document)

print(df)
