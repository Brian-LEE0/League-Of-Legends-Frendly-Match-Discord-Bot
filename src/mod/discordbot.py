
import discord
from datetime import datetime as dt
import pytz
import re
from table2ascii import table2ascii as t2a, PresetStyle
from mod.logger import setup_logger

KST = pytz.timezone('Asia/Seoul')
now = dt.now(KST)

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents) # Create a bot object
logger = setup_logger() # Setup the logger
Match = dict()
DL_NameMap = dict() # Discord Mention - League Name Map ex) {<@!123456789> : "Hide on bush"}

regex_time = re.compile(r'^\d{1,2}$')

class match_info():
    def __init__(self, notion_message, max) :
        self.notion_message = notion_message
        self.players : set = set()
        self.max = max
    
    def add_player(self, user) :
        self.players.add(user)
    
    def remove_player(self, user) :
        self.players.remove(user)
        
    def is_exist(self, player) :
        return player in self.players
    
    def call_players(self) :
        ctx = str()
        for p in self.players :
            ctx += f"{p.mention}\n"
        return ctx
    
    def __len__(self) :
        return len(self.players)
    
    async def del_message(self) :
        await self.notion_message.delete_original_response()
        
class MatchJoinButton(discord.ui.View):
    @discord.ui.button(label="참가 신청", style=discord.ButtonStyle.green)
    async def join(self, button, interaction):
        match_channel = interaction.message.channel.mention
        match_creator = interaction.message.content.split("\n")[1].split(" ")[0]
        key = f"{match_channel},{match_creator}"
        if not Match[key].is_exist(interaction.user) :
            await interaction.response.send_modal(MatchJoinForm(interaction.message,key,interaction.user))
        else :
            await interaction.response.send_message(f"이미 내전을 신청한 유저입니다.", ephemeral=True)
            
        
    @discord.ui.button(label="참가 철회", style=discord.ButtonStyle.red) 
    async def unjoin(self, button, interaction):
        match_channel = interaction.message.channel.mention
        match_creator = interaction.message.content.split("\n")[1].split(" ")[0]
        key = f"{match_channel},{match_creator}"
        if  Match[key].is_exist(interaction.user) :
            Match[key].remove_player(interaction.user)
            everyone = interaction.message.content.split("\n")[0]
            logger.info(f"{match_channel} {interaction.user} 참가 철회")
            await interaction.message.edit(content = f"{everyone}\n{match_creator} 님이 내전을 생성하였습니다. 현재인원 : {len(Match[key])}/{Match[key].max}")
            await interaction.response.send_message(f"{interaction.user.mention} 님의 참가 신청이 철회 되었습니다.", ephemeral=True)
        else :
            await interaction.response.send_message(f"신청 내역이 없습니다.", ephemeral=True)
    


class MatchJoinForm(discord.ui.Modal):
    def __init__(self, message, key, user):
        super().__init__(title = "참가 신청서")
        self.user = user
        self.key = key
        self.message = message

        self.league_name = discord.ui.InputText(
            style=discord.InputTextStyle.singleline,
            label="(필수) 리그오브레전드 닉네임",
            placeholder="ex) Hide on bush",
            value = DL_NameMap.get(self.user.mention),
            max_length = 16,
            )
        self.add_item(self.league_name)
        
        self.hour = discord.ui.InputText(
            style=discord.InputTextStyle.short,
            label="(필수) 게임 참가 가능한 시간을 알려주세요\n시 (ex. 23)",
            placeholder= str(now.hour),
            value = str(now.hour),
            max_length = 2,
            )
        self.add_item(self.hour)
        
        self.minute = discord.ui.InputText(
            style=discord.InputTextStyle.short,
            label="분 (ex. 59)",
            placeholder = str(now.minute),
            value = str(now.minute),
            max_length = 2,
            )
        self.add_item(self.minute)
        
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
        
        if regex_time.match(self.hour.value) and regex_time.match(self.minute.value) :
            Match[self.key].add_player(self.user)
            everyone = self.message.content.split("\n")[0]
            if self.suggestion.value :
                logger.info(f"Suggestion : {self.suggestion.value}")
            logger.info(f"{self.key.split(',')[0]} {self.user.mention} 참가 신청")
            await self.message.edit(content = f"{everyone}\n{self.key.split(',')[1]} 님이 내전을 생성하였습니다. 현재인원 : {len(Match[self.key])}/{Match[self.key].max}")
            await interaction.response.send_message(f"{interaction.user.mention} 님의 참가 신청이 완료 되었습니다.", ephemeral=True)
        else :
            await self.on_error(error=Exception("시간을 다시 입력해주세요"),interaction=interaction)
            
        
    
@bot.slash_command(name="내전생성") # Create a slash command
async def create_frendly_match(ctx, everyone: str, max: int = 10):
    global Match
    key = f"{ctx.channel.mention},{ctx.author.mention}"
    if key in Match :
        await ctx.respond("이미 내전을 생성했습니다. \"/내전취소\"를 해주세요.", ephemeral=True)
    else :
        logger.info(f"{ctx.channel.name} {ctx.author.name} 내전 생성 완료")
        interaction = await ctx.respond(f"{everyone}\n{ctx.author.mention} 님이 내전을 생성하였습니다. 참가를 원하시는 분은 아래 버튼을 눌러주세요.\n 현재인원 : 0/{max}", 
                          view=MatchJoinButton()
                          )
        # logger.info(f"interaction : {dir(interaction)}")
        Match[key] = match_info(interaction, max)


@bot.slash_command(name="내전정보") # Create a slash command
async def info_frendly_match(ctx):
    global Match
    key = f"{ctx.channel.mention},{ctx.author.mention}"
    if key in Match :
        embed=discord.Embed(
            title="현재 참가 신청자 목록",
            color=discord.Color.green()
        )
        id = "ㅇㅅㅇ\n게이\n"
        lid = "ㅇㅅㅇ\n레즈\n"
        for p in Match[key].players :
            id += f"{p.display_name}\n"
            lid += f"{DL_NameMap.get(p.mention)}\n"
        
        embed.add_field(name="디스코드 닉네임", value=id, inline=True)
        embed.add_field(name="롤 닉네임", value=lid, inline=True)
        msg = f"총 인원 : {len(Match[key])}/{Match[key].max}"
        await ctx.respond(msg, embed=embed, ephemeral=True) # Send a message with our View class that contains the button
    else :
        await ctx.respond("현재 {ctx.author.mention}님이 생성한 매치가 없습니다.", ephemeral=True) # Send a message with our View class that contains the button
        
    
@bot.slash_command(name="내전취소") # Create a slash command
async def remove_frendly_match(ctx):
    global Match
    key = f"{ctx.channel.mention},{ctx.author.mention}"
    
    if not key in Match :
        await ctx.respond("현재 {ctx.author.mention}님이 생성한 매치가 없습니다.", ephemeral=True)
    else :
        await ctx.respond(f"{ctx.author.mention}님이 만든 내전을 삭제했습니다.\n{Match[key].call_players()}내전이 취소되었습니다.") # Send a message with our View class that contains the button
        await Match[key].del_message()
        Match.pop(key)

def run_bot(token):
    logger.info("Launching bot...") # Log that the bot is launching
    bot.run(token)
