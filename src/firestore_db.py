from google.cloud import firestore
from datetime import datetime
from .config import LONDON_TZ
import os

# Initialize Firestore client
db = None

def init_firestore():
    """Initialize Firestore client"""
    global db
    try:
        db = firestore.Client()
        print("✅ Firestore client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Firestore: {e}")
        db = None

def get_guild_log(guild_id):
    """Get the daily collection for a specific guild"""
    if not db:
        return None
    return db.collection("wish_log").document(str(guild_id)).collection("daily")

def get_today_date():
    """Get today's date in London timezone as YYYY-MM-DD"""
    london_time = datetime.now(LONDON_TZ)
    return london_time.strftime("%Y-%m-%d")

async def record_user(guild_id, user_id, on_time=True):
    """Record a user as either wished on time or shamed"""
    if not db:
        print("❌ Firestore not initialized, cannot record user")
        return False
    
    try:
        today = get_today_date()
        doc_ref = get_guild_log(guild_id).document(today)
        field = "wished" if on_time else "shamed"
        
        # Use arrayUnion to avoid duplicates
        doc_ref.set({field: firestore.ArrayUnion([str(user_id)])}, merge=True)
        print(f"✅ Recorded user {user_id} as {'wished' if on_time else 'shamed'} for guild {guild_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to record user {user_id}: {e}")
        return False

def get_day_log(guild_id, date_str=None):
    """Get the wish/shame log for a specific day"""
    if not db:
        return {"wished": [], "shamed": []}
    
    try:
        if date_str is None:
            date_str = get_today_date()
        
        doc = get_guild_log(guild_id).document(date_str).get()
        return doc.to_dict() if doc.exists else {"wished": [], "shamed": []}
    except Exception as e:
        print(f"❌ Failed to get day log for {date_str}: {e}")
        return {"wished": [], "shamed": []}

def get_daily_wishers(guild_id, date_str=None):
    """Get list of users who wished on time for a specific day"""
    try:
        log = get_day_log(guild_id, date_str)
        return log.get("wished", [])
    except Exception as e:
        print(f"❌ Failed to get daily wishers for guild {guild_id}: {e}")
        return []

def get_daily_shamers(guild_id, date_str=None):
    """Get list of users who were shamed for a specific day"""
    try:
        log = get_day_log(guild_id, date_str)
        return log.get("shamed", [])
    except Exception as e:
        print(f"❌ Failed to get daily shamers for guild {guild_id}: {e}")
        return []

def user_already_recorded_today(guild_id, user_id, field_type="wished"):
    """Check if user is already recorded for today"""
    try:
        today_log = get_day_log(guild_id)
        field = "wished" if field_type == "wished" else "shamed"
        return str(user_id) in today_log.get(field, [])
    except Exception as e:
        print(f"❌ Failed to check if user {user_id} already recorded: {e}")
        return False

def get_leaderboard(guild_id):
    """Generate leaderboard for a specific guild"""
    if not db:
        return {"top_wishers": [], "top_shamers": []}
    
    try:
        wished_counter = {}
        shamed_counter = {}
        
        # Get all daily documents for this guild
        guild_collection = get_guild_log(guild_id)
        if not guild_collection:
            return {"top_wishers": [], "top_shamers": []}
        
        docs = guild_collection.stream()
        
        # Process documents (might be empty for new guilds)
        doc_count = 0
        for doc in docs:
            doc_count += 1
            data = doc.to_dict()
            if not data:  # Skip empty documents
                continue
            
            # Count wishes
            for user in data.get("wished", []):
                wished_counter[user] = wished_counter.get(user, 0) + 1
            
            # Count shames
            for user in data.get("shamed", []):
                shamed_counter[user] = shamed_counter.get(user, 0) + 1
        
        print(f"📊 Processed {doc_count} documents for guild {guild_id} leaderboard")
        
        return {
            "top_wishers": sorted(wished_counter.items(), key=lambda x: x[1], reverse=True),
            "top_shamers": sorted(shamed_counter.items(), key=lambda x: x[1], reverse=True)
        }
    except Exception as e:
        print(f"❌ Failed to generate leaderboard for guild {guild_id}: {e}")
        return {"top_wishers": [], "top_shamers": []} 