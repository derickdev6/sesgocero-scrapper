# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
from pymongo import MongoClient
from dotenv import load_dotenv


class SesgoceroScrapperPipeline:
    def process_item(self, item, spider):
        return item


class MongoDBPipeline:
    def __init__(self):
        load_dotenv()
        self.client = MongoClient(
            os.getenv(
                "MONGODB_URI",
                "mongodb+srv://derickdev6:AHrkkIM9SBZWtjsN@ecolog.vtaw5.mongodb.net/?retryWrites=true&w=majority&appName=sesgocero",
            )
        )
        self.db = self.client[os.getenv("MONGODB_DATABASE", "sesgocero")]
        self.collection = self.db[os.getenv("MONGODB_COLLECTION", "articles")]

    def process_item(self, item, spider):
        # Convert datetime to string for MongoDB storage
        if item.get("date"):
            item["date"] = item["date"].isoformat()

        # Insert the item into MongoDB
        self.collection.insert_one(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()
