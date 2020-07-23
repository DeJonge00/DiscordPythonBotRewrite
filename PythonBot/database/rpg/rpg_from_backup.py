from api.rpg.objects import rpgplayer
from database.rpg import player
import json

if __name__ == "__main__":
    with open("rpg_data_dump.json") as f:
        data = json.load(f)
    for p in data:
        p["userid"] = str(p.get("userid"))
        player.update_player(rpgplayer.dict_to_player(p))
