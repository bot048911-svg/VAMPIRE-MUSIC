from pyrogram import Client
import os
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

app = Client("my_account", api_id=api_id, api_hash=api_hash)

with app:
    session_string = app.export_session_string()
    print("\n" + "="*80)
    print("Your Pyrogram session string is:")
    print("="*80)
    print(session_string)
    print("="*80)
    print("\nPlease save this in your .env file as SESSION=")
