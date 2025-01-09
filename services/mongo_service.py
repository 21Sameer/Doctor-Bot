import os
from pymongo import MongoClient, ASCENDING
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MongoDB connection string
connection_string = os.getenv("MONGO_CONNECTION_STRING", "mongodb://localhost:27017")

# Database and collection names
DB_NAME = "UET"
CHAT_COLLECTION = "chat"


def get_database():
    """
    Connect to MongoDB and return the database instance.
    """
    try:
        client = MongoClient(connection_string)
        logging.info("Connected to MongoDB.")
        return client[DB_NAME]
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {e}")
        raise


def save_chat(data: dict):
    """
    Save a chat entry to the database.

    Args:
        data (dict): Chat data to be saved, must include user_id, query, and response.
    """
    try:
        data["timestamp"] = datetime.now()
        db = get_database()
        db[CHAT_COLLECTION].insert_one(data)
        logging.info(f"Chat saved: {data}")
    except Exception as e:
        logging.error(f"Error saving chat: {e}")
        raise


def fetch_chat(user_id: str):
    """
    Fetch chat history for a specific user.

    Args:
        user_id (str): User ID to fetch chat history for.

    Returns:
        list: A list of chat records sorted by timestamp.
    """
    try:
        db = get_database()
        chat_history = list(
            db[CHAT_COLLECTION].find({"user_id": user_id}).sort("timestamp", ASCENDING)
        )
        logging.info(f"Fetched {len(chat_history)} chat records for user_id: {user_id}")
        return chat_history
    except Exception as e:
        logging.error(f"Error fetching chat history: {e}")
        raise


