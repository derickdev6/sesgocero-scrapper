from itemadapter import ItemAdapter
from pymongo import MongoClient
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re
import logging

logger = logging.getLogger(__name__)


class MongoDBPipeline:
    def __init__(self):
        load_dotenv()
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.client[os.getenv("MONGODB_DATABASE", "sesgocero")]
        self.collection = self.db[os.getenv("MONGODB_COLLECTION", "articles")]
        self.collection.create_index("url", unique=True)

    def clean_html(self, text):
        if not text:
            return ""
        soup = BeautifulSoup(text, "html.parser")
        cleaned = soup.get_text(separator=" ", strip=True)
        return re.sub(r"\s+", " ", cleaned)

    def normalize_text(self, text):
        if not text:
            return ""
        return re.sub(r"\s+", " ", text.strip())

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Validación de campo obligatorio
        if not adapter.get("url"):
            spider.logger.warning("Item descartado: faltante campo 'url'")
            return None

        # Limpieza de campos de texto
        for field in ["title", "subtitle", "content"]:
            if adapter.get(field):
                adapter[field] = self.normalize_text(
                    self.clean_html(adapter.get(field))
                )

        # Fecha a ISO solo si es datetime
        if adapter.get("date") and isinstance(adapter["date"], datetime):
            adapter["date"] = adapter["date"].isoformat()

        # Evitar updates si no hay cambios
        existing = self.collection.find_one({"url": adapter["url"]})
        if existing:
            existing.pop("_id", None)
            current_data = dict(adapter)
            if all(existing.get(k) == current_data.get(k) for k in current_data):
                return item

        # Insertar o actualizar
        self.collection.update_one(
            {"url": adapter["url"]}, {"$set": dict(adapter)}, upsert=True
        )

        spider.logger.info(f"Artículo guardado: {adapter.get('title')}")
        return item

    def close_spider(self, spider):
        self.client.close()
