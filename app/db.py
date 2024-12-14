from pymongo import MongoClient
import os


client = MongoClient("mongodb://localhost:27017/Three_Level_Authentication")
db = client['Three_Level_Authentication']
users_collection = db['users']
patterns_collection = db['patterns']