import datetime
import discord
from mod.discordbot import bot
from mod.util.crud import *
from mod.util.logger import logger
from mod.util.time import TIME as T
import mod.data.val_image as val_image
import mod.data.league_image as league_image
    
class Match():
    def __init__(self) :
        self.d
        
class MatchInfo():
    def __init__(self, key, creator, setted_time, notion_id, tool_id, max, game=""):
        self.key = key
        self.creator = creator
        self.notion_id = notion_id
        self.tool_id = tool_id
        self.mention_everyone_id = None
        self.players: list = list()
        self.setted_time = setted_time
        self.fixed_time = None
        self.max = max
        self.game = game

    def __len__(self):
        return len(self.players)

    async def add_player(self, user, interaction):
        if self.is_player_exist(user):
            await interaction.response.send_message(f"이미 내전을 신청한 유저입니다.", ephemeral=True, delete_after=3)
            return False
        
        ctx = await self._get_msg_ctx_from_id(self.notion_id)
        if ctx is None:
            return False
        
        self.players.append(user) # inc player
        
        ctx = ctx.split("\n")
        ctx[-1] = f"현재인원 : {len(self)}/{self.max}" if len(self) <= self.max else f"현재인원 : {self.max}/{self.max} 후보인원 : {len(self) - self.max}명"
        ctx = "\n".join(ctx)
        
        logger.info(f"{user.mention} {interaction.user} 참가 신청")
        
        await self._edit_msg_from_id(self.notion_id, content=ctx) # edit msg
        if len(self) >= self.max : # call everyone
            await self.mention_everyone(interaction)
        if interaction.response.is_done() :
            return await interaction.followup.send(content = f"{user.mention} 님의 참가 신청이 완료 되었습니다.", ephemeral=True, delete_after=3)
        return await interaction.response.send_message(content = f"{user.mention} 님의 참가 신청이 완료 되었습니다.", ephemeral=True, delete_after=3)
    

    async def remove_player(self, user, interaction):
        if not self.is_player_exist(user):
            await interaction.response.send_message(f"신청 내역이 없습니다.", ephemeral=True, delete_after=3)
            return False
        
        ctx = await self._get_msg_ctx_from_id(self.notion_id)
        if ctx is None:
            return False
        
        self.players.remove(user) # dec player
        
        ctx = ctx.split("\n")
        ctx[-1] = f"현재인원 : {len(self)}/{self.max}" if len(self) <= self.max else f"현재인원 : {self.max}/{self.max} 후보인원 : {len(self) - self.max}명"
        ctx = "\n".join(ctx)
        
        logger.info(f"{interaction.channel.mention} {interaction.user} 참가 철회")
        
        await self._edit_msg_from_id(self.notion_id, content=ctx) # edit msg
        if len(self) >= self.max : # call everyone
            await self.mention_everyone(interaction)
        if len(self) < self.max and self.mention_everyone_id is not None:
            await self._edit_msg_from_id(self.mention_everyone_id, content=ctx, delete=True)
            self.mention_everyone_id = None
            self.fixed_time = None
        if interaction.response.is_done() :
            return await interaction.followup.send(content = f"{user.mention} 님의 참가 신청이 철회 되었습니다.", ephemeral=True, delete_after=3)
        return await interaction.response.send_message(content = f"{user.mention} 님의 참가 신청이 철회 되었습니다.", ephemeral=True, delete_after=3)

    def is_player_exist(self, player):
        return player in self.players
    
    def get_player_by_id(self, player_id):
        for p in self.players:
            if p.id == player_id:
                return p
        return None

    def cur_player_league(self, separator=" "):
        players = [get_league_from_discord_id(did.mention + self.game) for did in self.players]
        ctx = separator.join(players)
        return ctx

    def cur_player_mention(self, separator=" "):
        players = [p.mention for p in self.players]
        
        ctx = separator.join(players)
        return ctx

    @staticmethod
    async def _edit_msg_from_id(mid, **kwargs):
        msg = bot.get_message(mid)
        if msg is None:
            logger.info(f"fail to edit msg : {mid}")
            return False

        if "delete" in kwargs.keys() and kwargs["delete"] is True:
            try:
                await msg.delete()
                logger.info(f"edit msg : {mid}")
                return True
            except:
                return False
        logger.info(f"edit msg : {mid}")
        
        await msg.edit(**kwargs)
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
        if self.game == "val":
            title="발로란트 내전 참가자"
        else :
            title="롤 내전 참가자"
            
        embed = discord.Embed(
            title=title,
            color=discord.Color.green()
        )
        
        player_info_list = []
        for p in self.players[:self.max] :
            did = p.mention
            lid = get_league_from_discord_id(did + self.game)
            linfo = get_league_info_from_league(lid + self.game)
            if self.game == "val":
                priority = {
                    "unrank" : 0,
                    "iron" : 1,
                    "bronze" : 2,
                    "silver" : 3,
                    "gold" : 4,
                    "platinum" : 5,
                    "diamond" : 6,
                    "ascendant" : 7,
                    "immortal" : 8,
                    "radiant" : 9,
                }.get(linfo["cur_tier"],0)
                
                cur_tier_and_most_3 =  val_image.TIER_TO_DISCORD.get(linfo["cur_tier"],linfo["cur_tier"])+" "
                cur_tier_and_most_3 += "".join([val_image.CHAMP_TO_DISCORD.get(most[0],most[0]) for most in linfo['most_3']])
            else:
                priority = {
                    "unranked" : 0,
                    "iron" : 1,
                    "bronze" : 2,
                    "silver" : 3,
                    "gold" : 4,
                    "platinum" : 5,
                    "emerald" : 6,
                    "diamond" : 7,
                    "master" : 8,
                    "grandmaster" : 9,
                    "challenger" : 10,
                }.get(linfo["cur_tier"],0)
            
                cur_tier_and_most_3 =  league_image.TIER_TO_DISCORD.get(linfo["cur_tier"],linfo["cur_tier"])+" "
                cur_tier_and_most_3 += "".join([league_image.CHAMP_TO_DISCORD.get(most[0],most[0]) for most in linfo['most_3']])
            
            player_info_list.append({
                "did" : did,
                "lid" : lid,
                "linfo" : linfo,
                "cur_tier_and_most_3" : cur_tier_and_most_3,
                "priority" : priority
            })
            
            player_info_list.sort(
                key=lambda x : x["priority"],
                reverse=True
            )
        
        middle_boundary = 5 if len(player_info_list) > 5 else len(player_info_list)
        max_boundary = self.max if len(player_info_list) > self.max else len(player_info_list)
        
        embed.add_field(name="**디코닉**", value="\n".join([p["did"] for p in player_info_list[:middle_boundary]]), inline=True)
        embed.add_field(name="**게임닉**", value="\n".join([p["lid"] for p in player_info_list[:middle_boundary]]), inline=True)
        embed.add_field(name="**티어&모스트**", value="\n".join([p["cur_tier_and_most_3"] for p in player_info_list[:middle_boundary]]), inline=True)
        
        if len(self) > 5 :
            embed.add_field(name = "",value= "", inline=False)
            embed.add_field(name="", value="\n".join([p["did"] for p in player_info_list[middle_boundary:max_boundary]]), inline=True)
            embed.add_field(name="", value="\n".join([p["lid"] for p in player_info_list[middle_boundary:max_boundary]]), inline=True)
            embed.add_field(name="", value="\n".join([p["cur_tier_and_most_3"] for p in player_info_list[middle_boundary:max_boundary]]), inline=True)
        if len(self) > self.max :
            embed.add_field(name="후보선수", value=", ".join([p.mention for p in self.players[self.max:]]), inline=True)
        return embed
    
    def get_draft_embed_and_list(self,player_info_list = [], team1=[],team2=[]):
        embed = discord.Embed(
            title="팀 드래프트",
            color=discord.Color.red()
        )
        
        if not player_info_list :
            for p in self.players[:self.max] :
                did = p.mention
                lid = get_league_from_discord_id(did + self.game)
                linfo = get_league_info_from_league(lid + self.game)
                if self.game == "val":
                    priority = {
                        "unrank" : 0,
                        "iron" : 1,
                        "bronze" : 2,
                        "silver" : 3,
                        "gold" : 4,
                        "platinum" : 5,
                        "diamond" : 6,
                        "ascendant" : 7,
                        "immortal" : 8,
                        "radiant" : 9,
                    }.get(linfo["cur_tier"],0)
                    cur_tier =  val_image.TIER_TO_DISCORD.get(linfo["cur_tier"],linfo["cur_tier"])
                else:
                    priority = {
                        "unranked" : 0,
                        "iron" : 1,
                        "bronze" : 2,
                        "silver" : 3,
                        "gold" : 4,
                        "platinum" : 5,
                        "emerald" : 6,
                        "diamond" : 7,
                        "master" : 8,
                        "grandmaster" : 9,
                        "challenger" : 10,
                    }.get(linfo["cur_tier"],0)
                    cur_tier =  league_image.TIER_TO_DISCORD.get(linfo["cur_tier"],linfo["cur_tier"])

                
                player_info_list.append({
                    "did" : did,
                    "lid" : lid,
                    "linfo" : linfo,
                    "cur_tier" : cur_tier,
                    "priority" : priority,
                    "selected": False
                })
                
                player_info_list.sort(
                    key=lambda x : x["priority"],
                    reverse=True
                )
                
        else :
            for p in player_info_list :
                p["selected"]=False
        team1_list = []
        team2_list = []
        
        for n in team1 :
            player_info_list[n]["selected"] = True
            team1_list.append(player_info_list[n]["cur_tier"] + player_info_list[n]["lid"])
        for n in team2 :
            player_info_list[n]["selected"] = True
            team2_list.append(player_info_list[n]["cur_tier"] + player_info_list[n]["lid"])
            
        while(len(team1_list) < 6):
            team1_list.append("ㅤ"*12)
        while(len(team2_list) < 6):
            team2_list.append("ㅤ"*12)
        
        embed.add_field(name="**1팀**", value= "\n".join(team1_list), inline=True)
        embed.add_field(name="**2팀**", value= "\n".join(team2_list), inline=True)
        
        not_selected_list = []
        for idx, p in enumerate(player_info_list):
            if not p["selected"]:
                not_selected_list.append([p["cur_tier"], p["lid"], idx, p["did"]])
        return {
            "embed":embed,
            "list":not_selected_list
        }

    async def change_time(self, new_time: datetime, interaction):
        self.setted_time = new_time
        if self.fixed_time is not None:
            self.fixed_time = new_time.strftime("%p %I시 %M분").replace("AM", "오전").replace("PM", "오후")
        
        ctx = await self._get_msg_ctx_from_id(self.notion_id)
        if ctx is None:
            return False
        
        ctx = ctx.split("\n")
        ctx[-1] = f"현재인원 : {len(self)}/{self.max}" if len(self) <= self.max else f"현재인원 : {self.max}/{self.max} 후보인원 : {len(self) - self.max}명"
        ctx[-3] = f"내전이 **{new_time.strftime('%p %I시 %M분').replace('AM', '오전').replace('PM', '오후')}**에 시작될 예정입니다"
        ctx = "\n".join(ctx)
        
        await self._edit_msg_from_id(self.notion_id, content=ctx)
        
        if self.mention_everyone_id :
            embed = self.cur_player_embed()
            ctx = self.cur_player_mention()
            msg = f"{ctx}\n내전이 **{self.fixed_time}**에 시작될 예정입니다\n참가자 모두 빠짐없이 확인해주세요!"
            await self._edit_msg_from_id(self.mention_everyone_id, content=msg, embed=embed)
    
    async def mention_everyone(self, interaction):
        embed = self.cur_player_embed()
        ctx = self.cur_player_mention()
        after15m = T.now_time_after_m(15)
        start_time = max(after15m,self.setted_time).strftime("%p %I시 %M분").replace("AM", "오전").replace("PM", "오후")
        if self.fixed_time is None:
            self.fixed_time = start_time
        logger.info(f"mention_everyone, match will be start at {self.fixed_time}")
        msg = f"{ctx}\n내전이 **{self.fixed_time}**에 시작될 예정입니다\n참가자 모두 빠짐없이 확인해주세요!"
        if self.mention_everyone_id is not None:
            return await self._edit_msg_from_id(self.mention_everyone_id, content=msg, embed = embed)
        mention_everyone_msg = await interaction.channel.send(msg, embed=embed)
        self.mention_everyone_id = mention_everyone_msg.id

    async def del_message(self):
        await self._edit_msg_from_id(self.mention_everyone_id, content="", delete=True)
        await self._edit_msg_from_id(self.notion_id, content="", delete=True)
        await self._edit_msg_from_id(self.tool_id, content="", delete=True)