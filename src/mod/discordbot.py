import discord
Match = dict()
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(description="롤 내전을 위한 봇 입니다", intents=intents)  # Create a bot object

from mod.banpick import BanPick
from mod.data.match import MatchInfo
from mod.data.consts import *

from mod.util.logger import logger
from mod.util.uuid import generate_uuid
from mod.util.time import TIME as T

from view.discord_view import *
from view.competition_view import *

import mod.util.mongo as mongo

import re


########################## BOT COMMANDS ##########################     

@bot.slash_command(name="롤내전", description="ex) /롤내전 {@리그오브레전드} {오후 10시} {30분}")  # Create a slash command
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
    notion_str = f"{everyone}\n{ctx.author.mention} 님이 **롤** 내전을 생성하였습니다.\n내전이 **{str_time} 이후**에 시작 될 예정입니다.\n참가를 원하시는 분은 아래 **버튼**을 눌러주세요.\n현재인원 : 0/{max}"
    
    # send msg
    _ = await ctx.response.send_message(f"{ctx.author.mention}님이 **롤** 내전을 생성하였습니다.", ephemeral=True, delete_after=3)
    notion_msg = await ctx.channel.send(notion_str, view=MatchJoinView(key))
    tool_msg = await ctx.channel.send(view=ToolView(key))
    
    # make match class
    Match[key] = MatchInfo(key, ctx.author, setted_time, notion_msg.id, tool_msg.id, max)
    
    # logging
    logger.info(f"generate notion msg : {notion_msg.id}")
    logger.info(f"Match key : {key} generator : {ctx.author.name} / min_start_time : {setted_time} / max : {max} / channel : {ctx.channel.name}")

@bot.slash_command(name="발로내전", description="ex) /발로내전 {@발로란트} {오후 10시} {30분}")  # Create a slash command
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
    notion_str = f"{everyone}\n{ctx.author.mention} 님이 **발로란트** 내전을 생성하였습니다.\n내전이 **{str_time} 이후**에 시작 될 예정입니다.\n참가를 원하시는 분은 아래 **버튼**을 눌러주세요.\n현재인원 : 0/{max}"
    
    # send msg
    _ = await ctx.response.send_message(f"{ctx.author.mention}님이 **발로란트** 내전을 생성하였습니다.", ephemeral=True, delete_after=3)
    notion_msg = await ctx.channel.send(notion_str, view=MatchJoinView(key, game="val"))
    tool_msg = await ctx.channel.send(view=ToolView(key, game="val"))
    
    # make match class
    Match[key] = MatchInfo(key, ctx.author, setted_time, notion_msg.id, tool_msg.id, max, game="val")
    
    # logging
    logger.info(f"generate val notion msg : {notion_msg.id}")
    logger.info(f"Match key : {key} generator : {ctx.author.name} / min_start_time : {setted_time} / max : {max} / channel : {ctx.channel.name}")
    
@bot.slash_command(name="롤대회", description="")  # Create a slash command
async def create_competition_match(
    ctx,
    max: discord.commands.Option(int, "최대 인원", default=999),
    match_id: discord.commands.Option(str, "대회 키", default="")
    ):
    # generate key
    if match_id == "":
        match_id = generate_uuid()
    
    players_db = mongo.Player()
    
    notion_str = f"현재인원 : {len(players_db.get_players(match_id))}명"
    notion_msg = await ctx.channel.send(notion_str, view=CompetitionJoinView(match_id, game="lol"))
    
    matches_db = mongo.Match()
    matches_db.create_match("lol", match_id, notion_msg.id, max)
    _ = await ctx.response.send_message(f"{ctx.author.mention}님이 **롤** 대회를 생성하였습니다.", ephemeral=True, delete_after=3)
    
@bot.slash_command(name="벤픽", description="")  # Create a slash command
async def create_banpick(
    ctx):
    bp = BanPick()
    await ctx.channel.send(f"""벤픽 링크가 생성되었습니다!
[블루팀]({bp.get_ready_link(is_red=False)})
[레드팀]({bp.get_ready_link(is_red=True)})""")
    
    return
    
    
    
@bot.event
async def on_ready():
    matchs_db = mongo.Match()
    matches = matchs_db.get_all_match()
    for match in matches:
        logger.info(f"match : {match}")
        bot.add_view(CompetitionJoinView(match["match_id"], game=match["game"]))
    
    await OPGGVal.get_map()
    
    
    

# @bot.slash_command(name="시간변경", description="ex) /시간변경 {매치키} {@리그오브레전드} {오후 10시} {30분}")  # Create a slash command
# async def create_frendly_match(
#     ctx, 
#     match_key: str,
#     hour: discord.commands.Option(str, "시", choices=list(HOUR_CANDIDATE.keys())),
#     minute: discord.commands.Option(str, "분", choices=list(MIN_CANDIDIATE.keys())),
#     ):
#     await ctx.response.defer(ephemeral=True)
#     global Match
#     # 12 to 24
#     hour = HOUR_CANDIDATE[hour]
#     minute = MIN_CANDIDIATE[minute]
    
#     cur_match : MatchInfo | None = Match.get(match_key)
#     if not cur_match:
#         return await ctx.followup.send(f"{ctx.author.mention}님의 내전이 존재하지 않습니다.", ephemeral=True, delete_after=3)        
    
#     new_time = T.get_datetime(hour,minute)
#     await cur_match.change_time(new_time, ctx)
    
#     # logging
#     logger.info(f"change setted time: {new_time}, key: {match_key}")
    
#     return await ctx.followup.send(f"시간 변경 완료.", ephemeral=True, delete_after=3)   
    
    
# @bot.slash_command(name="선수삭제", description="ex) /선수삭제 {매치키} {@고삼토}")  # Create a slash command
# async def create_frendly_match(
#     ctx, 
#     match_key: str,
#     player_mention: str,
#     ):
#     await ctx.response.defer(ephemeral=True)
#     global Match
#     cur_match : MatchInfo | None = Match.get(match_key)
#     if not cur_match:
#         return await ctx.followup.send(f"{ctx.author.mention}\n님의 내전이 존재하지 않습니다.", ephemeral=True, delete_after=3)
    
#     user = cur_match.get_player_by_id(int(re.sub(r'[^0-9]', '', player_mention)))
#     if not user :
#         return await ctx.followup.send(f"{player_mention}\n존재하지 않는 유저 정보.", ephemeral=True, delete_after=3)
    
#     await cur_match.remove_player(user, ctx)
    
#     # logging
#     logger.info(f"remove user: {player_mention}, key: {match_key}")


def run_bot(token):
    logger.info("Launching bot...")  # Log that the bot is launching
    bot.run(token)