from mod.util.logger import logger
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

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
driver = webdriver.Chrome(options=options)
import asyncio
import re

class OPGG:
    @staticmethod
    def _get_tier(soup):
        try :
            rank_solo_tier = soup.find("strong","tier-rank").text.lower().strip()
            if rank_solo_tier and rank_solo_tier == "unrank":
                prev_tier_list = soup.find("ul", "prev-tier-list")
                if prev_tier_list is None :
                    return "unrank"
                prev_tier = prev_tier_list.find("li").text.split()[2].lower()
                return prev_tier
            return rank_solo_tier.split()[0]
        except Exception as e:
            logger.info(e)
            return None

    @staticmethod
    def _get_champ_list(soup):
        try :
            champ_list = soup.find("table","css-1iy7n7q").find_all("tr")
            champ_list = list(map(lambda champ : [re.sub("[^a-z]","",champ.find("div","name-avg-score").find("a").text.lower())],
                                  champ_list))
            champ_list = champ_list[:(3 if len(champ_list) > 3 else len(champ_list))]
            return champ_list
        except Exception as e:
            logger.info(e)
            return []
        
    @staticmethod
    async def get_info(val_name = "고라니를삼킨토끼",
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
            raise Exception(f"⚠ https://valorant.op.gg/profile/{val_name.replace('#','-')} 에서 비공개 상태를 해제 해주세요.")
        tier = OPGG._get_tier(soup)
        cl = OPGG._get_champ_list(soup)
        logger.info({"cur_tier" : tier,
                "most_3" : cl})
        return {"cur_tier" : tier,
                "most_3" : cl}