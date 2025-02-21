from mod.util.logger import logger
import aiohttp
from bs4 import BeautifulSoup
import re
from async_lru import alru_cache

class OPGG:
        
    @staticmethod
    def tier_sort(tier):
        if tier == "unrank":
            return 0
        elif tier == "iron":
            return 1
        elif tier == "bronze":
            return 2
        elif tier == "silver":
            return 3
        elif tier == "gold":
            return 4
        elif tier == "platinum":
            return 5
        elif tier == "emerald":
            return 6
        elif tier == "diamond":
            return 7
        elif tier == "master":
            return 8
        elif tier == "grandmaster":
            return 9
        elif tier == "challenger":
            return 10
        else:
            return -1
        
    @staticmethod
    def _get_tier(soup):
        try :
            tier_sec = soup.find("div","css-xm62d3 e1l3ivmk0")
            tiers_raw = tier_sec.find_all("div","rank-item")
            if tiers_raw is None :
                return "unranked"
            tiers = []
            for tier in tiers_raw[:5]:
                tier = tier.find("span").text.split(" ")[0].lower()
                tiers.append(tier)
            
            try:
                tier_cur = soup.find("div", "css-1wk31w7 eaj0zte0")
                tier_raw = tier_cur.find("div", "tier").text.split(" ")[0].lower()
                tiers.append(tier_raw)
            except:
                pass
                
            # sort
            if len(tiers) == 1:
                return tiers[0]
            else:
                return sorted(tiers, key=lambda x : OPGG().tier_sort(x), reverse=True)[0]
        except Exception as e:
            logger.info(e)
            raise Exception("⚠️ 존재하지 않는 아이디 티어")

    @staticmethod
    def _get_champ_list(soup):
        try :
            champ_list = soup.find_all("div","champion-box")
            champ_list = list(map(lambda champ : [re.sub("[^a-z]","",champ.find("div","info").find("div", "name").text.lower()), 
                                                  champ.find("div","kda").find("div").find("div").text.split(":")[0],
                                                  champ.find("div","played").find("div").find("div").text
                                                 ],
                                  champ_list))
            champ_list = champ_list[:(3 if len(champ_list) > 3 else len(champ_list))]
            return champ_list
        except Exception as e:
            logger.info(e)
            raise Exception("⚠️ 존재하지 않는 아이디 챔프")
        
    @staticmethod
    @alru_cache(maxsize=1024, ttl=60*60*24)
    async def get_info(league_name = "고라니를삼킨토끼#KR1",
                        timeout = 10.0, 
                        retry_cnt = 0,
                        if_null_return_error = False,
                        if_unranked_return_error = False
                    ):
        if retry_cnt >= 5:
            return None
        async with aiohttp.ClientSession(cookies = {"_ol":"en_US"},
                                        timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            logger.info(f"req to : https://www.op.gg/summoners/kr/{league_name.replace('#','-')}")
            async with session.get(f"https://www.op.gg/summoners/kr/{league_name.replace('#','-')}") as response:
                soup = BeautifulSoup(await response.text(), "html.parser")
                try:
                    tier = OPGG._get_tier(soup)
                    cl = OPGG._get_champ_list(soup)
                except Exception as e:
                    if if_null_return_error:
                        raise e
                    else:
                        tier = "unranked"
                        cl = []
                
                if if_unranked_return_error and tier == "unranked":
                    raise Exception("⚠️ 언랭 계정은 참가할 수 없습니다.")
                logger.info({"cur_tier" : tier,
                        "most_3" : cl})
                return {"cur_tier" : tier,
                        "most_3" : cl}
