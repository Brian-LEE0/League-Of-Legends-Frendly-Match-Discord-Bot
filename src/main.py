import os

SERVICE_STATE = os.environ['SERVICE_STATE'] if 'SERVICE_STATE' in os.environ else "dev"

if __name__ == "__main__":
    import mod.discordbot
    mod.discordbot.run_bot(os.environ['BOT_TOKEN'])