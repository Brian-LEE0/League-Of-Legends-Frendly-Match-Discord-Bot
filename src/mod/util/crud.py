import mod.util.cache as cache

def get_league_from_discord_id(discord_id):
    return cache.get_str_from_redis(f"league_id:{discord_id}")

def set_discord_id_to_league(discord_id, league_id):
    return cache.save_str_to_redis(f"league_id:{discord_id}",league_id)