RPGDB = "logs/rpg.db"
pidfile = "logs/pid.txt"

TEXT = "text_message"
EMBED = "embed_message"
IMAGE = "image"
ERROR = "error_message"
KICK_REASON = "kick_message"
ACTION = "action_taken"

member_counter_message = "Members: {}"

SERVICE = False

# User Id's
CATEid = 183977132622348288
CHURROid = 224267646869176320
DOGEid = 226782069747875842
POLYid = 677221088081739776
KAPPAid = 237514437194547202
LOLIid = 182127850919428096
NYAid = 143037788969762816
RAZid = 185377283194748928
TRISTANid = 214708282864959489
WIZZid = 224620110277509120

# Server id's
PRIVATESERVERid = 226010107513798656
NINECHATid = 225995968703627265
LEGITSOCIALid = 319581059467575297
bot_list_servers = [264445053596991498, 110373943822540800, 374071874222686211]

# Channel id's
SNOWFLAKE_GENERAL = 378190443533434890

# Embeds
BASIC_COMMANDS_EMBED_COLOR = 0x008909
LOOKUP_COMMANDS_EMBED_COLOR = 0xFF0000
IMAGE_COMMANDS_EMBED_COLOR = 0x000000
WELCOME_EMBED_COLOR = 0xFF0000
MUSIC_EMBED_COLOR = 0x93CC04
STAR_EMBED_COLOR = 0xF9E000
HANGMAN_EMBED_COLOR = 0x007A01
STREAMER_EMBED_COLOR = 0x7900A8
STAR_EMOJI = "⭐"

ytdl_options = dict(
    format="bestaudio/best",
    extractaudio=True,
    audioformat="opus",
    noplaylist=True,
    default_search="auto",
    quiet=True,
    nocheckcertificate=True,
    restrictfilenames=True,
)

ytdl_before = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"

whitelists = [
    "image_spam_protection",
    "nickname_auto_change",
    "s_to_ringel_s",
    "uumuu_reaction",
]

# Blacklists
sponge_capitalization_blacklist = bot_list_servers
praise_the_sun_blacklist = bot_list_servers
ayy_lmao_blacklist = bot_list_servers + [NINECHATid]
lenny_blacklist = bot_list_servers
ded_blacklist = bot_list_servers
table_unflip_blacklist = bot_list_servers
bot_talk_blacklist = bot_list_servers
