import random
import discord
from mod.opgg_val import OPGG as OPGGVal

async def get_random_val_map(user: discord.Member) -> discord.Embed:
    map_list = await OPGGVal.get_map()
    map_chosen = random.choice(list(map_list.keys()))
    embed = discord.Embed(
        title=f"랜덤으로 추첨된 맵은 **{map_chosen}** 입니다",
        color=discord.Colour.blurple()
    )
    embed.set_image(url=map_list[map_chosen])
    embed.set_footer(text=f"요청자: {user.display_name}", icon_url=user.avatar)
    print(embed.to_dict())
    return embed