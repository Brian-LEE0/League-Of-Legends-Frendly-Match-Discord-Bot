from mod.util.logger import logger
import aiohttp
from bs4 import BeautifulSoup
import re

class OPGG:
    @staticmethod
    def _get_tier(soup):
        try :
            tier = soup.find("div","rank-item")
            if tier is None :
                return "unranked"
            tier = tier.find("span").text.split(" ")[0].lower()
            return tier
        except Exception as e:
            logger.info(e)
            raise Exception("⚠ 존재하지 않는 아이디 티어")

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
            raise Exception("⚠ 존재하지 않는 아이디 챔프")
        
    @staticmethod
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
                    raise Exception("⚠ 언랭 계정은 참가할 수 없습니다.")
                logger.info({"cur_tier" : tier,
                        "most_3" : cl})
                return {"cur_tier" : tier,
                        "most_3" : cl}
