from logging import Logger
import aiohttp
from bs4 import BeautifulSoup

class OPGG:
    @staticmethod
    def _get_tier(soup):
        try :
            rank_solo_tier = soup.find("div","css-1kw4425 ecc8cxr0").find("div","tier")
            if rank_solo_tier is None :
                prev_tier = soup.find("ul", "tier-list").find("li")
                if prev_tier is None :
                    return "UNRANK"
                prev_tier = prev_tier.text.split()
                if len(prev_tier) == 4 :
                    tier = f"{prev_tier[2][0].upper()}{prev_tier[3]}"
                    season = f"{prev_tier[0]} {prev_tier[1]}"
                elif len(prev_tier) == 3:
                    if prev_tier[-1].isnumeric():
                        tier = f"{prev_tier[1][0].upper()}{prev_tier[2]}"
                        season = f"{prev_tier[0]}"
                    else:
                        tier = f"{prev_tier[2][0].upper()}"
                        season = f"{prev_tier[0]} {prev_tier[1]}"
                else:
                    tier = f"{prev_tier[1][0].upper()}"
                    season = f"{prev_tier[0]}"
                return f"{tier}({season})"
            rank_solo_tier = rank_solo_tier.text
            return rank_solo_tier[0].upper()+rank_solo_tier[-1]
        except:
            return None

    @staticmethod
    def _get_champ_list(soup):
        try :
            champ_list = soup.find("div","css-yqoz96 enfvmur0").find_all("div","champion-box")
            champ_list = list(map(lambda champ : [champ.find("div","name").text, 
                                                  champ.find("div","kda").find("div").find("div").text.split(":")[0],
                                                  champ.find("div","played").find("div").find("div").text
                                                 ],
                                  champ_list))
            champ_list = champ_list[:(3 if len(champ_list) > 3 else len(champ_list))]
            while(len(champ_list) < 3):
                champ_list.append(["","",""])
            return champ_list[:(3 if len(champ_list) > 3 else len(champ_list))]
        except Exception as e:
            print(e)
            return [["","",""]]*3
        
    @staticmethod
    async def get_info(timeout = 2.0, 
                        league_name = "고라니를삼킨토끼", 
                        retry_cnt = 0):
        if retry_cnt >= 5:
            return None
        async with aiohttp.ClientSession(cookies = {"_ol":"ko_KR"},
                                        timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.get(f"https://www.op.gg/summoners/kr/{league_name}") as response:
                soup = BeautifulSoup(await response.text(), "html.parser")
                tier = OPGG._get_tier(soup)
                if tier is None :
                    raise Exception("존재하지 않는 아이디")
                cl = OPGG._get_champ_list(soup)
                return {"cur_tier" : tier,
                        "most_3" : cl}
