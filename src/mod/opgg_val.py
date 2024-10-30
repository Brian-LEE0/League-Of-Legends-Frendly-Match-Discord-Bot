import aiohttp
from mod.util.logger import logger
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from async_lru import alru_cache
from typing import Dict

options = Options()
options.page_load_strategy = 'eager'
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument("--disable-extensions")
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'")
options.add_experimental_option('useAutomationExtension', False)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
import re

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
        elif tier == "diamond":
            return 6
        elif tier == "immortal":
            return 7
        elif tier == "radiant":
            return 8
        else:
            return -1
        
    @staticmethod
    def _get_tier(soup):
        try :
            rank_solo_tier = soup.find("strong","tier-rank").text.lower().strip()
            if rank_solo_tier and rank_solo_tier == "unrank":
                prev_tier_list = soup.find("ul", "prev-tier-list").find("li")
                if prev_tier_list is None :
                    return "unrank"
                prev_tier = prev_tier_list.text.split()[2].lower()
                return prev_tier
            return rank_solo_tier.split()[0]
        except Exception as e:
            logger.info(e)
            return "unrank"

    @staticmethod
    def _get_champ_list(soup):
        try :
            print(soup.find("table","css-1iy7n7q"))
            champ_list = soup.find("table","css-1iy7n7q").find("tr")
            champ_list = list(map(lambda champ : [re.sub("[^a-z]","",champ.find("div","name-avg-score").find("a").text.lower())],
                                  champ_list))[:3]
            print(champ_list)
            return champ_list
        except Exception as e:
            logger.info(e)
            return []
        
    @staticmethod
    @alru_cache(maxsize=1024, ttl=60*60*24)
    async def get_info(val_name = "고라니를삼킨토끼#KR1",
                        timeout = 10.0, 
                        retry_cnt = 0):
        if retry_cnt >= 5:
            return None
        driver = webdriver.Chrome(options=options)
        driver.get(f"https://valorant.op.gg/profile/{val_name.replace('#','-')}?_ol=en_US")
        html = driver.page_source
        driver.close()
        soup = BeautifulSoup(html, "html.parser")
        is_private = soup.find("div","css-nam5yt")
        if is_private is not None :
            # raise Exception(f":warning: https://valorant.op.gg/profile/{val_name.replace('#','-')} 에서 비공개 상태를 해제 해주세요.")
            return {"cur_tier" : "unrank",
                "most_3" : []}
        tier = OPGG._get_tier(soup)
        if tier is None :
            return {"cur_tier" : "unrank",
                "most_3" : []}
            # raise Exception(f":warning: https://valorant.op.gg/profile/{val_name.replace('#','-')} 에서 계정 상태를 확인하고 다시 신청해주세요.")
        cl = OPGG._get_champ_list(soup)
        logger.info({"cur_tier" : tier,
                "most_3" : cl})
        return {"cur_tier" : tier,
                "most_3" : cl}
        
    @staticmethod
    @alru_cache(maxsize=1024, ttl=60*60*24)
    async def get_map(timeout = 10.0, 
                        retry_cnt = 0,
                        if_null_return_error = False,
                        if_unranked_return_error = False
                    ) -> Dict[str, str]:
        if retry_cnt >= 5:
            return None
        async with aiohttp.ClientSession(cookies = {"_ol":"en_US"},
                                        timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            logger.info(f"req to : https://valorant.op.gg/maps")
            async with session.get(f"https://valorant.op.gg/maps") as response:
                soup = BeautifulSoup(await response.text(), "html.parser")
                try:
                    map_list = soup.find("ul", "css-cwj72x").find_all("li")
                    map_list = { m.find("div","name").text: m.find("img")["src"] for m in map_list }
                    return map_list
                except Exception as e:
                    raise e