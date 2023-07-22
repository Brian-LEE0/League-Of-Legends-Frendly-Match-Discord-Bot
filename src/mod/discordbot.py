import discord
from datetime import datetime, timedelta
import pytz
import re
from mod.logger import setup_logger
from mod.crud.id import generate_uuid

KST = pytz.timezone('Asia/Seoul')
now = datetime.now(KST)

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(description = "롤 내전을 위한 봇 입니다",intents=intents) # Create a bot object
logger = setup_logger() # Setup the logger
Match = dict()
DL_NameMap = dict() # Discord Mention - League Name Map ex) {<@!123456789> : "Hide on bush"}

regex_time = re.compile(r'^\d{1,2}$')

class match_info():
    def __init__(self, creator, notion_message, notion_str, max) :
        self.creator = creator
        self.notion_msg = notion_message
        self.notion_str = notion_str
        self.call_everyone_msg = None
        self.players : set = set()
        self.max = max
        
    def __len__(self) :
        return len(self.players)
    
    async def add_player(self, user, interaction) :
        if self.is_player_exist(user) :
            await interaction.response.send_message(f"이미 내전을 신청한 유저입니다.", ephemeral=True)
            return False
        self.players.add(user)
        ctn = self.notion_str.split("\n")
        ctn[2] = f"현재인원 : {len(self)}/{self.max}"
        ctn = "\n".join(ctn)
        logger.info(f"{interaction.channel.mention} {interaction.user} 참가 신청")
        await self.notion_msg.edit_original_response(content = ctn)
        if len(self) == self.max :
            self.call_everyone_msg = await self.call_everyone(interaction)
        else :
            await interaction.response.send_message(f"{interaction.user.mention} 님의 참가 신청이 완료 되었습니다.", ephemeral=True)
        return True
    
    async def remove_player(self, user, interaction) :
        if len(self) == self.max :
            await interaction.response.send_message(f"이미 매치가 완료되었습니다. 매치 관리자에게 문의 해주세요!", ephemeral=True)
            return False
        if not self.is_player_exist(user) :
            await interaction.response.send_message(f"신청 내역이 없습니다.", ephemeral=True)
            return False
        self.players.remove(user)
        ctn = self.notion_str.split("\n")
        ctn[2] = f"현재인원 : {len(self)}/{self.max}"
        ctn = "\n".join(ctn)
        logger.info(f"{interaction.channel.mention} {interaction.user} 참가 철회")
        if self.call_everyone_msg :
            await self.call_everyone_msg.delete_original_response()
            self.call_everyone_msg = None
        await self.notion_msg.edit_original_response(content = ctn)
        await interaction.response.send_message(f"{interaction.user.mention} 님의 참가 신청이 철회 되었습니다.", ephemeral=True)
        return True
        
    def is_player_exist(self, player) :
        return player in self.players
    
    def cur_player_league(self, separator = " ") :
        players = [DL_NameMap[p.mention] for p in self.players]
        ctx = separator.join(players)
        return ctx
    
    def cur_player_mention(self, separator = " ") :
        players = [p.mention for p in self.players]
        ctx = separator.join(players)
        return ctx
    
    def cur_player_embed(self):
        embed=discord.Embed(
            title = "참가자들 전적 보러가기!!",
            url = "https://www.op.gg/multisearch/kr?summoners=" + self.cur_player_league(",").replace(" " , ""),
            color = discord.Color.green()
        )
        id, lid = str(), str()
        id = [p.display_name for p in self.players]
        id_str = "\n".join(id)
        lid_str = self.cur_player_league("\n")
        
        embed.add_field(name="디스코드 닉네임", value=id_str, inline=True)
        embed.add_field(name="롤 닉네임", value=lid_str, inline=True)
        
        return embed

    async def call_everyone(self, interaction):
        embed = self.cur_player_embed()
        ctx = self.cur_player_mention()
        after30m = (now + timedelta(minutes=30)).strftime("%H시%M분")
        
        msg = f"{ctx}\n내전이 **{after30m}**에 시작될 예정입니다\n참가자 모두 빠짐없이 확인해주세요!"
        return await interaction.response.send_message(msg, embed=embed)
        
    async def del_message(self) :
        if self.call_everyone_msg :
            await self.call_everyone_msg.delete_original_response()
            self.call_everyone_msg = None
        await self.notion_msg.delete_original_response()

class MatchJoinView(discord.ui.View):
    def __init__(self, key, timeout = None):
        super().__init__(timeout=timeout)
        self.key = key
    
    @discord.ui.button(label="참가 신청",style=discord.ButtonStyle.green)
    async def join(self, button, interaction):
        logger.info(f"push join button id : {button.custom_id} key : {self.key}")
        match = Match[self.key]
        if not match.is_player_exist(interaction.user) :
            await interaction.response.send_modal(MatchJoinForm(interaction.message,self.key,interaction.user))
        else :
            await interaction.response.send_message(f"이미 내전을 신청한 유저입니다.", ephemeral=True)
            
    @discord.ui.button(label="참가 철회", style=discord.ButtonStyle.red) 
    async def unjoin(self, button, interaction):
        logger.info(f"push unjoin button id : {button.custom_id} key : {self.key}")
        match = Match[self.key]
        await match.remove_player(interaction.user, interaction)
        
    @discord.ui.button(label="내전 정보", style=discord.ButtonStyle.blurple) 
    async def match_info(self, button, interaction):
        logger.info(f"push match_info button id : {button.custom_id} key : {self.key}")
        match = Match[self.key]
        embed = match.cur_player_embed()
        msg = f"총 인원 : {len(match)}/{match.max}"
        await interaction.response.send_message(msg, embed=embed, ephemeral=True) # Send a message with our View class that contains the button
        
    @discord.ui.button(label="내전 취소", style=discord.ButtonStyle.gray, emoji = "❌")
    async def destroy(self, button, interaction):
        logger.info(f"push destroy button id : {button.custom_id} key : {self.key}")
        match = Match[self.key]
        if match.creator.mention != interaction.user.mention :
            await interaction.response.send_message(f"{match.creator.mention}님이 만든 내전을 삭제했습니다.\n{match.cur_player_mention()}\n내전이 취소되었습니다.") # Send a message with our View class that contains the button
            Match.pop(self.key)
            await match.del_message()
        else :
            await interaction.response.send_message(f"{interaction.user.mention}님이 생성한 매치가 아닙니다.", ephemeral=True)
    


class MatchJoinForm(discord.ui.Modal):
    def __init__(self, message, key, user):
        super().__init__(title = "참가 신청서")
        self.user = user
        self.key = key
        self.message = message

        self.league_name = discord.ui.InputText(
            style=discord.InputTextStyle.singleline,
            label="리그오브레전드 닉네임",
            placeholder="ex) Hide on bush",
            value = DL_NameMap.get(self.user.mention),
            max_length = 16,
            )
        self.add_item(self.league_name)
        
        # self.hour = discord.ui.InputText(
        #     style=discord.InputTextStyle.short,
        #     label="시 (ex. 23) // 게임 시작 가능한 시간",
        #     placeholder= str(now.hour).zfill(2),
        #     value = str(now.hour).zfill(2),
        #     max_length = 2,
        #     )
        # self.add_item(self.hour)
        
        # self.minute = discord.ui.InputText(
        #     style=discord.InputTextStyle.short,
        #     label="분 (ex. 59)  // 게임 시작 가능한 시간",
        #     placeholder = str(now.minute).zfill(2),
        #     value = str(now.minute).zfill(2),
        #     max_length = 2,
        #     )
        # self.add_item(self.minute)
        
        self.suggestion = discord.ui.InputText(
            style=discord.InputTextStyle.long,
            label="기타 건의사항이 있으면 알려주세요",
            required = False,
            max_length = 500,
            )
        self.add_item(self.suggestion)
        
    async def callback(self, interaction) :
        #if() : # league name is exist
        DL_NameMap[self.user.mention] = self.league_name.value
        await Match[self.key].add_player(self.user, interaction)
        if self.suggestion.value :
            logger.info(f"Suggestion : {self.suggestion.value}")
        
        # if regex_time.match(self.hour.value) and regex_time.match(self.minute.value) :
        #     await Match[self.key].add_player(self.user, interaction)
        #     if self.suggestion.value :
        #         logger.info(f"Suggestion : {self.suggestion.value}")
        # else :
        #     await self.on_error(error=Exception("시간을 다시 입력해주세요"),interaction=interaction)
        
########################## BOT COMMANDS ##########################     
    
@bot.slash_command(name="내전생성", description = "ex) /내전생성 {@리그오브레전드} {10}") # Create a slash command
async def create_frendly_match(ctx, everyone: str, max: int = 10):
    global Match
    key = generate_uuid()
    if key in Match :
        await ctx.response.send_message("이미 내전을 생성했습니다. \"/내전취소\"를 해주세요.", ephemeral=True)
    else :
        logger.info(f"{ctx.channel.name} {ctx.author.name} 내전 생성 완료")
        notion_str = f"{everyone}\n{ctx.author.mention} 님이 내전을 생성하였습니다. 참가를 원하시는 분은 아래 버튼을 눌러주세요.\n현재인원 : 0/{max}"
        interaction = await ctx.response.send_message(notion_str, view=MatchJoinView(key))
        Match[key] = match_info(ctx.author, interaction, notion_str, max)
        logger.info(f"Match key : {key}")

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
    logger.info("Launching bot...") # Log that the bot is launching
    bot.run(token)

