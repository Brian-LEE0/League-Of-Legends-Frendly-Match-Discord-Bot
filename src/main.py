import mod.discordbot
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv("./token.env") # load all the variables from the env file
    mod.discordbot.run_bot(os.environ['BOT_TOKEN'])