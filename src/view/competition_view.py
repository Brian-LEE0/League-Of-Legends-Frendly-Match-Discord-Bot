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

    @discord.ui.button(label="참가 신청", style=discord.ButtonStyle.green, row=0)
    async def join(self, button, interaction):
        player_db = mongo.Player()
        player = player_db.get_player(self.match_id, interaction.user.id)
        if not player:
            await interaction.response.send_modal(CompetitionJoinForm(interaction.message, self.match_id, interaction.user, self.game))
        else:
            await interaction.response.send_message(f"이미 대회를 신청한 유저입니다.", ephemeral=True)

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
            label="롤 본계 닉네임+태그(필수)",
            placeholder="고라니를삼킨토끼#KR1",
            required=False,
            max_length=32,
        )
        self.add_item(self.league_1)

        self.league_2 = discord.ui.InputText(
            style=discord.InputTextStyle.singleline,
            label="롤 부계1 닉네임+태그(옵션)",
            placeholder="sasakure#KR1",
            required=False,
            max_length=32,
        )
        self.add_item(self.league_2)
        
        self.league_3 = discord.ui.InputText(
            style=discord.InputTextStyle.singleline,
            label="롤 부계2 닉네임+태그(옵션)",
            placeholder="Hide on bush#KR1",
            required=False,
            max_length=32,
        )
        self.add_item(self.league_3)
        
        self.is_streamable = discord.ui.InputText(
            style=discord.InputTextStyle.singleline,
            label="스트리밍(OBS 프로그램 사용) 가능 여부",
            value="가능",
            required=True,
            
        )
        self.add_item(self.is_streamable)

        self.suggestion = discord.ui.InputText(
            style=discord.InputTextStyle.long,
            label="기타 건의사항이 있으면 알려주세요",
            required=False,
            max_length=500,
        )
        self.add_item(self.suggestion)
        
    async def callback(self, interaction):
        try :
            await interaction.response.defer()
            # if() : # league name is exist
            try :
                _ = await OPGG.get_info(self.league_1.value, if_null_return_error=True, if_unranked_return_error=True)
                
                if self.league_2.value != "":
                    _ = await OPGG.get_info(self.league_2.value, if_null_return_error=True, if_unranked_return_error=True)
                
                if self.league_3.value != "":
                    _ = await OPGG.get_info(self.league_3.value, if_null_return_error=True, if_unranked_return_error=True)
                    
            except Exception as e:
                raise Exception(f"롤 닉네임을 확인해주세요. {e}")
            
            players_db = mongo.Player()
            players_db.create_player(
                match_key=self.match_id,
                discord_id=self.user.id,
                lol_id1=self.league_1.value,
                lol_id2=self.league_2.value,
                lol_id3=self.league_3.value,
                is_streamable=self.is_streamable.value,
                suggestion=self.suggestion.value
            )
            
            players = players_db.get_players(self.match_id)
            
            msg = await self._get_msg_ctx_from_id(self.message.id)
            msg = msg.split("\n")
            msg[-1] = f"현재인원 : {len(players)}명"
            
            await interaction.followup.send(f"대회 신청이 완료되었습니다. 참가 철회(취소)는 운영진에게 문의 해주세요.", ephemeral=True)
            await self._edit_msg_from_id(self.message.id, content="\n".join(msg))
        except Exception as e:
            logger.error(e)
            await interaction.followup.send(f"에러발생, {e}", ephemeral=True, delete_after=20)
            
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