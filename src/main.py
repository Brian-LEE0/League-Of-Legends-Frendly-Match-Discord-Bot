import mod.discordbot
import os
from dotenv import load_dotenv

SERVICE_STATE = "svc"

if __name__ == "__main__":
    load_dotenv(f"./token_{SERVICE_STATE}.env") # load all the variables from the env file
    mod.discordbot.run_bot(os.environ['BOT_TOKEN'])