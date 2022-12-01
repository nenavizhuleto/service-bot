from pymongo import MongoClient

class Mongo:
    def __init__(self, connection_sting) -> None:
        self.db = MongoClient(connection_sting)


    def get_db(self, dbname):
        return self.db[dbname]