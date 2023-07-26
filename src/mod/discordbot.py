import discord
Match = dict()
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(description="롤 내전을 위한 봇 입니다", intents=intents)  # Create a bot object

from mod.data.match import MatchInfo

from mod.util.logger import logger

from mod.util.uuid import generate_uuid
from mod.util.time import TIME as T

from view.discord_view import *


########################## BOT COMMANDS ##########################     

hour_candidate=[]
for i in range(1,13) :
    hour_candidate.append("오전 " + f"{i}".zfill(2) +"시")
for i in range(1,13) :
    hour_candidate.append("오후 " + f"{i}".zfill(2) +"시")

min_candidate=[]
for i in range(0,60,10) :
    min_candidate.append(f"{i}".zfill(2) + "분")

@bot.slash_command(name="내전생성", description="ex) /내전생성 {@리그오브레전드} {10}")  # Create a slash command
async def create_frendly_match(
    ctx, 
    everyone: str,
    hour: discord.commands.Option(str, "시", choices=hour_candidate),
    minute: discord.commands.Option(str, "분", choices=min_candidate),
    max: discord.commands.Option(int, "내전 최대 인원", default=10),
    ):
    global Match
    # 12 to 24
    hour = hour.replace("시","")
    minute = int(minute.replace("분",""))
    ampm = hour.split()[0]
    hour12 = int(hour.split()[1])
    hour24 = hour12 + 12 if ampm == "오후" else hour12
    
    # generate key
    key = generate_uuid()
    print(hour24,minute)
    
    min_start_time = T.get_datetime(hour24,minute)
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
        


# @bot.slash_command(name="내전정보", description = "ex) /내전정보") # Create a slash command
# async def info_frendly_match(ctx):
#     global Match
#     key = ctx.channel.mention
#     if key in Match :
#         embed = Match[key].cur_player_embed()
#         msg = f"총 인원 : {len(Match[key])}/{Match[key].max}"
#         await ctx.response.send_message(msg, embed=embed, ephemeral=True) # Send a message with our View class that contains the button
#     else :
#         await ctx.response.send_message("현재 {ctx.author.mention}님이 생성한 매치가 없습니다.", ephemeral=True) # Send a message with our View class that contains the button


# @bot.slash_command(name="내전취소", description = "ex) /내전취소") # Create a slash command
# async def remove_frendly_match(ctx):
#     global Match
#     key = ctx.channel.mention
#     if not key in Match or ctx.author != Match[key].creator :
#         await ctx.response.send_message("현재 {ctx.author.mention}님이 생성한 매치가 없습니다.", ephemeral=True)
#     else :
#         await ctx.response.send_message(f"{ctx.author.mention}님이 만든 내전을 삭제했습니다.\n{Match[key].cur_player_mention()}\n내전이 취소되었습니다.") # Send a message with our View class that contains the button
#         await Match[key].del_message()
#         Match.pop(key)

########################## BOT COMMANDS ##########################   

def run_bot(token):
    logger.info("Launching bot...")  # Log that the bot is launching
    bot.run(token)