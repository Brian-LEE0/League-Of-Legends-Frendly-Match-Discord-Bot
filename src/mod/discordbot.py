import discord
Match = dict()
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(description="롤 내전을 위한 봇 입니다", intents=intents)  # Create a bot object

from mod.data.match import MatchInfo
from mod.util.logger import logger
from mod.util.uuid import generate_uuid
from mod.util.time import TIME as T
from mod.consts import *

from view.discord_view import *


########################## BOT COMMANDS ##########################     

@bot.slash_command(name="내전생성", description="ex) /내전생성 {@리그오브레전드} {10}")  # Create a slash command
async def create_frendly_match(
    ctx, 
    everyone: str,
    hour: discord.commands.Option(str, "시", choices=list(HOUR_CANDIDATE.keys())),
    minute: discord.commands.Option(str, "분", choices=list(MIN_CANDIDIATE.keys())),
    max: discord.commands.Option(int, "내전 최대 인원", default=10),
    ):
    global Match
    # 12 to 24
    hour = HOUR_CANDIDATE[hour]
    minute = MIN_CANDIDIATE[minute]
    
    # generate key
    key = generate_uuid()
    
    min_start_time = T.get_datetime(hour,minute)
    str_time = min_start_time.strftime(f"%p %I시 %M분").replace("AM", "오전").replace("PM", "오후")
    notion_str = f"{everyone}\n{ctx.author.mention} 님이 내전을 생성하였습니다.\n내전이 **{str_time} 이후**에 시작 될 예정입니다.\n참가를 원하시는 분은 아래 **버튼**을 눌러주세요.\n현재인원 : 0/{max}"
    
    # send msg
    _ = await ctx.response.send_message(f"{ctx.author.mention}님이 내전을 생성하였습니다.", ephemeral=True, delete_after=3)
    notion_msg = await ctx.channel.send(notion_str, view=MatchJoinView(key))
    
    # make match class
    Match[key] = MatchInfo(ctx.author, min_start_time, notion_msg.id, max)
    
    # logging
    logger.info(f"generate notion msg : {notion_msg.id}")
    logger.info(f"Match key : {key} generator : {ctx.author.name} / min_start_time : {min_start_time} / max : {max} / channel : {ctx.channel.name}")



def run_bot(token):
    logger.info("Launching bot...")  # Log that the bot is launching
    bot.run(token)