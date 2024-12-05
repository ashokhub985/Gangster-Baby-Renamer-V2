import pymongo
import os
from typing import Optional, List, Any
from helper.date import add_date

# Load environment variables
DB_NAME = os.environ.get("DB_NAME", "")
DB_URL = os.environ.get("DB_URL", "")

# Initialize MongoDB Client
mongo = pymongo.MongoClient(DB_URL)
db = mongo[DB_NAME]
dbcol = db["user"]

# Ensure indexing for efficient lookups
dbcol.create_index("_id", unique=True)

# Helper Functions

def total_user() -> int:
    """Get the total number of users."""
    return dbcol.count_documents({})

def botdata(chat_id: int) -> None:
    """Insert bot data for a new bot."""
    try:
        bot_data = {"_id": chat_id, "total_rename": 0, "total_size": 0}
        dbcol.update_one({"_id": chat_id}, {"$setOnInsert": bot_data}, upsert=True)
    except Exception as e:
        print(f"Error inserting bot data: {e}")

def total_rename(chat_id: int, renamed_file: int) -> None:
    """Update the total rename count."""
    try:
        dbcol.update_one({"_id": chat_id}, {"$inc": {"total_rename": renamed_file}})
    except Exception as e:
        print(f"Error updating total rename: {e}")

def total_size(chat_id: int, now_file_size: int) -> None:
    """Update the total size."""
    try:
        dbcol.update_one({"_id": chat_id}, {"$inc": {"total_size": now_file_size}})
    except Exception as e:
        print(f"Error updating total size: {e}")

def insert(chat_id: int) -> None:
    """Insert a new user."""
    try:
        user_det = {
            "_id": chat_id,
            "file_id": None,
            "caption": None,
            "daily": 0,
            "date": 0,
            "uploadlimit": 1288490188,  # Default limit (approx. 1.2GB)
            "used_limit": 0,
            "usertype": "Free",
            "prexdate": None,
        }
        dbcol.update_one({"_id": chat_id}, {"$setOnInsert": user_det}, upsert=True)
    except Exception as e:
        print(f"Error inserting user: {e}")

def addthumb(chat_id: int, file_id: str) -> None:
    """Save a thumbnail for the user."""
    try:
        dbcol.update_one({"_id": chat_id}, {"$set": {"file_id": file_id}})
    except Exception as e:
        print(f"Error adding thumbnail: {e}")

def delthumb(chat_id: int) -> None:
    """Delete the user's thumbnail."""
    try:
        dbcol.update_one({"_id": chat_id}, {"$set": {"file_id": None}})
    except Exception as e:
        print(f"Error deleting thumbnail: {e}")

def addcaption(chat_id: int, caption: str) -> None:
    """Save a caption for the user."""
    try:
        dbcol.update_one({"_id": chat_id}, {"$set": {"caption": caption}})
    except Exception as e:
        print(f"Error adding caption: {e}")

def delcaption(chat_id: int) -> None:
    """Delete the user's caption."""
    try:
        dbcol.update_one({"_id": chat_id}, {"$set": {"caption": None}})
    except Exception as e:
        print(f"Error deleting caption: {e}")

def dateupdate(chat_id: int, date: int) -> None:
    """Update the user's date."""
    try:
        dbcol.update_one({"_id": chat_id}, {"$set": {"date": date}})
    except Exception as e:
        print(f"Error updating date: {e}")

def used_limit(chat_id: int, used: int) -> None:
    """Update the user's used limit."""
    try:
        dbcol.update_one({"_id": chat_id}, {"$set": {"used_limit": used}})
    except Exception as e:
        print(f"Error updating used limit: {e}")

def usertype(chat_id: int, type: str) -> None:
    """Update the user's type."""
    try:
        dbcol.update_one({"_id": chat_id}, {"$set": {"usertype": type}})
    except Exception as e:
        print(f"Error updating user type: {e}")

def uploadlimit(chat_id: int, limit: int) -> None:
    """Update the user's upload limit."""
    try:
        dbcol.update_one({"_id": chat_id}, {"$set": {"uploadlimit": limit}})
    except Exception as e:
        print(f"Error updating upload limit: {e}")

def addpre(chat_id: int) -> None:
    """Add a premium expiry date for the user."""
    try:
        date = add_date()
        dbcol.update_one({"_id": chat_id}, {"$set": {"prexdate": date[0]}})
    except Exception as e:
        print(f"Error adding premium date: {e}")

def addpredata(chat_id: int) -> None:
    """Remove premium expiry date for the user."""
    try:
        dbcol.update_one({"_id": chat_id}, {"$set": {"prexdate": None}})
    except Exception as e:
        print(f"Error removing premium date: {e}")

def daily(chat_id: int, date: int) -> None:
    """Update the user's daily limit."""
    try:
        dbcol.update_one({"_id": chat_id}, {"$set": {"daily": date}})
    except Exception as e:
        print(f"Error updating daily limit: {e}")

def find(chat_id: int) -> List[Optional[Any]]:
    """Find a user's file and caption."""
    try:
        user = dbcol.find_one({"_id": chat_id}, {"file_id": 1, "caption": 1})
        if user:
            return [user.get("file_id"), user.get("caption")]
        return [None, None]
    except Exception as e:
        print(f"Error finding user: {e}")
        return [None, None]

def getid() -> List[int]:
    """Get all user IDs."""
    try:
        return [user["_id"] for user in dbcol.find({}, {"_id": 1})]
    except Exception as e:
        print(f"Error getting user IDs: {e}")
        return []

def delete(chat_id: int) -> None:
    """Delete a user."""
    try:
        dbcol.delete_one({"_id": chat_id})
    except Exception as e:
        print(f"Error deleting user: {e}")

def find_one(chat_id: int) -> Optional[dict]:
    """Find a single user."""
    try:
        return dbcol.find_one({"_id": chat_id})
    except Exception as e:
        print(f"Error finding user: {e}")
        return None
