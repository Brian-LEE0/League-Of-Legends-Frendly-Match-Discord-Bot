import discord

from mod.discordbot import Match
from mod.opgg import OPGG
from mod.opgg_val import OPGG as OPGGVal

from mod.util import mongo
from mod.util.logger import logger
from mod.util.crud import *
from mod.discordbot import bot
import re
import random

class CompetitionJoinView(discord.ui.View):
    def __init__(self, match_id, timeout=None, game=""):
        super().__init__(timeout=timeout)
        self.match_id = match_id
        self.game = game
        
        joinButton = discord.ui.Button(label="참가 신청", style=discord.ButtonStyle.green, custom_id= match_id+ "참가신청_버튼")
        joinButton.callback = self.join
        self.add_item(joinButton)
        
    # @discord.ui.button(label="참가 신청", custom_id="참가신청_버튼", style=discord.ButtonStyle.green, row=0)
    async def join(self, interaction):
        player_db = mongo.Player()
        player = player_db.get_player(self.match_id, interaction.user.id)
        if not player:
            await interaction.response.send_modal(CompetitionJoinForm(interaction.message, self.match_id, interaction.user, self.game))
        else:
            await interaction.response.send_message(f"⚠️⚠️⚠️ 이미 대회를 신청한 유저입니다.", ephemeral=True)

    # @discord.ui.button(label="참가 철회", style=discord.ButtonStyle.red, row=0)
    # async def unjoin(self, button, interaction):
    #     logger.info(f"push unjoin button id : {button.custom_id} match_id : {self.match_id}")
    #     match = Match[self.match_id]
    #     await match.remove_player(interaction.user, interaction)
        
class CompetitionJoinForm(discord.ui.Modal):
    def __init__(self, message, match_id, user, game=""):
        super().__init__(title="참가 신청서")
        self.user = user
        self.match_id = match_id
        self.message = message
        self.game = game

        self.league_1 = discord.ui.InputText(
            style=discord.InputTextStyle.singleline,
            label="롤 본계 닉네임+태그",
            placeholder="고라니를삼킨토끼#KR1",
            required=True,
            max_length=32,
        )
        self.add_item(self.league_1)

        self.league_2 = discord.ui.InputText(
            style=discord.InputTextStyle.singleline,
            label="롤 부계 닉네임+태그",
            placeholder="sasakure#KR1",
            required=False,
            max_length=32,
        )
        self.add_item(self.league_2)
        
        self.is_streamable = discord.ui.InputText(
            style=discord.InputTextStyle.singleline,
            label="스트리밍(OBS 프로그램 사용) 가능 여부 (가능/불가능)",
            value="가능",
            required=True,
        )
        self.add_item(self.is_streamable)
        
        self.position_1 = discord.ui.InputText(
            placeholder="미드",
            style=discord.InputTextStyle.singleline,
            label="주포지션",
            required=True,
        )
        self.add_item(self.position_1)
        
        self.position_2 = discord.ui.InputText(
            placeholder="원딜",
            style=discord.InputTextStyle.singleline,
            label="부포지션",
            required=True,
        )
        self.add_item(self.position_2)
        
    async def callback(self, interaction):
        try :
            await interaction.response.defer()
            # if() : # league name is exist
            try :
                _ = await OPGG.get_info(self.league_1.value, if_null_return_error=True, if_unranked_return_error=True)
                
                if self.league_2.value != "":
                    _ = await OPGG.get_info(self.league_2.value, if_null_return_error=True, if_unranked_return_error=True)
                
                # if self.league_3.value != "":
                #     _ = await OPGG.get_info(self.league_3.value, if_null_return_error=True, if_unranked_return_error=True)
                    
            except Exception as e:
                raise Exception(f"롤 닉네임을 확인해주세요. {e}")
            
            if self.is_streamable.value not in ["가능", "불가능"]:
                raise Exception("스트리밍 가능 여부는 가능/불가능 중 하나로 입력해주세요.")
            
            if self.position_1.value not in ["탑", "미드", "원딜", "서폿", "정글"]:
                raise Exception("주포지션은 탑, 미드, 원딜, 서폿, 정글 중 하나로 입력해주세요.")
            
            if self.position_2.value not in ["탑", "미드", "원딜", "서폿", "정글"]:
                raise Exception("부포지션1은 탑, 미드, 원딜, 서폿, 정글 중 하나로 입력해주세요.")
            
            players_db = mongo.Player()
            players_db.create_player(
                match_key=self.match_id,
                discord_id=self.user.id,
                lol_id1=self.league_1.value,
                lol_id2=self.league_2.value,
                lol_id3="",
                position1=self.position_1.value,
                position2=self.position_2.value,
                position3="",
                is_streamable=self.is_streamable.value,
            )
            
            players = players_db.get_players(self.match_id)
            
            msg = f"현재인원 : {len(players)}명"
            
            await interaction.followup.send(f"대회 신청이 완료되었습니다. 참가 철회(취소)는 운영진에게 문의 해주세요.", ephemeral=True)
            await self.message.edit(content=msg)
        except Exception as e:
            logger.error(e)
            await interaction.followup.send(f"⚠️⚠️⚠️에러발생, {e}", ephemeral=True)
            
    # @staticmethod
    # async def _edit_msg_from_id(mid, **kwargs):
    #     msg = bot.get_message(mid)
    #     if msg is None:
    #         logger.info(f"fail to edit msg : {mid}")
    #         return False

    #     if "delete" in kwargs.keys() and kwargs["delete"] is True:
    #         try:
    #             await msg.delete()
    #             logger.info(f"edit msg : {mid}")
    #             return True
    #         except:
    #             return False
    #     logger.info(f"edit msg : {mid}")
        
    #     await msg.edit(**kwargs)
    #     return True

    # @staticmethod
    # async def _get_msg_ctx_from_id(mid):
    #     msg = bot.get_message(mid)
    #     if msg is None:
    #         logger.info(f"fail to get msg from : {mid}")
    #         return None
    #     logger.info(f"get msg from : {mid}")
    #     return msg.content