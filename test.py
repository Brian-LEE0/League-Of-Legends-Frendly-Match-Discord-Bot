
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
val_name = "으아악#1234"
print(f"https://valorant.op.gg/profile/{val_name.replace('#','-')}?_ol=en_US")
driver.get(f"https://valorant.op.gg/profile/{val_name.replace('#','-')}?_ol=en_US")
soup = BeautifulSoup(driver.page_source, "html.parser")
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
        print(e)
        return "unrank"
print(_get_tier(soup))