from database.rpg import rpg_main, player as rpg_player
from database.rpg import channels as rpg_channels
from api.rpg.objects.rpgplayer import RPGPlayer, BUSY_DESC_BOSSRAID, BUSY_DESC_ADVENTURE
from api.rpg.objects.rpgpet import RPGPet
from random import randint


def test_rpg_channel():
    server = 1
    channel = 2
    rpg_channels.set_rpg_channel(server, channel)
    channel = rpg_channels.get_rpg_channel(server)
    print("Setchannel/getchannel", channel, channel == channel)

    channel = 3
    rpg_channels.set_rpg_channel(server, channel)
    channel = rpg_channels.get_rpg_channel(server)
    print("Setchannel/getchannel", channel, channel == channel)

    rpg_main.get_table(rpg_main.RPG_PLAYER_TABLE).drop()


def test_rpg_player():
    player = RPGPlayer(userid=1, picture_url="", username="owo", health=10)

    try:
        rpg_player.get_player(player.userid, player.name)
    except ValueError:
        print("No user successful")

    rpg_player.update_player(player)
    print(player.name)
    for k, v in rpg_player.get_player(player.userid, player.name).as_dict().items():
        print(k, v)

    rpg_main.get_table(rpg_main.RPG_PLAYER_TABLE).drop()


def test_top_list():
    players = [
        RPGPlayer(userid=x, picture_url="", username=str(x), exp=x).as_dict()
        for x in range(400)
    ]
    rpg_channels.get_table(rpg_main.RPG_PLAYER_TABLE).insert_many(players)

    print("0-10")
    for i in rpg_main.get_top_players(group="exp", start=0, amount=10):
        print(i)

    print("11-20")
    for i in rpg_main.get_top_players(group="exp", start=300, amount=10):
        print(i)

        rpg_main.get_table(rpg_main.RPG_PLAYER_TABLE).drop()


def test_boss_parties():
    players = [RPGPlayer(userid=x, picture_url="", username=str(x)) for x in range(400)]
    for p in players:
        p.set_busy(BUSY_DESC_BOSSRAID, 10, randint(0, 10))
    rpg_main.get_table(rpg_main.RPG_PLAYER_TABLE).insert_many(
        [x.as_dict() for x in players]
    )

    for k, v in rpg_main.get_boss_parties().items():
        print(k, len(v))

    rpg_main.get_table(rpg_main.RPG_PLAYER_TABLE).drop()


def test_add_stat():
    player = RPGPlayer(
        userid=1,
        picture_url="",
        username="owo",
        pets=[RPGPet(name=str(x)) for x in range(2)],
    )
    rpg_player.update_player(player)
    exp = player.exp
    rpg_player.add_stats(player.userid, "exp", 10)
    print(
        "Player exp from-to", exp, rpg_player.get_player(player.userid, player.name).exp
    )

    exp = [p.exp for p in rpg_player.get_player(player.userid, player.name).pets]
    rpg_player.add_pet_stats(player.userid, "exp", 10)
    print(
        "Pet exp from-to",
        exp,
        [p.exp for p in rpg_player.get_player(player.userid, player.name).pets],
    )

    rpg_main.get_table(rpg_main.RPG_PLAYER_TABLE).drop()


def test_decrement_busy_counters():
    players = [RPGPlayer(userid=x, picture_url="", username=str(x)) for x in range(10)]
    for p in players:
        p.set_busy(BUSY_DESC_ADVENTURE, 20, randint(0, 10))
    rpg_main.get_table(rpg_main.RPG_PLAYER_TABLE).insert_many(
        [x.as_dict() for x in players]
    )

    rpg_main.decrement_busy_counters()
    for x in rpg_main.get_table(rpg_main.RPG_PLAYER_TABLE).find():
        print(x.get("busy").get("time"))

    rpg_main.get_table(rpg_main.RPG_PLAYER_TABLE).drop()


#
# def test_get_done_players():
#     players = [RPGPlayer(userid=x, picture_url='', username=str(x)) for x in range(10)]
#     for p in players:
#         p.set_busy(BUSY_DESC_ADVENTURE, randint(0, 2), '1')
#     rpg_main.get_table(rpg_main.RPG_PLAYER_TABLE).insert_many([x.as_dict() for x in players])
#
#     print('Done players', len(list(rpg_main.get_done_players())))
#     print('Player busytimes', [x.get('busy').get('time') for x in rpg.get_table(rpg.RPG_PLAYER_TABLE).find()])
#
#     rpg.get_table(rpg.RPG_PLAYER_TABLE).drop()
