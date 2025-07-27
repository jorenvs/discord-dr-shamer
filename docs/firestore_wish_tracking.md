# Firestore-Based Wish Tracking for Dr. Shamer Bot

## Overview

This document outlines the approach for tracking daily wishers and late ("shamed") users using Google Firestore in the Dr. Shamer Discord bot. The goal is to maintain a historical log of user wish activity without relying on a heavyweight database or incurring significant cost.

---

## Goals

- Record users who wished on time and those who were late ("shamed")
- Store this data per day
- Send a summary **wish message shortly after 11:11**, and a **summary shame message at 22:22**
- Retain up to 5 years of data for historical insights
- Provide a leaderboard function summarizing all-time wish/shame activity
- Avoid high-cost infrastructure

---

## Why Firestore?

Firestore provides a serverless, low-latency NoSQL database with a generous free tier that easily covers our expected usage:

### Free Tier (monthly)

- 50,000 reads
- 20,000 writes
- 1 GB storage

### Estimated Usage

- \~5 records/day
- \~1,825 documents over 5 years
- Total storage: \~0.35MB
- Reads/Writes well within free tier

Result: **Expected cost = \$0** for 5 years of usage.

---

## Data Model

Firestore Collection: `wish_log`

Each server (guild) is tracked independently using a nested structure. The collection stores a subcollection per guild ID, with daily documents inside.

**Structure:**

```
wish_log/
  <guild_id>/
    <YYYY-MM-DD>:
      wished: [...]
      shamed: [...]
```

Each document represents a day and stores two arrays:

```json
{
  "wished": ["@user1", "@user2"],
  "shamed": ["@user3", "@user4"]
}
```

### Document ID

Each document ID represents the UTC date in the format: `YYYY-MM-DD` (e.g., `2025-07-27`). The document is nested under its respective `guild_id` to ensure test servers and production are stored separately.

---

## Core Functions

### In-Memory Collection During 11:11 Window

To reduce latency and avoid excessive Firestore writes during the 11:11 wish window, use an in-memory set to track users who wished on time. This set is flushed to Firestore once, immediately after the summary is sent.

```python
today_wishers = set()

def register_wisher(user_id):
    today_wishers.add(user_id)

def flush_wishers_to_firestore():
    for user in today_wishers:
        record_user(user, on_time=True)
```

This allows fast reaction handling while still recording accurate historical data after the wish window.

### Add a Wisher or Shamed User

```python
from google.cloud import firestore
from datetime import datetime

db = firestore.Client()
def get_guild_log(guild_id):
    return db.collection("wish_log").document(guild_id).collection("daily")

def record_user(user_id, on_time=True):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    doc_ref = get_guild_log(guild_id).document(today)
    field = "wished" if on_time else "shamed"
    doc_ref.set({field: firestore.ArrayUnion([user_id])}, merge=True)
```

### Read Daily Log

```python
def get_day_log(date_str):
    doc = get_guild_log(guild_id).document(date_str).get()
    return doc.to_dict() if doc.exists else {"wished": [], "shamed": []}

def get_daily_wishers(date_str):
    doc = wish_log.document(date_str).get()
    return doc.to_dict().get("wished", []) if doc.exists else []

def get_daily_shamers(date_str):
    doc = wish_log.document(date_str).get()
    return doc.to_dict().get("shamed", []) if doc.exists else []
```

### Send Summary Messages

- **Wish Summary**: Triggered a few minutes after 11:11
- **Shame Summary**: Triggered at 22:22
- Fetch today's log, format message, send to channel
- Optionally clear or archive daily log

### Generate Leaderboard

```python
def get_leaderboard():
    wished_counter = {}
    shamed_counter = {}

    for guild in db.collection("wish_log").stream():
        for doc in guild.reference.collection("daily").stream():
        data = doc.to_dict()
        for user in data.get("wished", []):
            wished_counter[user] = wished_counter.get(user, 0) + 1
        for user in data.get("shamed", []):
            shamed_counter[user] = shamed_counter.get(user, 0) + 1

    return {
        "top_wishers": sorted(wished_counter.items(), key=lambda x: x[1], reverse=True),
        "top_shamed": sorted(shamed_counter.items(), key=lambda x: x[1], reverse=True)
    }
```

---

## Advantages

- Serverless and scalable
- Built-in concurrency and atomic writes
- No ops or infra maintenance
- GCP-native, works well with Cloud Run
