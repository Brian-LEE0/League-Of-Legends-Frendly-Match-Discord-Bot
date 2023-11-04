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

import re


########################## BOT COMMANDS ##########################     

@bot.slash_command(name="내전생성", description="ex) /내전생성 {@리그오브레전드} {오후 10시} {30분}")  # Create a slash command
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
    
    setted_time = T.get_datetime(hour,minute)
    str_time = setted_time.strftime(f"%p %I시 %M분").replace("AM", "오전").replace("PM", "오후")
    notion_str = f"{everyone}\n{ctx.author.mention} 님이 내전을 생성하였습니다.\n내전이 **{str_time} 이후**에 시작 될 예정입니다.\n참가를 원하시는 분은 아래 **버튼**을 눌러주세요.\n현재인원 : 0/{max}"
    
    # send msg
    _ = await ctx.response.send_message(f"{ctx.author.mention}님이 내전을 생성하였습니다.", ephemeral=True, delete_after=3)
    notion_msg = await ctx.channel.send(notion_str, view=MatchJoinView(key))
    
    # make match class
    Match[key] = MatchInfo(key, ctx.author, setted_time, notion_msg.id, max)
    
    # logging
    logger.info(f"generate notion msg : {notion_msg.id}")
    logger.info(f"Match key : {key} generator : {ctx.author.name} / min_start_time : {setted_time} / max : {max} / channel : {ctx.channel.name}")

@bot.slash_command(name="시간변경", description="ex) /시간변경 {매치키} {@리그오브레전드} {오후 10시} {30분}")  # Create a slash command
async def create_frendly_match(
    ctx, 
    match_key: str,
    hour: discord.commands.Option(str, "시", choices=list(HOUR_CANDIDATE.keys())),
    minute: discord.commands.Option(str, "분", choices=list(MIN_CANDIDIATE.keys())),
    ):
    await ctx.response.defer(ephemeral=True)
    global Match
    # 12 to 24
    hour = HOUR_CANDIDATE[hour]
    minute = MIN_CANDIDIATE[minute]
    
    cur_match : MatchInfo | None = Match.get(match_key)
    if not cur_match:
        return await ctx.followup.send(f"{ctx.author.mention}님의 내전이 존재하지 않습니다.", ephemeral=True, delete_after=3)        
    
    new_time = T.get_datetime(hour,minute)
    await cur_match.change_time(new_time, ctx)
    
    # logging
    logger.info(f"change setted time: {new_time}, key: {match_key}")
    
    return await ctx.followup.send(f"시간 변경 완료.", ephemeral=True, delete_after=3)   
    
    
@bot.slash_command(name="선수삭제", description="ex) /선수삭제 {매치키} {@고삼토}")  # Create a slash command
async def create_frendly_match(
    ctx, 
    match_key: str,
    player_mention: str,
    ):
    await ctx.response.defer(ephemeral=True)
    global Match
    cur_match : MatchInfo | None = Match.get(match_key)
    if not cur_match:
        return await ctx.followup.send(f"{ctx.author.mention}\n님의 내전이 존재하지 않습니다.", ephemeral=True, delete_after=3)
    
    user = cur_match.get_player_by_id(int(re.sub(r'[^0-9]', '', player_mention)))
    if not user :
        return await ctx.followup.send(f"{player_mention}\n존재하지 않는 유저 정보.", ephemeral=True, delete_after=3)
    
    await cur_match.remove_player(user, ctx)
    
    # logging
    logger.info(f"remove user: {player_mention}, key: {match_key}")


def run_bot(token):
    logger.info("Launching bot...")  # Log that the bot is launching
    bot.run(token)