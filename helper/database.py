import pymongo
import os
from helper.date import add_date

# Load environment variables
DB_NAME = os.environ.get("DB_NAME", "Rename")
DB_URL = os.environ.get("DB_URL", "mongodb+srv://fiwalo:Vijayraj786@rename.nkh3g.mongodb.net/?retryWrites=true&w=majority&appName=Rename")

# Initialize MongoDB Client
mongo = pymongo.MongoClient(DB_URL)
db = mongo[DB_NAME]
dbcol = db["user"]

# Ensure indexing for efficient lookups
dbcol.create_index("_id", unique=True)

# Helper Functions

def total_user():
    """Get the total number of users."""
    return dbcol.count_documents({})

def botdata(chat_id):
    """Insert bot data for a new bot."""
    bot_id = int(chat_id)
    bot_data = {"_id": bot_id, "total_rename": 0, "total_size": 0}
    dbcol.update_one({"_id": bot_id}, {"$setOnInsert": bot_data}, upsert=True)

def total_rename(chat_id, renamed_file):
    """Update the total rename count."""
    dbcol.update_one({"_id": chat_id}, {"$inc": {"total_rename": renamed_file}})

def total_size(chat_id, now_file_size):
    """Update the total size."""
    dbcol.update_one({"_id": chat_id}, {"$inc": {"total_size": now_file_size}})

def insert(chat_id):
    """Insert a new user."""
    user_id = int(chat_id)
    user_det = {
        "_id": user_id,
        "file_id": None,
        "caption": None,
        "daily": 0,
        "date": 0,
        "uploadlimit": 1288490188,  # Default limit
        "used_limit": 0,
        "usertype": "Free",
        "prexdate": None,
    }
    dbcol.update_one({"_id": user_id}, {"$setOnInsert": user_det}, upsert=True)

def addthumb(chat_id, file_id):
    """Save a thumbnail for the user."""
    dbcol.update_one({"_id": chat_id}, {"$set": {"file_id": file_id}})

def delthumb(chat_id):
    """Delete the user's thumbnail."""
    dbcol.update_one({"_id": chat_id}, {"$set": {"file_id": None}})

def addcaption(chat_id, caption):
    """Save a caption for the user."""
    dbcol.update_one({"_id": chat_id}, {"$set": {"caption": caption}})

def delcaption(chat_id):
    """Delete the user's caption."""
    dbcol.update_one({"_id": chat_id}, {"$set": {"caption": None}})

def dateupdate(chat_id, date):
    """Update the user's date."""
    dbcol.update_one({"_id": chat_id}, {"$set": {"date": date}})

def used_limit(chat_id, used):
    """Update the user's used limit."""
    dbcol.update_one({"_id": chat_id}, {"$set": {"used_limit": used}})

def usertype(chat_id, type):
    """Update the user's type."""
    dbcol.update_one({"_id": chat_id}, {"$set": {"usertype": type}})

def uploadlimit(chat_id, limit):
    """Update the user's upload limit."""
    dbcol.update_one({"_id": chat_id}, {"$set": {"uploadlimit": limit}})

def addpre(chat_id):
    """Add a premium expiry date for the user."""
    date = add_date()
    dbcol.update_one({"_id": chat_id}, {"$set": {"prexdate": date[0]}})

def addpredata(chat_id):
    """Remove premium expiry date for the user."""
    dbcol.update_one({"_id": chat_id}, {"$set": {"prexdate": None}})

def daily(chat_id, date):
    """Update the user's daily limit."""
    dbcol.update_one({"_id": chat_id}, {"$set": {"daily": date}})

def find(chat_id):
    """Find a user's file and caption."""
    user = dbcol.find_one({"_id": chat_id}, {"file_id": 1, "caption": 1})
    if user:
        return [user.get("file_id"), user.get("caption")]
    return [None, None]

def getid():
    """Get all user IDs."""
    return [user["_id"] for user in dbcol.find({}, {"_id": 1})]

def delete(chat_id):
    """Delete a user."""
    dbcol.delete_one({"_id": chat_id})

def find_one(chat_id):
    """Find a single user."""
    return dbcol.find_one({"_id": chat_id})
