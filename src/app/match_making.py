import asyncio
from quart import render_template, jsonify
from quart import Quart
from mod.util.mongo import Player
from mod.opgg import OPGG

app = Quart(__name__)

@app.route('/<tournament_id>')
async def index(tournament_id):
    
    return await render_template('player.html', tournament_id=tournament_id)

@app.route('/api/tournament/<tournament_id>/players', methods=['GET'])
async def get_players_data(tournament_id):
    
    # players_data = {
    #     "탑": [
    #         {"name": "A", "tier": "gold"},
    #         {"name": "B", "tier": "silver"}
    #     ],
    #     "정글": [
    #         {"name": "C", "tier": "platinum"},
    #         {"name": "D", "tier": "bronze"},
    #         {"name": "E", "tier": "diamond"}
    #     ],
    #     "미드": [
    #         {"name": "A", "tier": "gold", "sub": True},
    #         {"name": "F", "tier": "bronze"},
    #         {"name": "G", "tier": "platinum"}
    #     ],
    #     "원딜": [
    #         {"name": "H", "tier": "diamond"},
    #         {"name": "I", "tier": "master"}
    #     ],
    #     "서폿": [
    #         {"name": "J", "tier": "challenger"},
    #         {"name": "K", "tier": "bronze"},
    #         {"name": "L", "tier": "platinum"}
    #     ]
    # }
    
    db = Player()
    players = db.get_players(tournament_id)
    players_data = {
        "탑": [],
        "정글": [],
        "미드": [],
        "원딜": [],
        "서폿": []
    }
    
    async def fetch_player_info(player):
        players_opgg_info = await OPGG.get_info(league_name=player["lol_id1"])
        return players_opgg_info
    
    async def fetch_all_players_info(players):
        tasks = [fetch_player_info(player) for player in players]
        results = await asyncio.gather(*tasks)
        return results
    
    players_opgg_info = await fetch_all_players_info(players)
    
    for (player, opgg) in zip(players, players_opgg_info):
        tier = opgg["cur_tier"]
        p_info = {
                "name": player["lol_id1"],
                "tier": tier,
                "discord_id": str(player["discord_id"])
            }
        sub_info = p_info.copy()
        sub_info["sub"] = True
        if "position1" in player and player["position1"] != "":
            players_data[player["position1"]].append(p_info)
        if "position2" in player and player["position2"] != "":
            players_data[player["position2"]].append(sub_info)
        if "position3" in player and player["position3"] != "":
            players_data[player["position3"]].append(sub_info)
    
    #sort
    for key in players_data.keys():
        players_data[key] = sorted(players_data[key], key=lambda x: OPGG.tier_sort(x["tier"]), reverse=True)
    
    return jsonify(players_data)

