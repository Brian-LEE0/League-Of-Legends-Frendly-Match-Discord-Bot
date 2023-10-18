import discord

from mod.discordbot import Match
from mod.opgg import OPGG

from mod.util.logger import logger
from mod.util.crud import *

class MatchJoinView(discord.ui.View):
    def __init__(self, key, timeout=None):
        super().__init__(timeout=timeout)
        self.key = key

    @discord.ui.button(label="참가 신청", style=discord.ButtonStyle.green)
    async def join(self, button, interaction):
        logger.info(f"push join button id : {button.custom_id} key : {self.key}")
        match = Match[self.key]
        if not match.is_player_exist(interaction.user):
            await interaction.response.send_modal(MatchJoinForm(interaction.message, self.key, interaction.user))
        else:
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
        await interaction.response.send_message(msg, embed=embed,
                                                ephemeral=True)  # Send a message with our View class that contains the button

    @discord.ui.button(label="내전 취소", style=discord.ButtonStyle.gray, emoji="❌")
    async def destroy(self, button, interaction):
        logger.info(f"push destroy button id : {button.custom_id} key : {self.key}")
        match = Match[self.key]
        if match.creator.mention == interaction.user.mention:
            await interaction.response.send_message(
                f"{match.creator.mention}님이 만든 내전을 삭제했습니다.\n{match.cur_player_mention()}\n내전이 취소되었습니다.")  # Send a message with our View class that contains the button
            Match.pop(self.key)
            await match.del_message()
        else:
            await interaction.response.send_message(f"{interaction.user.mention}님이 생성한 매치가 아닙니다.", ephemeral=True)

class MentionEveryoneView(discord.ui.View):
    def __init__(self, key, timeout=None):
        super().__init__(timeout=timeout)
        self.key = key

    @discord.ui.button(label="시간 변경", style=discord.ButtonStyle.gray, emoji="⏰")
    async def change_time(self, button, interaction):
        logger.info(f"push destroy button id : {button.custom_id} key : {self.key}")
        match = Match[self.key]
        
class MatchJoinForm(discord.ui.Modal):
    def __init__(self, message, key, user):
        super().__init__(title="참가 신청서")
        self.user = user
        self.key = key
        self.message = message
        self.org_league = get_league_from_discord_id(self.user.mention)

        self.league_name = discord.ui.InputText(
            style=discord.InputTextStyle.singleline,
            label="시간변경",
            placeholder="ex)오후 10시 30분",
            value=self.org_league,
            max_length=16,
        )
        self.add_item(self.league_name)

        self.suggestion = discord.ui.InputText(
            style=discord.InputTextStyle.long,
            label="기타 건의사항이 있으면 알려주세요",
            required=False,
            max_length=500,
        )
        self.add_item(self.suggestion)
        
    async def callback(self, interaction):
        try :
            # if() : # league name is exist
            league_info = OPGG.get_info(self.league_name.value)
            set_league_to_league_info(self.league_name.value, league_info)
            if self.org_league != self.league_name.value :
                set_discord_id_to_league(self.user.mention, self.league_name.value)
            
            await Match[self.key].add_player(self.user, interaction)
            if self.suggestion.value:
                logger.info(f"Suggestion : {self.suggestion.value}")
        except Exception as e:
            await self.on_error(error=Exception(e),interaction=interaction)

        # if regex_time.match(self.hour.value) and regex_time.match(self.minute.value) :
        #     await Match[self.key].add_player(self.user, interaction)
        #     if self.suggestion.value :
        #         logger.info(f"Suggestion : {self.suggestion.value}")
        # else :
        #     await self.on_error(error=Exception("시간을 다시 입력해주세요"),interaction=interaction)
        
