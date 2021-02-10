


import os

from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", default="development")

def seek_confirmation():
    if APP_ENV=="development" and input("CONTINUE? (Y/N): ").upper() != "Y":
        print("EXITING...")
        exit()
