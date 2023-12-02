#DeprecationWarning
import requests
from mod.util.logger import logger
import os
from dotenv import load_dotenv
load_dotenv(f"../token_dev.env") # load all the variables from the env file
import unittest
# Riot Games API 키를 입력하세요.

API_KEY = os.environ['RIOT_API_KEY']
def get_summoner_info_by_name(summoner_name):
    base_url = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "ko,ko-KR;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://developer.riotgames.com",
        "X-Riot-Token": API_KEY
    }
    
    try:
        response = requests.get(base_url + summoner_name, headers=headers)
        response.raise_for_status()
        summoner_info = response.json()
        logger.info(f"summoner_name_retrieve: {summoner_info['name']}")
        return summoner_info
        # summoner_info has some keys like 'id', 'accountId', 'puuid', 'name', 'profileIconId', 'revisionDate', 'summonerLevel'
    except requests.exceptions.RequestException as e:
        logger.info(f"Error: {e}")
        return None
    
def get_summoner_info_by_aid(summoner_aid):
    base_url = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-account/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "ko,ko-KR;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://developer.riotgames.com",
        "X-Riot-Token": API_KEY
    }
    
    try:
        response = requests.get(base_url + summoner_aid, headers=headers)
        response.raise_for_status()
        summoner_info = response.json()
        logger.info(f"summoner_puuid_retrieve: {summoner_info['name']}")
        return summoner_info
        # summoner_info has some keys like 'id', 'accountId', 'puuid', 'name', 'profileIconId', 'revisionDate', 'summonerLevel'
    except requests.exceptions.RequestException as e:
        logger.info(f"Error: {e}")
        return None
    

class retrieve_test(unittest.TestCase):

    def test(self) :
        global API_KEY
        from dotenv import load_dotenv
        load_dotenv(f"../token_dev.env") # load all the variables from the env file
        API_KEY = os.environ['RIOT_API_KEY']
        info = get_summoner_info_by_name("쪼렙이다말로하자")
        get_summoner_info_by_aid(info['accountId'])['name']