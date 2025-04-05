from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime


def cleanup_duplicates():
    # Load environment variables
    load_dotenv()

    # Connect to MongoDB
    client = MongoClient(
        os.getenv(
            "MONGODB_URI",
            "mongodb+srv://derickdev6:AHrkkIM9SBZWtjsN@ecolog.vtaw5.mongodb.net/?retryWrites=true&w=majority&appName=sesgocero",
        )
    )

    # Get database and collection
    db = client[os.getenv("MONGODB_DATABASE", "sesgocero")]
    collection = db[os.getenv("MONGODB_COLLECTION", "articles")]

    # Find all duplicate IDs
    pipeline = [
        {"$group": {"_id": "$id", "count": {"$sum": 1}, "docs": {"$push": "$_id"}}},
        {"$match": {"count": {"$gt": 1}}},
    ]

    duplicates = list(collection.aggregate(pipeline))

    if not duplicates:
        print("No duplicates found!")
        return

    print(f"Found {len(duplicates)} IDs with duplicates")

    # For each duplicate ID, keep the most recent document and delete others
    for dup in duplicates:
        id_value = dup["_id"]
        doc_ids = dup["docs"]

        # Get all documents with this ID
        docs = list(collection.find({"id": id_value}))

        # Sort by date (if available) or keep the first one
        if all("date" in doc for doc in docs):

            def get_date(doc):
                date_str = doc.get("date")
                if date_str:
                    try:
                        return datetime.fromisoformat(date_str)
                    except (ValueError, TypeError):
                        return datetime.min
                return datetime.min

            docs.sort(key=get_date, reverse=True)

        # Keep the most recent document
        keep_id = docs[0]["_id"]

        # Delete all other duplicates
        collection.delete_many({"id": id_value, "_id": {"$ne": keep_id}})

        print(f"Cleaned up {len(doc_ids) - 1} duplicates for ID: {id_value}")

    print("Cleanup completed!")
    client.close()


if __name__ == "__main__":
    cleanup_duplicates()
