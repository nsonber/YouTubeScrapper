import pymongo
from pymongo.errors import ConnectionFailure


class ConnectionError(Exception):
    pass


class SaveToMongo:

    def __init__(self, config: dict) -> None:
        self.configuration = config

    def __enter__(self) -> 'cursor':
        try:
            conn_str = "mongodb+srv://" + self.configuration.get('user') + ":" + self.configuration.get('password') \
                       + "@" + self.configuration.get('host')
            self.client = pymongo.MongoClient(conn_str)
            db = self.client[self.configuration.get('database')]
            self.collection = db[self.configuration.get('collection')]
            return self.collection
        except ConnectionFailure as err:
            raise ConnectionError(err)
