import datetime
from pymongo import MongoClient
client = MongoClient("192.168.0.207", 27017)
db = client["lol_fm_dbot"]
    
class Match:
    def __init__(self):
        self.coll = db["matchs"]
        pass
        
    def create_match(self, game, match_id, notion_id, max):
        self.coll.insert_one({
            "game": game,
            "match_id": match_id,
            "notion_id": notion_id,
            "max": max
        })
    
    def get_match(self, match_id):
        return self.coll.find_one({"match_id": match_id})
    
    def update_match(self, match_id, max):
        self.coll.update_one({"match_id": match_id}, {"$set": {"max": max}})
        
    def delete_match(self, match_id):
        self.coll.delete_one({"match_id": match_id})
        
    def get_all_match(self):
        cur = self.coll.find()
        return list(cur)
    
class Player:
    def __init__(self):
        self.coll = db["players"]
        
    def create_player(
        self,
        match_key,
        discord_id,
        lol_id1,
        lol_id2,
        lol_id3,
        
        position1,
        position2,
        position3,
        is_streamable="가능",
        suggestion=""
    ):
        self.coll.insert_one({
            "match_key": match_key,
            "discord_id": discord_id,
            "lol_id1": lol_id1,
            "lol_id2": lol_id2,
            "lol_id3": lol_id3,
            "position1": position1,
            "position2": position2,
            "position3": position3,
            "is_streamable": is_streamable,
            "datetime": datetime.datetime.now(),
            "suggestion": suggestion
        })
        
    def delete_player(self, match_key, discord_id):
        self.coll.delete_one({
            "match_key": match_key,
            "discord_id": discord_id
        })
    
    def get_player(self, match_key, discord_id):
        return self.coll.find_one({
            "match_key": match_key,
            "discord_id": discord_id
        })
    
    def get_players(self, match_key):
        cur = self.coll.find({"match_key": match_key})
        return list(cur)
