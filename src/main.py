import asyncio
import os
from mod.discordbot import run_bot
from app.match_making import app
from multiprocessing import Process

SERVICE_STATE = os.environ['SERVICE_STATE'] if 'SERVICE_STATE' in os.environ else "dev"

def start_quart():
    app.run(host="0.0.0.0", port=7070, debug=True)

if __name__ == "__main__":
    #another process run start_quart
    p = Process(target=start_quart)
    p.start()
    
    run_bot(os.environ['BOT_TOKEN'])
    p.join()