


import os
import time

from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", default="development")

def seek_confirmation():
    if APP_ENV=="development" and input("CONTINUE? (Y/N): ").upper() != "Y":
        print("EXITING...")
        exit()

def server_sleep(seconds=None):
    seconds = seconds or (6 * 60 * 60) # 6 hours
    if APP_ENV == "production":
        print(f"SERVER SLEEPING...")
        time.sleep(seconds)
