import discord
from mod.discordbot import bot
from mod.util.crud import *
from mod.util.logger import logger
from mod.util.time import TIME as T

class Match():
    def __init__(self) :
        self.d
        
class MatchInfo():
    def __init__(self, creator, min_start_time, notion_id, max):
        self.creator = creator
        self.notion_id = notion_id
        self.mention_everyone_id = None
        self.players: set = set()
        self.min_start_time = min_start_time
        self.max = max

    def __len__(self):
        return len(self.players)

    async def add_player(self, user, interaction):
        if self.is_player_exist(user):
            await interaction.response.send_message(f"이미 내전을 신청한 유저입니다.", ephemeral=True, delete_after=3)
            return False
        
        ctn = await self._get_msg_ctx_from_id(self.notion_id)
        if ctn is None:
            return False
        
        ctn = ctn.split("\n")
        self.players.add(user) # inc player
        ctn[-1] = f"현재인원 : {len(self)}/{self.max}"
        ctn = "\n".join(ctn)
        
        logger.info(f"{interaction.channel.mention} {interaction.user} 참가 신청")
        
        await self._edit_msg_from_id(self.notion_id, ctn) # edit msg
        if len(self) == self.max: # call everyone
            self.mention_everyone_id = await self.mention_everyone(interaction)
        else: # success msg
            await interaction.response.send_message(f"{interaction.user.mention} 님의 참가 신청이 완료 되었습니다.", ephemeral=True, delete_after=3)
        return True

    async def remove_player(self, user, interaction):
        if not self.is_player_exist(user):
            await interaction.response.send_message(f"신청 내역이 없습니다.", ephemeral=True, delete_after=3)
            return False
        
        ctn = await self._get_msg_ctx_from_id(self.notion_id)
        if ctn is None:
            return False
        
        ctn = ctn.split("\n")
        self.players.remove(user) # dec player
        ctn[-1] = f"현재인원 : {len(self)}/{self.max}"
        ctn = "\n".join(ctn)
        
        logger.info(f"{interaction.channel.mention} {interaction.user} 참가 철회")
        
        await self._edit_msg_from_id(self.notion_id, ctn) # edit msg
        if self.mention_everyone_id:
            await self._edit_msg_from_id(self.mention_everyone_id, "", delete=True)
            self.mention_everyone_id = None
        await interaction.response.send_message(f"{interaction.user.mention} 님의 참가 신청이 철회 되었습니다.", ephemeral=True, delete_after=3)
        return True

    def is_player_exist(self, player):
        return player in self.players

    def cur_player_league(self, separator=" "):
        players = [get_league_from_discord_id(did.mention) for did in self.players]
        ctx = separator.join(players)
        return ctx

    def cur_player_mention(self, separator=" "):
        players = [p.mention for p in self.players]
        
        ctx = separator.join(players)
        return ctx

    @staticmethod
    async def _edit_msg_from_id(mid, ctn, delete=False):
        msg = bot.get_message(mid)
        if msg is None:
            logger.info(f"fail to edit msg : {mid}")
            return False

        if delete:
            try:
                await msg.delete()
                logger.info(f"edit msg : {mid}")
                return True
            except:
                return False
        logger.info(f"edit msg : {mid}")
        await msg.edit(content=ctn)
        return True

    @staticmethod
    async def _get_msg_ctx_from_id(mid):
        msg = bot.get_message(mid)
        if msg is None:
            logger.info(f"fail to get msg from : {mid}")
            return None
        logger.info(f"get msg from : {mid}")
        return msg.content

    def cur_player_embed(self):
        embed = discord.Embed(
            title="참가자들 전적 보러가기!!",
            url="https://www.op.gg/multisearch/kr?summoners=" + self.cur_player_league(",").replace(" ", ""),
            color=discord.Color.green()
        )
        uid = [p.display_name for p in self.players]
        uid_str = "\n".join(uid)
        lid_str = self.cur_player_league("\n")
        embed.add_field(name="**내전 DB**", value="[**Link!**](https://docs.google.com/spreadsheets/d/1lSOKjcKNu0lI7EP87KEW2gYEBW4Y7HW8_KawxNuu1L0/edit?usp=sharing)", inline=False)
        embed.add_field(name="**디스코드 닉네임**", value=uid_str, inline=True)
        embed.add_field(name="**롤 닉네임**", value=lid_str, inline=True)
        

        return embed

    async def mention_everyone(self, interaction):
        embed = self.cur_player_embed()
        ctx = self.cur_player_mention()
        after15m = T.now_time_after_m(15)
        start_time = max(after15m,self.min_start_time).strftime("%p %I시 %M분").replace("AM", "오전").replace("PM", "오후")
        logger.info(f"mention_everyone, match will be start at {start_time}")
        msg = f"{ctx}\n내전이 **{start_time}**에 시작될 예정입니다\n참가자 모두 빠짐없이 확인해주세요!"
        mention_everyone_msg = await interaction.response.send_message(msg, embed=embed)
        mention_everyone_msg = await mention_everyone_msg.original_response()
        return mention_everyone_msg.id

    async def del_message(self):
        await self._edit_msg_from_id(self.mention_everyone_id, "", delete=True)
        await self._edit_msg_from_id(self.notion_id, "", delete=True)