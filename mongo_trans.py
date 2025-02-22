from pymongo import MongoClient

class MongoDBManager:
    def __init__(self, db_name, collection_name, mongo_uri):
       
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def save_data(self, data):
       
        conversation_id = data.get('conversation_id')
        if conversation_id:
            return self.collection.update_one(
                {'conversation_id': conversation_id},
                {'$set': data},
                upsert=True
            )
        else:
            
            return self.collection.insert_one(data).inserted_id

    def get_data(self, query):
     
        return list(self.collection.find(query))