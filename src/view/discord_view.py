from typing import Dict, List
import discord

from mod.discordbot import Match
from mod.opgg import OPGG
from mod.opgg_val import OPGG as OPGGVal

from mod.util.logger import logger
from mod.util.crud import *
import re
import random

from view.embed.val import get_random_val_map

class MatchJoinView(discord.ui.View):
    def __init__(self, key, timeout=None, game=""):
        super().__init__(timeout=timeout)
        self.key = key
        self.game = game

    @discord.ui.button(label="참가 신청", style=discord.ButtonStyle.green, row=0)
    async def join(self, button, interaction):
        logger.info(f"push join button id : {button.custom_id} key : {self.key}")
        match = Match[self.key]
        if not match.is_player_exist(interaction.user):
            await interaction.response.send_modal(MatchJoinForm(interaction.message, self.key, interaction.user, self.game))
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
        await interaction.response.send_message(msg,
                                                embed=embed,
                                                ephemeral=True,
                                                delete_after=60)  # Send a message with our View class that contains the button
        
    @discord.ui.button(label="팀 드래프트", style=discord.ButtonStyle.gray, emoji="🎲", row=1)
    async def team_draft(self, button, interaction):
        await interaction.response.defer()
        logger.info(f"push team draft button id : {button.custom_id} key : {self.key}")
        match = Match[self.key]
        if len(match) < match.max:
            return await interaction.followup.send("매치 인원이 부족합니다.", ephemeral=True, delete_after=3)
        player_info_list = []
        draft_info = match.get_draft_embed_and_list(player_info_list)
        await interaction.followup.send(f"각 팀 **팀장**을 먼저 등록 해주세요!\n드래프트 순서와 진영은 상관 없습니다.", 
                                                    embed=draft_info["embed"],
                                                    view=TeamDraftView(match,draft_info["list"], player_info_list))
        
    @discord.ui.button(label="내전 취소", style=discord.ButtonStyle.gray, emoji="❌", row=1)
    async def destroy(self, button, interaction):
        await interaction.response.defer()
        logger.info(f"push destroy button id : {button.custom_id} key : {self.key}")
        match = Match[self.key]
        if match.creator.mention == interaction.user.mention:
            await interaction.followup.send(
                f"{match.cur_player_mention()}{match.creator.mention}님이 만든 내전을 삭제했습니다.\n내전이 취소되었습니다.")  # Send a message with our View class that contains the button
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
            
class PlayerDeleteSelect(discord.ui.Select):
    def __init__(self, match, usr_list):
        self.match = match
        options : list = [discord.SelectOption(emoji=usr[0], label=usr[1], value=str(usr[3])) for usr in usr_list]
        
        super().__init__(
            min_values=1,
            max_values=1,
            options=options,
        )
        
    async def callback(self, interaction):
        player_mention = self.values[0]
        deleted_user = self.match.get_player_by_id(int(re.sub(r'[^0-9]', '', player_mention)))
        await self.match.remove_player(deleted_user, interaction)
        await interaction.followup.send(f"{interaction.user.mention}님이 {player_mention}님을 매치에서 제거했습니다.")
        
        # self.disabled = True
        # await interaction.followup.edit_message(view=self.view)
        
class PlayerDeleteView(discord.ui.View):
    def __init__(self, match, usr_list, timeout=None):
        super().__init__(timeout=timeout)
        self.select = PlayerDeleteSelect(match, usr_list)
        self.add_item(self.select)
        
class ToolView(discord.ui.View):
    def __init__(self, key, timeout=None, game=""):
        self.key = key
        self.game = game
        super().__init__(timeout=timeout)
        
    @discord.ui.button(label="시간 변경", style=discord.ButtonStyle.blurple, row=0, emoji="⏰")
    async def join(self, button, interaction):
        await interaction.response.defer()
        return await interaction.followup.send(f"곧 구현될 기능입니다.", ephemeral=True, delete_after=3)

    @discord.ui.button(label="선수 삭제", style=discord.ButtonStyle.red, row=0, emoji="🗑️")
    async def unjoin(self, button, interaction):
        await interaction.response.defer()
        logger.info(f"push player delete button id : {button.custom_id} key : {self.key}")
        match = Match[self.key]
        if len(match) > 0 :
            player_info_list = []
            draft_info = match.get_draft_embed_and_list(player_info_list)
            return await interaction.followup.send(f"***⚠️ 주의! 선수를 매치에서 제거합니다.***",
                                                    view=PlayerDeleteView(match, draft_info["list"]), ephemeral=True, delete_after=30)
        await interaction.followup.send(f"참가를 신청한 선수가 없습니다.", ephemeral=True, delete_after=3)
        
    @discord.ui.button(label="맵뽑기", style=discord.ButtonStyle.green, row = 0)
    async def match_info(self, button, interaction):
        map_list = await OPGGVal.get_map()
        await interaction.response.send_modal(ElectMapForm(map_list))
        
class MatchInfoView(discord.ui.View):
    def __init__(self, key, timeout=None):
        super().__init__(timeout=timeout)
        self.key = key
    
    @discord.ui.button(label="선수삭제 | 시간변경", style=discord.ButtonStyle.red, emoji="⚙️", row=0)
    async def team_draft(self, button, interaction):
        await interaction.response.defer()
        logger.info(f"push destroy button id : {button.custom_id} key : {self.key}")
        match = Match[self.key]
        if match.creator.mention == interaction.user.mention:
            await interaction.followup.send(
                f"**/선수삭제**, **/시간변경** 명령어를 사용 해 주세요\n**매치 키**: {self.key}", ephemeral=True, delete_after=30)  # Send a message with our View class that contains the button
        else:
            await interaction.followup.send(f"{interaction.user.mention}님이 생성한 매치가 아닙니다. 매치 생성자에게 문의 해주세요", delete_after=10)
            
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
    
    def is_valid_req(self):
        if not self.selected_user.values:
            return False
        if int(self.selected_user.values[0]) in self.team1 + self.team2:
            return False
        return True
    
    async def change_msg(self, interaction):
        ctx = ""
        draft_info =  self.match.get_draft_embed_and_list(player_info_list=self.player_info_list, team1 = self.team1, team2 = self.team2)
        
        if draft_info["list"] :
            self.selected_user.options = [discord.SelectOption(emoji=usr[0], label=usr[1], value=str(usr[2])) for usr in draft_info["list"]]
            self.selected_user.disabled = False
        else:
            self.selected_user.disabled = True
            
        if len(self.team1) < 1 or len(self.team2) < 1:
            dice = random.randint(1, 6)
            ctx = f"각 팀 **팀장**을 먼저 등록 해주세요!\n드래프트 순서와 진영은 상관 없습니다."
        if len(self.team1) == 1 and len(self.team2) == 1:
            dice = random.randint(1, 6)
            ctx = f"**팀장 등록**이 완료되었습니다.\n홀수: {self.player_info_list[self.team1[0]]['did']}, 짝수: {self.player_info_list[self.team2[0]]['did']}\n랜덤 주사위 결과 ***{dice}***!, **{self.player_info_list[self.team1[0]]['did'] if dice % 2 else self.player_info_list[self.team2[0]]['did']}**님이 먼저 팀원을 선택해주세요"
        if len(self.team1) == self.match.max/2 and len(self.team2) == self.match.max/2:
            dice = random.randint(1, 6)
            ctx = f"**팀원 등록**이 완료되었습니다.\n홀수: {self.player_info_list[self.team1[0]]['did']}, 짝수: {self.player_info_list[self.team2[0]]['did']}\n랜덤 주사위 결과 ***{dice}***!, **{self.player_info_list[self.team1[0]]['did'] if dice % 2 else self.player_info_list[self.team2[0]]['did']}**님이 먼저 진영을 선택해주세요"
        
        if ctx :
            return await interaction.response.edit_message(content = ctx, embed = draft_info["embed"], view=self)
        await interaction.response.edit_message(embed = draft_info["embed"], view=self)

    @discord.ui.button(label="1팀 등록", style=discord.ButtonStyle.blurple, row = 1)
    async def enroll_team1(self, button, interaction):
        try:
            if not self.is_valid_req():
                return await interaction.response.send_message(content="유저를 다시 선택해주세요.", ephemeral=True, delete_after=3)
            if len(self.team2) == 0 and len(self.team1) >= 1:
                return await interaction.response.send_message(content="2팀 팀장을 먼저 선택해주세요.", delete_after=3)
            
            self.team1.append(int(self.selected_user.values[0]))
            self.selected.append(int(self.selected_user.values[0]))
            
            await self.change_msg(interaction)
            
        except Exception as e:
            return await interaction.response.send_message(content=f"올바른 유저를 선택해주세요. {e}", ephemeral=True, delete_after=3)
        
    @discord.ui.button(label="2팀 등록", style=discord.ButtonStyle.red, row = 1)
    async def enroll_team2(self, button, interaction):
        try:
            if not self.is_valid_req():
                return await interaction.response.send_message(content="유저를 다시 선택해주세요.", ephemeral=True, delete_after=3)
            if len(self.team1) == 0 and len(self.team2) >= 1:
                return await interaction.response.send_message(content="1팀 팀장을 먼저 선택해주세요.", delete_after=3)
            
            self.team2.append(int(self.selected_user.values[0]))
            self.selected.append(int(self.selected_user.values[0]))
            
            await self.change_msg(interaction)
        except Exception as e:
            return await interaction.response.send_message(content=f"올바른 유저를 선택해주세요. {e}", ephemeral=True, delete_after=3)

    @discord.ui.button(label="되돌리기", style=discord.ButtonStyle.gray, row = 1)
    async def match_info(self, button, interaction):
        try :
            last_idx = self.selected.pop()
            if last_idx in self.team1:
                self.team1.remove(last_idx)
            if last_idx in self.team2:
                self.team2.remove(last_idx)
                
            await self.change_msg(interaction)
        except Exception as e :
            return await interaction.response.send_message(content=f"에러발생 {e}", ephemeral=True, delete_after=3)
        
    @discord.ui.button(label="맵뽑기", style=discord.ButtonStyle.green, row = 1)
    async def match_info(self, button, interaction):
        map_list = await OPGGVal.get_map()
        await interaction.response.send_modal(ElectMapForm(map_list))
        
class MatchJoinForm(discord.ui.Modal):
    def __init__(self, message, key, user, game=""):
        super().__init__(title="참가 신청서")
        self.user = user
        self.key = key
        self.message = message
        self.game = game
        self.org_league = get_league_from_discord_id(self.user.mention + self.game)
        if self.org_league and "#" not in self.org_league :
            self.org_league += "#KR1"
        self.org_league_name = self.org_league.split("#")[0] if self.org_league else None
        self.org_league_tag = ("#" + self.org_league.split("#")[1]) if self.org_league else None

        self.league_name = discord.ui.InputText(
            style=discord.InputTextStyle.singleline,
            label="게임 닉네임",
            placeholder="Hide on bush",
            value=self.org_league_name,
            max_length=16,
        )
        self.add_item(self.league_name)

        self.league_tag = discord.ui.InputText(
            style=discord.InputTextStyle.singleline,
            label="리그 오브 레전드 태그",
            placeholder="#KR1",
            value=self.org_league_tag if self.org_league_tag is not None else "#KR1",
            max_length=16,
        )
        self.add_item(self.league_tag)

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
            my_league_full_name = self.league_name.value + self.league_tag.value
            if self.game == "val":
                league_info = await OPGGVal.get_info(val_name=my_league_full_name)
            else:
                league_info = await OPGG.get_info(league_name=my_league_full_name)
            if league_info is None:
                if get_league_from_discord_id(self.user.mention + self.game):
                    pass
                else:
                    raise Exception("존재하지 않는 아이디")
            else:
                set_league_to_league_info(my_league_full_name + self.game, league_info)
            
            set_discord_id_to_league(self.user.mention + self.game, my_league_full_name)
            
            await Match[self.key].add_player(self.user, interaction)
            if my_league_full_name:
                logger.info(f"Suggestion : {my_league_full_name}")
        except Exception as e:
            logger.error(e)
            await interaction.followup.send(f"에러발생, {e}", ephemeral=True, delete_after=20)
            


class ElectMapForm(discord.ui.Modal):
    def __init__(self, map_list: Dict[str, str], timeout=None):
        super().__init__(title="맵뽑기", timeout=timeout)
        self.org_map_list = map_list
        self.map_candidates = discord.ui.InputText(
            style=discord.InputTextStyle.long,
            label="맵 후보",
            value = "\n".join(list(map_list.keys())),
            required=True,
            max_length=500,
        )
        self.add_item(self.map_candidates)
        
    async def callback(self, interaction):
        try :
            await interaction.response.defer()
            map_candidates_list = self.map_candidates.value.split("\n")
            map_candidates_list = [m.strip() for m in map_candidates_list if m.strip() != ""]
            print(map_candidates_list)
            for om in self.org_map_list.copy():
                if om not in map_candidates_list:
                    self.org_map_list.pop(om)
            for m in map_candidates_list:
                if m not in self.org_map_list:
                    self.org_map_list.update({m: ""})
            
            embed = await get_random_val_map(self.org_map_list, interaction.user)
            await interaction.followup.send(embed=embed)
            return 
        except Exception as e:
            logger.error(e)
            await interaction.followup.send(f"에러발생, {e}", ephemeral=True, delete_after=20)