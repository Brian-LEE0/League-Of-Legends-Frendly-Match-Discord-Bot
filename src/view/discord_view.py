import discord

from mod.discordbot import Match
from mod.opgg import OPGG

from mod.util.logger import logger
from mod.util.crud import *

import random

class MatchJoinView(discord.ui.View):
    def __init__(self, key, timeout=None):
        super().__init__(timeout=timeout)
        self.key = key

    @discord.ui.button(label="참가 신청", style=discord.ButtonStyle.green, row=0)
    async def join(self, button, interaction):
        logger.info(f"push join button id : {button.custom_id} key : {self.key}")
        match = Match[self.key]
        if not match.is_player_exist(interaction.user):
            await interaction.response.send_modal(MatchJoinForm(interaction.message, self.key, interaction.user))
        else:
            await interaction.response.send_message(f"이미 내전을 신청한 유저입니다.", ephemeral=True)

    @discord.ui.button(label="참가 철회", style=discord.ButtonStyle.red, row=0)
    async def unjoin(self, button, interaction):
        logger.info(f"push unjoin button id : {button.custom_id} key : {self.key}")
        match = Match[self.key]
        await match.remove_player(interaction.user, interaction)

    @discord.ui.button(label="내전 정보", style=discord.ButtonStyle.blurple, row=0)
    async def match_info(self, button, interaction):
        logger.info(f"push match_info button id : {button.custom_id} key : {self.key}")
        match = Match[self.key]
        embed = match.cur_player_embed()
        msg = f"총 인원 : {len(match)}/{match.max}"
        await interaction.response.send_message(msg, embed=embed,
                                                ephemeral=True, delete_after=20)  # Send a message with our View class that contains the button
        
    @discord.ui.button(label="팀 드래프트", style=discord.ButtonStyle.gray, emoji="🎲", row=0)
    async def team_draft(self, button, interaction):
        await interaction.response.defer()
        logger.info(f"push team draft button id : {button.custom_id} key : {self.key}")
        match = Match[self.key]
        if len(match) < match.max:
            return await interaction.followup.send("매치 인원이 부족합니다.", ephemeral=True, delete_after=3)
        player_info_list = []
        draft_info = match.get_draft_embed_and_list(player_info_list)
        await interaction.followup.send("각 팀별 **방장**을 등록 해주세요!\n드래프트 순서와 진영은 상관 없습니다.", 
                                                    embed=draft_info["embed"],
                                                    view=TeamDraftView(match,draft_info["list"], player_info_list))
        

    @discord.ui.button(label="내전 취소", style=discord.ButtonStyle.gray, emoji="❌", row=1)
    async def destroy(self, button, interaction):
        await interaction.response.defer()
        logger.info(f"push destroy button id : {button.custom_id} key : {self.key}")
        match = Match[self.key]
        if match.creator.mention == interaction.user.mention:
            await interaction.followup.send(
                f"{match.creator.mention}님이 만든 내전을 삭제했습니다.\n{match.cur_player_mention()}\n내전이 취소되었습니다.")  # Send a message with our View class that contains the button
            Match.pop(self.key)
            await match.del_message()
        else:
            await interaction.followup.send(f"{interaction.user.mention}님이 생성한 매치가 아닙니다.", ephemeral=True, delete_after=3)
            
    @discord.ui.button(label="조용히 내전 취소", style=discord.ButtonStyle.gray, emoji="🔇", row=1)
    async def slient_destroy(self, button, interaction):
        await interaction.response.defer()
        logger.info(f"push slient destroy button id : {button.custom_id} key : {self.key}")
        match = Match[self.key]
        if match.creator.mention == interaction.user.mention:
            await interaction.followup.send(
                f"{match.creator.mention}님이 만든 내전을 삭제했습니다.\n내전이 취소되었습니다.")  # Send a message with our View class that contains the button
            Match.pop(self.key)
            await match.del_message()
        else:
            await interaction.followup.send(f"{interaction.user.mention}님이 생성한 매치가 아닙니다.", ephemeral=True, delete_after=3)

class TeamDraftSelect(discord.ui.Select):
    def __init__(self, usr_list):
        options : list = [discord.SelectOption(emoji=usr[0], label=usr[1], value=str(usr[2])) for usr in usr_list]
        super().__init__(
            min_values=1,
            max_values=1,
            options=options,
        )
        
    async def callback(self, interaction):
        for o in self.options:
            if o.default == True:
                o.default = False
            if o.value == self.values[0]:
                o.default = True
        await interaction.response.edit_message(view=self.view)

class TeamDraftView(discord.ui.View):
    def __init__(self, match, usr_list, player_info_list, timeout=None):
        super().__init__(timeout=timeout)
        self.selected_user = TeamDraftSelect(usr_list)
        self.add_item(self.selected_user)
        self.match = match
        self.team1 = []
        self.team2 = []
        self.selected = []
        self.player_info_list = player_info_list
        

    @discord.ui.button(label="1팀 등록", style=discord.ButtonStyle.blurple, row = 1)
    async def enroll_team1(self, button, interaction):
        try:
            ctx = ""
            if not self.selected_user.values:
                return await interaction.response.send_message(content="1팀에 등록할 유저를 선택해주세요.", ephemeral=True, delete_after=3)
            if int(self.selected_user.values[0]) in self.team1 + self.team2:
                return await interaction.response.send_message(content="올바른 유저를 선택해주세요.", ephemeral=True, delete_after=3)
            if len(self.team2) == 0 and len(self.team1) >= 1:
                return await interaction.response.send_message(content="1팀 팀장을 먼저선택해주세요.", delete_after=3)
            if len(self.team1) == 1 and len(self.team2) == 1:
                dice = random.randint(1, 6)
                ctx = f"팀장 등록이 완료되었습니다.\n랜덤 주사위 결과 ***{dice}***!, **{'2팀' if dice % 2 else '1팀'}**이 먼저 팀원을 선택해주세요"
            if len(self.team1) == self.match.max%2 and len(self.team2) == self.match.max%2:
                dice = random.randint(1, 6)
                ctx = f"팀원 선택이 완료되었습니다.\n랜덤 주사위 결과 ***{dice}***!, **{'2팀' if dice % 2 else '1팀'}**이 먼저 진영을 선택해주세요"
            self.team1.append(int(self.selected_user.values[0]))
            self.selected.append(int(self.selected_user.values[0]))
            draft_info =  self.match.get_draft_embed_and_list(player_info_list=self.player_info_list, team1 = self.team1, team2 = self.team2)
            if draft_info["list"] :
                self.selected_user.options = [discord.SelectOption(emoji=usr[0], label=usr[1], value=str(usr[2])) for usr in draft_info["list"]]
            else:
                self.selected_user.disabled = True
            if ctx :
                return await interaction.response.edit_message(content = ctx, embed = draft_info["embed"], view=self)
            await interaction.response.edit_message(embed = draft_info["embed"], view=self)
        except Exception as e:
            return await interaction.response.send_message(content=f"올바른 유저를 선택해주세요. {e}", ephemeral=True, delete_after=3)
        
    @discord.ui.button(label="2팀 등록", style=discord.ButtonStyle.red, row = 1)
    async def enroll_team2(self, button, interaction):
        try:
            ctx = ""
            if not self.selected_user.values:
                return await interaction.response.send_message(content="2팀에 등록할 유저를 선택해주세요.", ephemeral=True, delete_after=3)
            if int(self.selected_user.values[0]) in self.team1 + self.team2:
                return await interaction.response.send_message(content="올바른 유저를 선택해주세요.", ephemeral=True, delete_after=3)
            if len(self.team1) == 0 and len(self.team2) >= 1:
                return await interaction.response.send_message(content="1팀 팀장을 먼저선택해주세요.", delete_after=3)
            if len(self.team1) == 1 and len(self.team2) == 1:
                dice = random.randint(1, 6)
                ctx = f"팀장 등록이 완료되었습니다.\n랜덤 주사위 결과 ***{dice}***!, **{'1팀' if dice % 2 else '2팀'}**이 먼저 팀원을 선택해주세요"
            if len(self.team1) == self.match.max/2 and len(self.team2) == self.match.max/2:
                dice = random.randint(1, 6)
                ctx = f"팀원 선택이 완료되었습니다.\n랜덤 주사위 결과 ***{dice}***!, **{'1팀' if dice % 2 else '2팀'}**이 먼저 진영을 선택해주세요"
            self.team2.append(int(self.selected_user.values[0]))
            self.selected.append(int(self.selected_user.values[0]))
            draft_info =  self.match.get_draft_embed_and_list(player_info_list=self.player_info_list, team1 = self.team1, team2 = self.team2)
            if draft_info["list"] :
                self.selected_user.options = [discord.SelectOption(emoji=usr[0], label=usr[1], value=str(usr[2])) for usr in draft_info["list"]]
                self.selected_user.disabled = False
            else:
                self.selected_user.disabled = True
            if ctx :
                return await interaction.response.edit_message(content = ctx, embed = draft_info["embed"], view=self)
            await interaction.response.edit_message(embed = draft_info["embed"], view=self)
        except Exception as e:
            return await interaction.response.send_message(content=f"올바른 유저를 선택해주세요. {e}", ephemeral=True, delete_after=3)

    @discord.ui.button(label="되돌리기", style=discord.ButtonStyle.gray, row = 1)
    async def match_info(self, button, interaction):
        try :
            ctx = ""
            last_idx = self.selected.pop()
            if last_idx in self.team1:
                self.team1.remove(last_idx)
            if last_idx in self.team2:
                self.team2.remove(last_idx)
            if len(self.team1) < 1 or len(self.team2) < 1:
                dice = random.randint(1, 6)
                ctx = f"각 팀별 **방장**을 등록 해주세요!\n드래프트 순서와 진영은 상관 없습니다."
            if len(self.team1) == 1 and len(self.team2) == 1:
                dice = random.randint(1, 6)
                ctx = f"팀장 등록이 완료되었습니다.\n랜덤 주사위 결과 ***{dice}***!, **{'1팀' if dice % 2 else '2팀'}**이 먼저 팀원을 선택해주세요"
            if len(self.team1) == self.match.max/2 and len(self.team2) == self.match.max/2:
                dice = random.randint(1, 6)
                ctx = f"팀원 선택이 완료되었습니다.\n랜덤 주사위 결과 ***{dice}***!, **{'1팀' if dice % 2 else '2팀'}**이 먼저 진영을 선택해주세요"
            draft_info =  self.match.get_draft_embed_and_list(player_info_list=self.player_info_list, team1 = self.team1, team2 = self.team2)
            if draft_info["list"] :
                self.selected_user.options = [discord.SelectOption(emoji=usr[0], label=usr[1], value=str(usr[2])) for usr in draft_info["list"]]
                self.selected_user.disabled = False
            if ctx :
                return await interaction.response.edit_message(content = ctx, embed = draft_info["embed"], view=self)
            await interaction.response.edit_message(embed = draft_info["embed"], view=self)
        except Exception as e :
            return await interaction.response.send_message(content=f"에러발생 {e}", ephemeral=True, delete_after=3)
# class MentionEveryoneView(discord.ui.View):
#     def __init__(self, key, timeout=None):
#         super().__init__(timeout=timeout)
#         self.key = key

#     @discord.ui.button(label="시간 변경", style=discord.ButtonStyle.gray, emoji="⏰")
#     async def change_time(self, button, interaction):
#         logger.info(f"push destroy button id : {button.custom_id} key : {self.key}")
#         match = Match[self.key]
        
class MatchJoinForm(discord.ui.Modal):
    def __init__(self, message, key, user):
        super().__init__(title="참가 신청서")
        self.user = user
        self.key = key
        self.message = message
        self.org_league = get_league_from_discord_id(self.user.mention)

        self.league_name = discord.ui.InputText(
            style=discord.InputTextStyle.singleline,
            label="리그 오브 레전드 닉네임",
            placeholder="Hide on bush",
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
            league_info = await OPGG.get_info(league_name=self.league_name.value)
            set_league_to_league_info(self.league_name.value, league_info)
            if self.org_league != self.league_name.value :
                set_discord_id_to_league(self.user.mention, self.league_name.value)
            
            await Match[self.key].add_player(self.user, interaction)
            if self.suggestion.value:
                logger.info(f"Suggestion : {self.suggestion.value}")
        except Exception as e:
            logger.error(e)
            await self.on_error(error=e,interaction=interaction)

        # if regex_time.match(self.hour.value) and regex_time.match(self.minute.value) :
        #     await Match[self.key].add_player(self.user, interaction)
        #     if self.suggestion.value :
        #         logger.info(f"Suggestion : {self.suggestion.value}")
        # else :
        #     await self.on_error(error=Exception("시간을 다시 입력해주세요"),interaction=interaction)