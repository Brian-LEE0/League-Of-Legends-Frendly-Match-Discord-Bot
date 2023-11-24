from mod.util.logger import logger
import aiohttp
from bs4 import BeautifulSoup
import re

class OPGG:
    @staticmethod
    def _get_tier(soup):
        try :
            rank_solo_tier = soup.find("div","css-1kw4425 ecc8cxr0").find("div","tier")
            if rank_solo_tier is None :
                prev_tier = soup.find("ul", "tier-list").find("li")
                if prev_tier is None :
                    return "unranked"
                prev_tier = prev_tier.text.split()
                if len(prev_tier) == 4 :
                    tier = prev_tier[2]
                elif len(prev_tier) == 3:
                    if prev_tier[-1].isnumeric():
                        tier = prev_tier[1]
                    else:
                        tier = prev_tier[2]
                else:
                    tier = prev_tier[1]
                return tier
            rank_solo_tier = rank_solo_tier.text
            return rank_solo_tier.split()[0]
        except:
            return None

    @staticmethod
    def _get_champ_list(soup):
        try :
            champ_list = soup.find_all("div","champion-box")
            champ_list = list(map(lambda champ : [re.sub("[^a-z]","",champ.find("div","name").text.lower()), 
                                                  champ.find("div","kda").find("div").find("div").text.split(":")[0],
                                                  champ.find("div","played").find("div").find("div").text
                                                 ],
                                  champ_list))
            champ_list = champ_list[:(3 if len(champ_list) > 3 else len(champ_list))]
            return champ_list
        except Exception as e:
            logger.info(e)
            return []
        
    @staticmethod
    async def get_info(league_name = "고라니를삼킨토끼",
                        timeout = 10.0, 
                        retry_cnt = 0):
        if retry_cnt >= 5:
            return None
        async with aiohttp.ClientSession(cookies = {"_ol":"en_US"},
                                        timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.get(f"https://www.op.gg/summoners/kr/{league_name.replace('#','-')}") as response:
                soup = BeautifulSoup(await response.text(), "html.parser")
                tier = OPGG._get_tier(soup)
                if tier is None :
                    raise Exception("존재하지 않는 아이디")
                cl = OPGG._get_champ_list(soup)
                logger.info({"cur_tier" : tier,
                        "most_3" : cl})
                return {"cur_tier" : tier,
                        "most_3" : cl}
