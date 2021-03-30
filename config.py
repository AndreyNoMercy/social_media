from pymongo import MongoClient

DB_hello_moda = MongoClient('mongodb://localhost:27017/')['hello_moda']
DB_bereg_resort = MongoClient('mongodb://localhost:27017/')['bereg_resort']
DB_hydroflight = MongoClient('mongodb://localhost:27017/')['hydroflight_academy']