from pymongo import MongoClient
from configs import MONGODB_URI

cluster = MongoClient(MONGODB_URI)
database = cluster['cwp']

autorole_db = database['autorole']
