import datetime
import logging
import math
import os
import os.path
import random
import traceback
from io import BytesIO

import discord
import requests
from PIL import Image, ImageFont, ImageDraw
from discord import Message, Reaction, DMChannel, File, Embed
from discord.ext import commands
from discord.ext.commands.context import Context

from api.rpg import constants as rpgc
from api.rpg.objects.rpgcharacter import RPGCharacter
from api.rpg.objects.rpgmonster import RPGMonster
from api.rpg.objects.rpgpet import RPGPet
from api.rpg.objects.rpgplayer import (
    RPGPlayer,
    BUSY_DESC_NONE,
    BUSY_DESC_WANDERING,
    BUSY_DESC_BOSSRAID,
    BUSY_DESC_WORKING,
    BUSY_DESC_ADVENTURE,
    BUSY_DESC_TRAINING,
    minadvtime,
    maxadvtime,
    minwandertime,
    maxwandertime,
)
from api.rpg.rpg_helper_functions import construct_battle_report, add_health_rep
from commands.rpg import rpggameactivities
from config import constants
from core import logging as log
from core.bot import PythonBot
from core.utils import shorten_number
from database.rpg import (
    rpg_main as db_rpg,
    channels as db_rpg_channels,
    player as db_rpg_player,
)
from secret.secrets import font_path

RPG_EMBED_COLOR = 0x710075
STANDARD_BATTLE_TURNS = 50
BATTLE_TURNS = {"Bossbattle": 200}

logging.basicConfig(
    filename="logs/rpg_main.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


class RPGGame(commands.Cog):
    def __init__(self, my_bot: PythonBot):
        self.bot = my_bot
        self.bot.rpg_game = self
        self.top_lists = {}
        self.logger = logging.getLogger(__name__)

    async def check_role(
        self, role: str, message: discord.Message, error="You"
    ) -> bool:
        if role not in [x[0] for x in rpgc.names.get("role")]:
            c = "{} are still Undead. Please select a class with '{}rpg role' in order to start to play!".format(
                error, await self.bot.get_prefix(message)
            )
            await self.bot.send_message(destination=message.channel, content=c)
            return False
        return True

    def calculate_battle_result(self, p1, p2):
        if sum([x.get_health() for x in p1]) <= 0:
            if (len(p1) == 1) and (len(p2) == 1):
                result = "{} ({}) laughs while walking away from {}'s corpse".format(
                    p2[0].name, p2[0].get_health(), p1[0].name
                )
                healthrep = None
            else:
                result = "{}'s party completely slaughtered {}'s party".format(
                    p2[0].name, p1[0].name
                )
                healthrep = add_health_rep(p1 + p2)
        else:
            result = "The battle lasted long, both parties are exhausted.\nThey agree on a draw this time"
            healthrep = add_health_rep(p1 + p2)
        return result, healthrep

    async def send_battle_report(
        self,
        embed: Embed,
        battle_report_text,
        channel,
        battle_report_stats,
        healthrep,
        result,
    ):
        for i in range(len(battle_report_text) - 1):
            embed.add_field(
                name="Battle report", value=battle_report_text[i], inline=False
            )
            await self.bot.send_message(channel, embed=embed)
            embed = discord.Embed(colour=RPG_EMBED_COLOR)

        text_length = len(battle_report_text[-1])
        embed.add_field(
            name="Battle report", value=battle_report_text[-1], inline=False
        )

        if text_length > 900:
            await self.bot.send_message(channel, embed=embed)
            embed = discord.Embed(colour=RPG_EMBED_COLOR)
            text_length = 0

        embed.add_field(name="Stats", value=battle_report_stats)
        text_length += len(battle_report_stats)

        if text_length > 900:
            await self.bot.send_message(channel, embed=embed)
            embed = discord.Embed(colour=RPG_EMBED_COLOR)
            text_length = 0

        if healthrep:
            embed.add_field(name="Health report", value=healthrep)
            text_length += len(healthrep)
            if text_length > 900:
                await self.bot.send_message(channel, embed=embed)
                embed = discord.Embed(colour=RPG_EMBED_COLOR)

        embed.add_field(name="Result", value=result)
        try:
            await self.bot.send_message(channel, embed=embed)
        except discord.HTTPException:
            try:
                await self.bot.send_message(
                    channel, "\n".join(battle_report_text + [result])
                )
            except discord.HTTPException as e:
                log.announcement(
                    channel.guild.name, e.text + " while sending battle report"
                )

    async def resolve_battle(
        self,
        battle_name: str,
        channel: discord.TextChannel,
        p1: [RPGCharacter],
        p2: [RPGMonster],
        winner_pic=False,
    ):

        # Gather report header information
        embed = discord.Embed(colour=RPG_EMBED_COLOR)
        title = ""
        if len(p1) == 1:
            title += "{} ({}hp, {})".format(
                p1[0].name,
                p1[0].get_health(),
                rpgc.elementnames.get(p1[0].get_element())[0],
            )
        else:
            title += "A party of {}".format(len(p1))
        title += " vs "
        if len(p2) == 1:
            title += "{} ({}hp, {})".format(
                p2[0].name,
                p2[0].get_health(),
                rpgc.elementnames.get(p2[0].get_element())[0],
            )
        else:
            title += "A party of {}".format(len(p2))
        embed.add_field(name=battle_name, value=title, inline=False)
        battle_report = []
        i = 0

        # Save healthvalues in case of mockbattle
        h1 = []
        h2 = []
        for i in range(len(p1)):
            h1.append(p1[i].get_health())
        for i in range(len(p2)):
            h2.append(p2[i].get_health())

        # Fight starts
        # Fight stops when either party (not including pets) runs out of health
        turns = BATTLE_TURNS.get(battle_name, STANDARD_BATTLE_TURNS)
        while (
            (i < turns)
            and (sum([x.get_health() for x in p1]) > 0)
            and (sum([x.get_health() for x in p2]) > 0)
        ):
            attackers = list(p1)

            # Pets are added to allow them to attack
            for p in [x for x in p1 if isinstance(x, RPGPlayer) and x.get_health() > 0]:
                attackers += p.pets
            for attacker in attackers:
                if attacker.get_health() > 0:

                    # Choose attackers target
                    defs = [x for x in p2 if x.get_health() > 0]
                    if len(defs) <= 0:
                        break
                    defender = random.choice(defs)
                    ws = random.randint(
                        0, attacker.get_weaponskill() + defender.get_weaponskill()
                    )

                    # Determine whether the attacker hits and for how much damage
                    if ws < attacker.get_weaponskill():
                        if ws < min(
                            int(attacker.get_weaponskill() / 3), attacker.get_critical()
                        ):
                            damage = int(
                                (
                                    2
                                    + (
                                        math.log(
                                            max(
                                                0,
                                                attacker.get_critical()
                                                - int(attacker.get_weaponskill() / 3),
                                            )
                                            + 1
                                        )
                                    )
                                    / pow(2 * attacker.get_level(), 0.3)
                                )
                                * attacker.get_damage(defender.get_element())
                            )
                            battle_report.append(
                                (
                                    attacker,
                                    defender,
                                    damage,
                                    True,
                                )
                            )

                        else:
                            damage = int(
                                math.floor(
                                    math.sqrt(random.randint(100, 400) / 100)
                                    * attacker.get_damage(defender.get_element())
                                )
                            )
                            battle_report.append(
                                (
                                    attacker,
                                    defender,
                                    damage,
                                    False,
                                )
                            )

                        defender.add_health(
                            -1 * damage, death=not (battle_name == "Mockbattle")
                        )

            # Switch attackers and defenders roles
            p3 = p1
            p1 = p2
            p2 = p3
            i += 1

        battle_report_text, battle_report_stats = construct_battle_report(
            len(title), battle_report
        )
        result, healthrep = self.calculate_battle_result(p1, p2)

        # Switch teams to original positions
        if i % 2 == 1:
            p3 = p1
            p1 = p2
            p2 = p3

        winner = sum([(x.get_health() / x.get_max_health()) for x in p1]) > sum(
            [(x.get_health() / x.get_max_health()) for x in p2]
        )
        if winner_pic and winner:
            embed.set_thumbnail(url=p1[0].picture_url)
        else:
            embed.set_thumbnail(url=p2[0].picture_url)

        await self.send_battle_report(
            embed, battle_report_text, channel, battle_report_stats, healthrep, result
        )

        # Return who won
        # Winning means having dealt a higher percentage of damage
        if winner:
            return 1
        return 2

    async def boss_battle(self):
        print("Boss time!")

        boss_parties = db_rpg.get_boss_parties()
        for serverid in boss_parties.keys():
            party = boss_parties.get(serverid)
            try:
                if len(party) > 0:
                    channel = self.bot.get_channel(
                        db_rpg_channels.get_rpg_channel(int(serverid))
                    )
                    if not channel:
                        print("No channel for {}".format(serverid))
                        return

                    # Determine bossbattle difficulty
                    lvl = max([x.get_bosstier() for x in party])
                    bosses = []
                    while (3 * len(bosses)) < len(party):
                        (name, elem, pic) = random.choice(rpgc.bosses)
                        bosses.append(
                            RPGMonster(
                                name=name,
                                picture_url=pic,
                                health=int(52 * lvl * lvl),
                                damage=int(lvl * lvl * 1.1),
                                ws=int(lvl * lvl * 0.6),
                                element=elem,
                            )
                        )

                    winner = await self.resolve_battle(
                        "Bossbattle", channel, party, bosses
                    )

                    if winner == 1:
                        # Reward the winners with exp, money and a bosstier
                        for p in party:
                            reward = 32 * lvl * lvl * len(bosses) / len(party)
                            p.add_exp(reward)
                            p.add_bosstier()
                            for pet in p.pets:
                                pet.add_exp(
                                    0.13 * reward
                                    if p.role == rpgc.names.get("role")[2][0]
                                    else 0.1 * reward
                                )

                        # Chance to reward a player with a new pet
                        if random.randint(0, 100) < 35:
                            petwinner = random.choice(party)
                            petname = "Pet " + bosses[0].name
                            pet = RPGPet(
                                name=petname,
                                picture_url=bosses[0].picture_url,
                                damage=petwinner.get_bosstier() * 10,
                                weaponskill=petwinner.get_bosstier(),
                            )
                            if pet and petwinner.add_pet(pet):
                                await self.bot.send_message(
                                    channel,
                                    "{} found a baby {}, a new pet!".format(
                                        petwinner.name, petname
                                    ),
                                )

            except Exception as e:
                log.announcement("All guilds", str(e) + " while resolving boss battle")
            # Reset players busy status and clear past bossraid info
            for p in party:
                p.reset_busy()
                db_rpg_player.update_player(p)

    async def adventure_encounter(
        self, player: RPGPlayer, channel: discord.TextChannel
    ):
        # Choose monster and determine battle difficulty
        (name, elem, pic) = random.choice(rpgc.monsters)
        lvl = player.get_level()
        winner = await self.resolve_battle(
            "Adventure encounter",
            channel,
            [player],
            [
                RPGMonster(
                    name=name,
                    picture_url=pic,
                    health=(int(10 + math.floor(player.exp / 75))),
                    damage=int(math.floor(7 * lvl)),
                    ws=int(math.floor(1 + (0.085 * (player.exp ** 0.62)))),
                    element=elem,
                )
            ],
        )

        # Reward victory
        if winner == 1:
            lvl = math.pow(player.get_level(), 0.9)
            player.add_exp(int(110 * lvl))
            player.add_money(int(25 * lvl))
            for p in player.pets:
                p.add_exp(
                    13 * lvl
                    if player.role == rpgc.names.get("role")[2][0]
                    else 10 * lvl
                )
        db_rpg_player.update_player(player)

    async def adventure_secret(self, player: RPGPlayer, channel: discord.TextChannel):
        secrets_list = rpgc.adventureSecrets
        (name, stat, amount) = secrets_list[random.randint(0, len(secrets_list) - 1)]

        if stat.lower() == "health":
            amount *= max(1, int(player.get_level() / 4))
            db_rpg_player.add_stats(player.userid, "stats.health", amount)
        elif stat.lower() == "weaponskill":
            amount *= max(1, int(math.pow(player.get_level(), 0.25)))
            db_rpg_player.add_stats(player.userid, "stats.weaponskill", amount)
        elif stat.lower() == "money":
            amount *= max(1, int(math.sqrt(player.get_level())))
            db_rpg_player.add_stats(player.userid, "money", amount)
        elif stat.lower() == "exp":
            amount *= max(1, int(math.sqrt(player.get_level() / 2)))
            db_rpg_player.add_stats(player.userid, "exp", amount)
        elif stat.lower() == "damage":
            amount *= max(1, int(math.pow(player.get_level(), 0.4)))
            db_rpg_player.add_stats(player.userid, "stats.damage", amount)
        embed = discord.Embed(colour=RPG_EMBED_COLOR)
        embed.add_field(
            name="Adventure secret found",
            value="{}, {}\n{} +{}".format(player.name, name, stat, amount),
        )
        await self.bot.send_message(channel, embed=embed)

    async def do_adventure(
        self, user_id: int, name: str, pic_url: str, busy: dict, health=1
    ):
        if random.randint(0, 4) <= 0:
            player = db_rpg_player.get_player(user_id, name, pic_url)
            await self.adventure_encounter(
                player, self.bot.get_channel(busy.get("channel"))
            )
            return player.get_health()
        return await self.do_wander(user_id, name, pic_url, busy, health=health)

    async def do_wander(
        self, user_id: int, name: str, pic_url: str, busy: dict, health=1
    ):
        if random.randint(0, 14) <= 0:
            player = db_rpg_player.get_player(user_id, name, pic_url)
            await self.adventure_secret(
                player, self.bot.get_channel(busy.get("channel"))
            )
            return player.get_health()
        return health

    async def do_busy_per_person(
        self, name: str, user_id: int, pic_url: str, busy, health
    ):
        if busy.get("description") == BUSY_DESC_ADVENTURE:
            health = await self.do_adventure(user_id, name, pic_url, busy, health)
        if busy.get("description") == BUSY_DESC_WANDERING:
            health = await self.do_wander(user_id, name, pic_url, busy, health)

        if busy.get("time") > 0 and health > 0:
            return

        if busy.get("description") == BUSY_DESC_NONE:
            db_rpg_player.reset_busy(user_id)
            return

        # Send done message
        embed = discord.Embed(colour=RPG_EMBED_COLOR)
        embed.set_author(name=self.bot.user.name)
        if busy.get("description") == BUSY_DESC_ADVENTURE:
            action_type = "adventure"
            action_name = "adventuring"
        elif busy.get("description") == BUSY_DESC_TRAINING:
            action_type = action_name = "training"
        elif busy.get("description") == BUSY_DESC_WANDERING:
            action_type = action_name = "wandering"
        elif busy.get("description") == BUSY_DESC_WORKING:
            action_type = "work"
            action_name = "working"
        else:
            action_type = action_name = "Unknown"
        if health > 0:
            embed.add_field(
                name="Ended {}".format(action_type),
                value="You are now done {}".format(action_name),
            )
        else:
            embed.add_field(
                name="You Died".format(action_type),
                value="You were killed on one of your adventures".format(action_name),
            )
            embed.set_thumbnail(
                url="https://res.cloudinary.com/teepublic/image/private/s--_1_FlGA"
                "a--/t_Preview/b_rgb:191919,c_limit,f_jpg,h_630,q_90,w_630/v146"
                "6191557/production/designs/549487_1.jpg"
            )
        c = self.bot.get_user(user_id)
        if c:
            await self.bot.send_message(c, embed=embed)
        else:
            print(
                "Channel not found, {} is done with {}".format(
                    name, busy.get("desription")
                )
            )
        db_rpg_player.reset_busy(user_id)

    async def do_busy(self):
        db_rpg.decrement_busy_counters()
        pl = db_rpg.get_busy_players()
        for name, userid, pic_url, busy, health in pl:
            try:
                await self.do_busy_per_person(name, userid, pic_url, busy, health)
            except Exception:
                print(traceback.format_exc())
                self.logger.error(traceback.format_exc())

    async def do_boss_raids_warning(self):
        boss_parties = db_rpg.get_boss_parties()
        for p in [x for x in boss_parties if x]:
            channel = self.bot.get_channel(db_rpg_channels.get_rpg_channel(p))
            if not channel:
                print("No channel for {}".format(p))
                return
            await self.bot.send_message(
                channel,
                "A party of {} is going to fight the boss in 5 minutes!!\nJoin fast if"
                " you want to participate".format(len(boss_parties.get(p))),
            )

    async def game_tick(self, time):
        try:
            # if time.minute % 5 == 0:
            #     print(time.strftime("%H:%M:%S"))
            if time.minute == 55:
                await self.do_boss_raids_warning()
            if time.minute == 0:
                await self.boss_battle()
                self.bot.rpg_shop.weapons = {}
                self.bot.rpg_shop.armors = {}

        except Exception:
            print(traceback.format_exc())
            self.logger.error(traceback.format_exc())
        await self.do_busy()

        db_rpg.do_health_regen()

    @staticmethod
    def handle(message: Message):
        data = db_rpg_player.get_player(
            message.author.id, message.author.display_name, message.author.avatar_url
        )
        if data.role not in [x[0] for x in rpgc.names.get("role")]:
            return
        # Reward player based on rpg level with money
        i = round(
            pow((data.get_level()) + 1, 1 / 2)  # level bonus
            * max(0, min(80, int((len(message.content) - 3) / 1.5)))
        )  # Text bonus
        if data.busydescription in [BUSY_DESC_TRAINING, BUSY_DESC_BOSSRAID]:
            i *= 0.5
        db_rpg_player.add_stats(message.author.id, "money", int(i))
        db_rpg_player.add_stats(message.author.id, "exp", 1)

    async def send_help_message(self, ctx: Context):
        prefix = await self.bot.get_prefix(ctx.message)
        c = "Your '{}rpg' has been heard, you will be send the commands list for the rpg game".format(
            prefix
        )
        await self.bot.send_message(destination=ctx.channel, content=c)

        # Intro/setup help
        embed = discord.Embed(colour=RPG_EMBED_COLOR)
        embed.set_author(name="RPG Help: Basics", icon_url=self.bot.user.avatar_url)
        embed.add_field(
            name="Introduction",
            value="Welcome adventurer, this game grants you the opportunity to slay "
            "monsters and rule a realm. You can train yourself and buy upgrades "
            "at the shop, and when you are done with adventuring, you can even "
            "challenge a boss every hour with a group of friends.",
            inline=False,
        )
        embed.add_field(
            name="Basics",
            value="Talking gains you extra money\n"
            "If it sounds like a logical alias, it probably is\n"
            "Your health regenerates every minute\n"
            "The weaponsmith refills his inventory every hour\n"
            "A boss can be fought at the hour mark",
            inline=False,
        )
        embed.add_field(
            name="{}rpg [role|r|class|c]".format(prefix),
            value="Switch your role on the battlefield (A role is needed to play the game)",
            inline=False,
        )
        embed.add_field(
            name="{}rpg [setchannel]".format(prefix),
            value="This sets the channel for bossbattle results "
            "(It only needs to be done once per server by an admin)",
            inline=False,
        )
        await self.bot.send_message(ctx.message.author, embed=embed)

        # RPG infos
        embed = discord.Embed(colour=RPG_EMBED_COLOR)
        embed.set_author(
            name="RPG Help: Status Information", icon_url=self.bot.user.avatar_url
        )
        embed.add_field(
            name="{}rpg [info|i|stats|status] <user>".format(prefix),
            value="Show your or another user's game statistics",
            inline=False,
        )
        embed.add_field(
            name="{}rpg [info|i|stats|status] [weapon|w|armor|a] <user>".format(prefix),
            value="Show your or another user's weapon statistics",
            inline=False,
        )
        embed.add_field(
            name="{}rpg [levelup|lvl|lvlup]".format(prefix),
            value="Choose a reward when you leveled up",
            inline=False,
        )
        embed.add_field(
            name="{}rpg king".format(prefix),
            value="Show the current King of the server",
            inline=False,
        )
        embed.add_field(
            name="{}rpg king [c|b|challenge|battle]".format(prefix),
            value="Challenge the current King and try to take his spot (level 10+)",
            inline=False,
        )
        embed.add_field(
            name="{}rpg [party|p]".format(prefix),
            value="Show the brave souls that will be attacking the boss at the hour mark",
            inline=False,
        )
        embed.add_field(
            name="{}rpg [top|t] <exp|money|bosstier> <page>".format(prefix),
            value="Show the best players of the game",
            inline=False,
        )
        await self.bot.send_message(ctx.message.author, embed=embed)

        # RPG what can you actually do help
        embed = discord.Embed(colour=RPG_EMBED_COLOR)
        embed.set_author(
            name="RPG Help: Things to do", icon_url=self.bot.user.avatar_url
        )
        embed.add_field(
            name="{}rpg [adventure|a] <minutes>".format(prefix),
            value="Go on an adventure, find monsters to slay to gain exp",
            inline=False,
        )
        embed.add_field(
            name="{}rpg [wander|w] <minutes>".format(prefix),
            value="Go wandering, you might find a great treasure!",
            inline=False,
        )
        embed.add_field(
            name="{}rpg [battle|b] <user>".format(prefix),
            value="Battle another user for the lolz, no exp will be gained and no health will be lost",
            inline=False,
        )
        embed.add_field(
            name="{}rpg [join|j]".format(prefix),
            value="Join the hourly boss raid (warning, don't try this alone)",
            inline=False,
        )
        await self.bot.send_message(ctx.message.author, embed=embed)

        # Shop/training/work
        embed = discord.Embed(colour=RPG_EMBED_COLOR)
        embed.set_author(
            name="RPG Help: Improve your character", icon_url=self.bot.user.avatar_url
        )
        embed.add_field(
            name="{}shop".format(prefix),
            value="Show the rpg shop inventory",
            inline=False,
        )
        embed.add_field(
            name="{}shop [item|i|buy] <item> <amount>".format(prefix),
            value="Buy <amount> of <item> from the shop",
            inline=False,
        )
        embed.add_field(
            name="{}shop [weapon|w] <number>".format(prefix),
            value="Buy a certain weapon from the shop (hourly refresh of stock)",
            inline=False,
        )
        embed.add_field(
            name="{}shop [armor|a] <number>".format(prefix),
            value="Buy a certain armor from the shop (hourly refresh of stock)",
            inline=False,
        )
        embed.add_field(
            name="{}train".format(prefix),
            value="Show the available training sessions",
            inline=False,
        )
        embed.add_field(
            name="{}train <stat> <amount>".format(prefix),
            value="Train yourself for <amount> points of the chosen <stat>",
            inline=False,
        )
        embed.add_field(
            name="{}work <amount>".format(prefix),
            value="Work an interesting job for some money, for <amount> minutes",
            inline=False,
        )
        await self.bot.send_message(ctx.message.author, embed=embed)

        # Pets help
        embed = discord.Embed(colour=RPG_EMBED_COLOR)
        embed.set_author(name="RPG Help: Pets", icon_url=self.bot.user.avatar_url)
        embed.add_field(
            name="{}rpg [pet,pets] <user>".format(prefix),
            value="Show the pets owned by you or another user",
            inline=False,
        )
        embed.add_field(
            name="{}rpg [pet,pets] [release,remove,r] <pet name>".format(prefix),
            value="Release all pets with the name <pet name>, be warned, they will be gone forever!",
            inline=False,
        )
        embed.set_footer(
            text="Suggestions? Feel free to message me or join my server (see {}help for details)".format(
                prefix
            )
        )
        await self.bot.send_message(ctx.message.author, embed=embed)

    # RPG intro/help
    @commands.group(
        pass_context=1,
        aliases=["Rpg", "b&d", "B&d", "bnd", "Bnd"],
        help="Get send an overview of the rpg game's commands",
    )
    async def rpg(self, ctx: Context):
        if ctx.invoked_subcommand is None and ctx.message.content == "{}rpg".format(
            await self.bot.get_prefix(ctx.message)
        ):
            if not await self.bot.pre_command(
                message=ctx.message, channel=ctx.channel, command="rpg help"
            ):
                return
            await self.send_help_message(ctx)

    # {prefix}rpg adventure #
    @rpg.command(pass_context=1, help="RPG game help message!", aliases=["Help"])
    async def help(self, ctx: Context):
        if not await self.bot.pre_command(
            message=ctx.message, channel=ctx.channel, command="rpg help"
        ):
            return
        await self.send_help_message(ctx)

    # {prefix}rpg adventure #
    @rpg.command(
        pass_context=1, aliases=["Adventure", "a", "A"], help="Go on an adventure!"
    )
    async def adventure(self, ctx: Context, *args):
        if not await self.bot.pre_command(
            message=ctx.message, channel=ctx.channel, command="rpg adventure"
        ):
            return
        data = db_rpg_player.get_player(
            ctx.message.author.id,
            ctx.message.author.display_name,
            ctx.message.author.avatar_url,
        )
        if not await self.check_role(data.role, ctx.message):
            return

        if len(args) > 0:
            try:
                n = int(args[0])
            except ValueError:
                n = 10
        else:
            n = 10

        if data.busydescription != BUSY_DESC_NONE:
            await self.bot.send_message(
                destination=ctx.channel, content="You are already doing other things"
            )
            return
        if n < minadvtime:
            await self.bot.send_message(
                destination=ctx.channel,
                content="You came back before you even went out, 0 exp earned",
            )
            return
        if n > (maxadvtime + data.extratime):
            await self.bot.send_message(
                destination=ctx.channel,
                content="You can only go on an adventure for {} minutes".format(
                    maxadvtime + data.extratime
                ),
            )
            return
        c = ctx.message.channel
        if isinstance(c, DMChannel):
            # c: Member
            c = ctx.message.author
        db_rpg_player.set_busy(data.userid, n, c.id, BUSY_DESC_ADVENTURE)
        await self.bot.send_message(
            destination=ctx.channel,
            content="{}, you are now adventuring for {} minutes, good luck!".format(
                ctx.message.author.mention, n
            ),
        )

    # {prefix}rpg battle <user>
    @rpg.command(
        pass_context=1,
        aliases=["Battle", "b", "B"],
        help="Battle a fellow discord ally to a deadly fight!",
    )
    async def battle(self, ctx: Context, *args):
        if not await self.bot.pre_command(
            message=ctx.message, channel=ctx.channel, command="rpg battle"
        ):
            return
        attacker = db_rpg_player.get_player(
            ctx.message.author.id,
            ctx.message.author.display_name,
            ctx.message.author.avatar_url,
        )
        if not await self.check_role(attacker.role, ctx.message):
            return
        try:
            errors = {"no_mention": "You need to tag someone to battle with!"}
            defender = await self.bot.get_member_from_message(
                ctx=ctx, args=args, in_text=True, errors=errors
            )
        except ValueError:
            return

        if defender == ctx.message.author:
            await self.bot.send_message(
                destination=ctx.channel, content="Suicide is never the answer :angry:"
            )
            return

        defender = db_rpg_player.get_player(
            defender.id, defender.display_name, defender.avatar_url
        )
        await self.resolve_battle(
            "Mockbattle", ctx.message.channel, [attacker], [defender], winner_pic=True
        )

    # {prefix}rpg info [weapon|w|armor|a] <user>
    @rpg.command(
        pass_context=1,
        aliases=["Info", "I", "i", "stats", "Stats", "status", "Status"],
        help="Show the character's status information!",
    )
    async def info(self, ctx: Context, *args):
        if not await self.bot.pre_command(
            message=ctx.message, channel=ctx.channel, command="rpg info"
        ):
            return

        try:
            if len(args) > 0 and args[0] in ["w", "weapon", "a", "armor"]:
                a = args[1:]
            else:
                a = args
            user = await self.bot.get_member_from_message(ctx=ctx, args=a, in_text=True)
        except ValueError:
            user = ctx.message.author

        data = db_rpg_player.get_player(user.id, user.display_name, user.avatar_url)
        if not await self.check_role(data.role, ctx.message, error="That player"):
            return

        # Requested info is of weapon
        if len(args) > 0:
            if args[0] in ["w", "weapon"]:
                embed = discord.Embed(colour=RPG_EMBED_COLOR)
                embed.set_author(
                    name="{}'s weapon".format(data.name),
                    icon_url=ctx.message.author.avatar_url,
                )
                embed.add_field(
                    name="Weapon's name", value=data.weapon.name, inline=False
                )
                embed.add_field(
                    name="Original cost", value=data.weapon.cost, inline=False
                )
                embed.add_field(
                    name="Element",
                    value=rpgc.elementnames.get(data.weapon.element)[0],
                    inline=False,
                )
                if data.weapon.damage != 0:
                    embed.add_field(
                        name="Damage", value=data.weapon.damage, inline=False
                    )
                if data.weapon.weaponskill != 0:
                    embed.add_field(
                        name="Weaponskill", value=data.weapon.weaponskill, inline=False
                    )
                if data.weapon.critical != 0:
                    embed.add_field(
                        name="Critical", value=data.weapon.critical, inline=False
                    )
                await self.bot.send_message(ctx.message.channel, embed=embed)
                return

            # Requested info is of armor
            if args[0] in ["a", "armor"]:
                embed = discord.Embed(colour=RPG_EMBED_COLOR)
                embed.set_author(
                    name="{}'s armor".format(data.name),
                    icon_url=ctx.message.author.avatar_url,
                )
                embed.add_field(
                    name="Armor's name", value=data.armor.name, inline=False
                )
                embed.add_field(
                    name="Original cost", value=data.armor.cost, inline=False
                )
                embed.add_field(
                    name="Element",
                    value=rpgc.elementnames.get(data.armor.element)[0],
                    inline=False,
                )
                if data.armor.maxhealth != 0:
                    embed.add_field(
                        name="Maxhealth", value=data.armor.maxhealth, inline=False
                    )
                if data.armor.healthregen != 0:
                    embed.add_field(
                        name="Healthregeneration",
                        value=data.armor.healthregen,
                        inline=False,
                    )
                if data.armor.money != 0:
                    embed.add_field(
                        name="Extra money",
                        value="{}%".format(data.armor.money),
                        inline=False,
                    )
                await self.bot.send_message(ctx.message.channel, embed=embed)
                return

        # Requested info is of player
        # Load image and set basic params
        try:
            im = Image.open("images/rpg/{}.png".format(data.role.lower()))
        except:
            im = Image.open("images/rpg/undead.png")

        try:
            pp = Image.open(BytesIO(requests.get(data.picture_url).content))
            pp = pp.resize((60, 60))
            im.paste(pp, (235, 5))
        except OSError:
            pass

        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype(font_path, 12)
        color = (255, 255, 255)
        nameoffset = 18
        statoffset = nameoffset + 98
        topoffset = 18
        following = 23

        # Gather and add information to the picture
        name = data.name
        if len(name) < 12:
            name += " 's information"
        draw.text((nameoffset, topoffset), name + ":", color, font=font)
        draw.text((nameoffset, topoffset + following), str(data.role), color, font=font)
        if data.get_level() > data.level:
            stats = "Level up available!"
        else:
            stats = "lvl {} ({} xp)".format(data.level, shorten_number(data.exp))
        draw.text((statoffset, topoffset + following), stats, color, font=font)
        draw.text(
            (nameoffset, topoffset + 2 * following), "Boss Tier:", color, font=font
        )
        draw.text(
            (statoffset, topoffset + 2 * following),
            "{}".format(data.get_bosstier()),
            color,
            font=font,
        )
        if data.get_health() <= 0:
            stats = "Dead"
        elif data.busydescription == BUSY_DESC_ADVENTURE:
            stats = "Adventuring for {}m".format(data.busytime)
        elif data.busydescription == BUSY_DESC_TRAINING:
            stats = "Training for {}m".format(data.busytime)
        elif data.busydescription == BUSY_DESC_BOSSRAID:
            stats = "Waiting for the bossbattle"
        elif data.busydescription == BUSY_DESC_WANDERING:
            stats = "Wandering for {}m".format(data.busytime)
        elif data.busydescription == BUSY_DESC_WORKING:
            stats = "Working for {}m".format(data.busytime)
        else:
            stats = "Alive"
        draw.text((nameoffset, topoffset + 3 * following), "Status:", color, font=font)
        draw.text((statoffset, topoffset + 3 * following), stats, color, font=font)
        draw.text((nameoffset, topoffset + 4 * following), "Money:", color, font=font)
        draw.text(
            (statoffset, topoffset + 4 * following),
            "{}{}".format(rpggameactivities.money_sign, data.money),
            color,
            font=font,
        )
        draw.text((nameoffset, topoffset + 5 * following), "Health:", color, font=font)
        draw.text(
            (statoffset, topoffset + 5 * following),
            "{}/{}".format(data.get_health(), data.get_max_health()),
            color,
            font=font,
        )
        draw.text((nameoffset, topoffset + 6 * following), "Damage:", color, font=font)
        draw.text(
            (statoffset, topoffset + 6 * following),
            "{}".format(data.get_damage()),
            color,
            font=font,
        )
        draw.text(
            (nameoffset, topoffset + 7 * following), "Weaponskill:", color, font=font
        )
        draw.text(
            (statoffset, topoffset + 7 * following),
            "{}".format(data.get_weaponskill()),
            color,
            font=font,
        )
        draw.text(
            (nameoffset, topoffset + 8 * following), "Critical:", color, font=font
        )
        draw.text(
            (statoffset, topoffset + 8 * following),
            "{}".format(data.get_critical()),
            color,
            font=font,
        )
        draw.text(
            (nameoffset, topoffset + 9 * following), "Time extention:", color, font=font
        )
        draw.text(
            (statoffset, topoffset + 9 * following),
            "{}".format(data.extratime),
            color,
            font=font,
        )
        draw.text((nameoffset, topoffset + 10 * following), "Pets:", color, font=font)
        draw.text(
            (statoffset, topoffset + 10 * following),
            "{}".format(len(data.pets)),
            color,
            font=font,
        )

        imname = "temp/{}.png".format(ctx.message.author.id)
        im.save(imname)
        with open(imname, "rb") as file:
            f = File(file, filename=imname, spoiler=False)
            await self.bot.send_message(destination=ctx.message.channel, file=f)
            f.close()
        os.remove(imname)

    # {prefix}rpg join
    @rpg.command(
        pass_context=1, aliases=["Join", "J", "j"], help="Join a raid to kill a boss!"
    )
    async def join(self, ctx: Context):
        if not await self.bot.pre_command(
            message=ctx.message,
            channel=ctx.channel,
            command="rpg join",
            cannot_be_private=True,
        ):
            return

        data = db_rpg_player.get_player(
            ctx.message.author.id,
            ctx.message.author.display_name,
            ctx.message.author.avatar_url,
        )
        if not await self.check_role(data.role, ctx.message):
            return

        party = db_rpg.get_boss_parties().get(ctx.message.guild.id, [])
        if data in party:
            await self.bot.send_message(
                destination=ctx.channel,
                content="{}, you are already in the boss raid party...".format(
                    ctx.message.author.mention
                ),
            )
            return
        if data.busydescription != BUSY_DESC_NONE:
            await self.bot.send_message(
                destination=ctx.channel,
                content="{}, finish your current task first, then you can join the boss raid party!".format(
                    ctx.message.author.mention
                ),
            )
            return
        if len(party) <= 0 and not db_rpg_channels.get_rpg_channel(
            ctx.message.guild.id
        ):
            await self.bot.send_message(
                destination=ctx.channel,
                content='Be sure to set the channel for bossfights with "{}rpg setchannel, '
                "or you will not be able to see the results!".format(
                    await self.bot.get_prefix(ctx.message)
                ),
            )

        db_rpg_player.set_busy(
            data.userid, 61, ctx.message.guild.id, BUSY_DESC_BOSSRAID
        )
        c = "{}, prepare yourself! You and your party of {} will be fighting the boss at the hour mark!".format(
            ctx.message.author.mention, len(party) + 1
        )
        await self.bot.send_message(destination=ctx.channel, content=c)

    # {prefix}rpg king
    @rpg.command(
        pass_context=1, aliases=["King", "k", "K"], help="The great king's game!"
    )
    async def king(self, ctx: Context, *args):
        kingname = "Neko Overlord Ruling with an Iron Paw"
        if not await self.bot.pre_command(
            message=ctx.message,
            channel=ctx.channel,
            command="rpg king",
            cannot_be_private=True,
        ):
            return
        king = int(db_rpg.get_king(ctx.message.guild.id))
        if len(args) <= 0:
            if king is None:
                await self.bot.send_message(
                    destination=ctx.channel,
                    content="There is currently no {} in {}".format(
                        kingname, ctx.message.guild.name
                    ),
                )
                return
            await self.bot.send_message(
                destination=ctx.channel,
                content="The current {} of {} is {}".format(
                    kingname,
                    ctx.message.guild.name,
                    ctx.message.guild.get_member(king).display_name,
                ),
            )
            return
        data = db_rpg_player.get_player(
            ctx.message.author.id,
            ctx.message.author.display_name,
            ctx.message.author.avatar_url,
        )
        if data.busydescription != BUSY_DESC_NONE:
            await self.bot.send_message(
                destination=ctx.channel,
                content="Please finish what you are doing before a fight",
            )
            return
        now = datetime.datetime.now()
        if data.kingtimer != 0:
            if (now - datetime.datetime.fromtimestamp(data.kingtimer)).seconds < 3600:
                c = "You are still tired from your last battle, rest for an hour or so and you can try again"
                await self.bot.send_message(destination=ctx.channel, content=c)
                return
        if db_rpg.is_king(data.userid):
            await self.bot.send_message(
                destination=ctx.channel,
                content="You are already a {} somewhere".format(kingname),
            )
            return
        if not (args[0] in ["c", "b", "challenge", "battle"]):
            return
        if data.get_level() < 10:
            await self.bot.send_message(
                destination=ctx.channel,
                content="You need to be at least level 10 to challenge the current {}".format(
                    kingname
                ),
            )
            return
        if king is None:
            db_rpg.set_king(data.userid, ctx.guild.id)
            c = "You are now the {0} of {1}!\nLong live the {0}!".format(
                kingname, ctx.guild.name
            )
            await self.bot.send_message(destination=ctx.channel, content=c)
            return

        king = ctx.message.guild.get_member(king)
        king = db_rpg_player.get_player(king.id, king.display_name, king.avatar_url)

        battle_result = await self.resolve_battle(
            "Kingsbattle", ctx.message.channel, [data], [king]
        )
        for p in [data, king]:
            db_rpg_player.update_player(p)
        if battle_result == 1:
            winner = data
            db_rpg.set_king(data.userid, ctx.message.guild.id)
            c = "{0} beat down {1}\n{0} is now the {2} of {3}!".format(
                data.name, king.name, kingname, ctx.guild.name
            )
            await self.bot.send_message(destination=ctx.channel, content=c)
        else:
            winner = king
            c = "{0} beat down {1}\n{0} remains the true {2} of {3}!".format(
                king.name, data.name, kingname, ctx.guild.name
            )
            await self.bot.send_message(destination=ctx.channel, content=c)
        now = now.timestamp()
        db_rpg_player.set_kingtimer(data.userid, now)
        db_rpg_player.set_kingtimer(king.userid, now)
        db_rpg_player.set_health(winner.userid, winner.get_max_health())
        db_rpg_player.add_stats(winner.userid, "level", -1)

    async def add_levelup(self, data, channel, reward):
        if reward == 1:
            db_rpg_player.add_stats(data.userid, "stats.maxhealth", 80)
            await self.bot.send_message(
                channel,
                "Your base maximum health is now {}".format(data.maxhealth + 80),
            )
        elif reward == 2:
            db_rpg_player.add_stats(data.userid, "extratime", 1)
            await self.bot.send_message(
                channel,
                "You can now do things {} minutes longer".format(data.extratime + 1),
            )
        elif reward == 3:
            db_rpg_player.add_stats(data.userid, "stats.damage", 30)
            await self.bot.send_message(
                channel, "Your base damage is now {}".format(data.damage + 30)
            )
        else:
            await self.bot.send_message(channel, "Dunno what you mean tbh")
            return False
        return True

    # {prefix}rpg levelup
    @rpg.command(
        pass_context=1,
        aliases=["Levelup", "lvlup", "Lvlup", "lvl", "Lvl"],
        help="Choose the reward for leveling up!",
    )
    async def levelup(self, ctx: Context, *args):
        if not await self.bot.pre_command(
            message=ctx.message, channel=ctx.channel, command="rpg levelup"
        ):
            return

        data = db_rpg_player.get_player(
            ctx.message.author.id,
            ctx.message.author.name,
            ctx.message.author.avatar_url,
        )
        if not await self.check_role(data.role, ctx.message):
            return

        if data.get_level() <= data.level:
            await self.bot.send_message(
                destination=ctx.channel, content="You have no level-ups available"
            )
            return

        if len(args) <= 0:
            while data.get_level() > data.level:
                c = "Available rewards are:\n1)\t+80 hp\n2)\t+1 minute busytime\n3)\t+30 damage"
                m = await self.bot.send_message(destination=ctx.channel, content=c)

                def check(r: Message):
                    return (
                        m.channel is r.channel and r.author.id is ctx.message.author.id
                    )

                r = await self.bot.wait_for("message", check=check, timeout=60)
                await self.bot.delete_message(m)
                if not r:
                    return
                try:
                    num = int(r.content)
                    if await self.add_levelup(data, ctx.channel, num):
                        db_rpg_player.add_stats(data.userid, "level", 1)
                        data.level += 1
                    await self.bot.delete_message(r)
                except ValueError:
                    return
            return
        try:
            if await self.add_levelup(data, ctx.channel, int(args[0])):
                db_rpg_player.add_stats(data.userid, "level", 1)
        except ValueError:
            await self.bot.send_message(
                destination=ctx.channel, content="Thats not even a number..."
            )

    # {prefix}rpg party
    @rpg.command(
        pass_context=1,
        aliases=["Party", "p", "P"],
        help="All players gathered to kill the boss",
    )
    async def party(self, ctx: Context):
        if not await self.bot.pre_command(
            message=ctx.message,
            channel=ctx.channel,
            command="rpg party",
            cannot_be_private=True,
        ):
            return
        party = db_rpg.get_boss_parties().get(ctx.message.guild.id, [])
        if len(party) <= 0:
            c = "There is no planned boss raid, but you are welcome to start a party!"
            await self.bot.send_message(destination=ctx.channel, content=c)
            return
        embed = discord.Embed(colour=RPG_EMBED_COLOR)
        embed.add_field(
            name="Boss raiding party",
            value="{} adventurers".format(len(party)),
            inline=False,
        )
        embed.add_field(
            name="Estimated boss level",
            value=max([x.get_bosstier() for x in party]),
            inline=False,
        )
        m = ""
        for n in party:
            member = ctx.guild.get_member(int(n.userid))
            m += "{}, level {}\n".format(member.display_name, n.get_level())
        embed.add_field(name="Adventurers", value=m, inline=False)
        await self.bot.send_message(destination=ctx.channel, embed=embed)

    # {prefix}rpg role
    @rpg.command(
        pass_context=1,
        aliases=["Role", "r", "R", "class", "Class", "c", "C"],
        help="Switch your role on the battlefield",
    )
    async def role(self, ctx: Context, *args):
        if not await self.bot.pre_command(
            message=ctx.message, channel=ctx.channel, command="rpg role"
        ):
            return
        data = db_rpg_player.get_player(
            ctx.message.author.id,
            ctx.message.author.display_name,
            ctx.message.author.avatar_url,
        )
        if len(args) <= 0:
            embed = discord.Embed(colour=RPG_EMBED_COLOR)
            embed.set_author(
                name="You can be anything you want, as long as it is one of these:",
                icon_url=data.picture_url,
            )
            for name, desc in rpgc.names.get("role"):
                embed.add_field(name=name, value=desc, inline=False)
            embed.set_footer(text="Be aware! You choose you occupation for life!")
            await self.bot.send_message(destination=ctx.channel, embed=embed)
            return
        if (
            data.role in [x[0] for x in rpgc.names.get("role")[:-1]]
            and ctx.message.author.id != constants.NYAid
        ):
            await self.bot.send_message(
                destination=ctx.channel,
                content="You cannot change your role once chosen",
            )
            return
        role = " ".join(args).lower()
        role = role[0].upper() + role[1:]

        if role == data.role:
            c = "{}, that is already your current role...".format(
                ctx.message.author.mention
            )
            await self.bot.send_message(destination=ctx.channel, content=c)
            return
        if role not in [x[0] for x in rpgc.names.get("role")]:
            c = "{}, that is not a role available to a mere mortal".format(
                ctx.message.author.mention
            )
            await self.bot.send_message(destination=ctx.channel, content=c)
            return
        if data.role == rpgc.names.get("role")[-1][0]:
            data.health = 100
        data.role = role
        db_rpg_player.update_player(data)
        c = "{}, you now have the role of {}".format(ctx.message.author.mention, role)
        await self.bot.send_message(destination=ctx.channel, content=c)

    @staticmethod
    def get_group(s: str):
        if s in ["m", "money"]:
            return "money"
        if s in ["b", "bt", "bosstier"]:
            return "bosstier"
        if s in ["c", "critical"]:
            return "critical"
        if s in ["ws", "weaponskill"]:
            return "weaponskill"
        if s in ["d", "dam", "damage"]:
            return "damage"
        if s in ["hp", "health", "mh", "mhp", "maxhealth"]:
            return "maxhealth"
        return "exp"

    @staticmethod
    def top_board(page=0, group="exp"):
        users_per_page = 10
        embed = discord.Embed(colour=RPG_EMBED_COLOR)
        embed.add_field(
            name="RPG top players", value="Page " + str(page + 1), inline=False
        )
        players = db_rpg.get_top_players(group, page * users_per_page, users_per_page)
        result = ""

        for i in range(len(players)):
            name, player_score = players[i]
            player_score_text = shorten_number(player_score)
            rank = page * users_per_page + i + 1
            if group == "money":
                result += "Rank {}:\n\t**{}**, {}{}\n".format(
                    rank, name, rpggameactivities.money_sign, player_score_text
                )
            elif group == "bosstier":
                result += "Rank {}:\n\t**{}**, tier {}\n".format(
                    rank, name, player_score_text
                )
            elif group in ["critical", "weaponskill", "damage", "maxhealth"]:
                result += "Rank {}:\n\t**{}**, {}\n".format(
                    rank, name, player_score_text
                )
            else:
                result += "Rank {}:\n\t**{}**, {}xp (L{})\n".format(
                    rank,
                    name,
                    player_score_text,
                    RPGPlayer.get_level_by_exp(player_score),
                )
        if result == "":
            return None
        embed.add_field(name="Ranks and names", value=result)
        return embed

    async def handle_reaction(self, reaction: Reaction):
        if reaction.message.id in [x[0] for x in self.top_lists.values()]:
            _, page, group = self.top_lists.get(reaction.message.guild.id)
            if reaction.emoji == "\N{LEFTWARDS BLACK ARROW}":
                page = page - 1
            if reaction.emoji == "\N{BLACK RIGHTWARDS ARROW}":
                page = page + 1
            async for m in reaction.users():
                if m.id != self.bot.user.id:
                    await reaction.remove(m)
            try:
                embed = self.top_board(page, group)
                if not embed:
                    return
                await self.bot.edit_message(reaction.message, embed=embed)
                self.top_lists[reaction.message.guild.id] = (
                    reaction.message.id,
                    page,
                    group,
                )
            except ValueError:
                pass

    # {prefix}rpg top <exp|money|bosstier> <amount>
    @rpg.command(
        pass_context=1,
        aliases=["Top", "T", "t"],
        help="Show the people with the most experience!",
    )
    async def top(self, ctx: Context, *args):
        if not await self.bot.pre_command(
            message=ctx.message, channel=ctx.message.channel, command="rpg top"
        ):
            return
        if len(args) > 0:
            if len(args) > 1:
                try:
                    n = int(args[1]) - 1
                except ValueError:
                    n = 0
                group = RPGGame.get_group(args[0])
            else:
                try:
                    n = int(args[0]) - 1
                    group = "exp"
                except ValueError:
                    n = 0
                    group = RPGGame.get_group(args[0])
        else:
            n = 0
            group = "exp"

        embed = self.top_board(page=n, group=group)
        if not embed:
            await self.bot.send_message(
                destination=ctx.channel,
                content="There aren't that many pages...",
            )
            return
        m = await self.bot.send_message(ctx.message.channel, embed=embed)
        await m.add_reaction("\N{LEFTWARDS BLACK ARROW}")
        await m.add_reaction("\N{BLACK RIGHTWARDS ARROW}")
        await m.add_reaction("\N{BROKEN HEART}")
        self.top_lists[ctx.guild.id] = (m.id, n, group)

    # {prefix}rpg wander #
    @rpg.command(
        pass_context=1,
        aliases=["Wander", "w", "W"],
        help="Wander in the beautiful country",
    )
    async def wander(self, ctx: Context, *args):
        if not await self.bot.pre_command(
            message=ctx.message, channel=ctx.message.channel, command="rpg wander"
        ):
            return
        data = db_rpg_player.get_player(
            ctx.message.author.id,
            ctx.message.author.display_name,
            ctx.message.author.avatar_url,
        )
        if not await self.check_role(data.role, ctx.message):
            return
        if len(args) > 0:
            try:
                n = int(args[0])
            except ValueError:
                n = 60
        else:
            n = 60

        if data.busydescription != BUSY_DESC_NONE:
            await self.bot.send_message(
                destination=ctx.channel, content="You are already doing other things"
            )
            return
        if not (minwandertime <= n <= (maxwandertime + (2 * data.extratime))):
            c = "You can wander between {} and {} minutes".format(
                minwandertime, maxwandertime + (2 * data.extratime)
            )
            await self.bot.send_message(destination=ctx.channel, content=c)
            return
        c = ctx.message.channel
        db_rpg_player.set_busy(
            user_id=data.userid,
            time=n,
            channel_id=c.id,
            description=BUSY_DESC_WANDERING,
        )
        c = "{}, you are now wandering for {} minutes, good luck!".format(
            ctx.message.author.mention, n
        )
        await self.bot.send_message(destination=ctx.channel, content=c)

    # DB commands
    @rpg.command(pass_context=1, help="Set rpg channel!")
    async def setchannel(self, ctx: Context):
        if not await self.bot.pre_command(
            message=ctx.message,
            channel=ctx.message.channel,
            command="rpg setchannel",
            perm_needed=["manage_server", "administrator"],
        ):
            return
        db_rpg_channels.set_rpg_channel(ctx.message.guild.id, ctx.message.channel.id)
        c = "This channel is now the rpg channel for this server"
        await self.bot.send_message(destination=ctx.channel, content=c)

    # money for devs (testing purpose ONLY)
    @rpg.command(pass_context=1, hidden=True, help="Dev money")
    async def cashme(self, ctx: Context):
        if not await self.bot.pre_command(
            message=ctx.message,
            channel=ctx.message.channel,
            command="rpg cashme",
            is_typing=False,
            owner_check=True,
        ):
            return
        db_rpg_player.set_stat(ctx.message.author.id, "money", 99999999)

    @rpg.command(pass_context=1, hidden=True, help="Dev exp")
    async def xpme(self, ctx: Context):
        if not await self.bot.pre_command(
            message=ctx.message,
            channel=ctx.message.channel,
            command="rpg xpme",
            is_typing=False,
            owner_check=True,
        ):
            return
        db_rpg_player.set_stat(ctx.message.author.id, "exp", 99999999)

    @rpg.command(pass_context=1, hidden=True, aliases=["tbf"])
    async def triggerbossfights(self, ctx: Context):
        if not await self.bot.pre_command(
            message=ctx.message,
            channel=ctx.channel,
            command="rpg triggerbossfights",
            is_typing=False,
            owner_check=True,
        ):
            return
        await self.bot.rpg_game.boss_battle()

    @rpg.command(pass_context=1, hidden=True)
    async def addpet(self, ctx: Context, num: int):
        if not await self.bot.pre_command(
            message=ctx.message,
            channel=ctx.channel,
            command="rpg addpet",
            owner_check=True,
        ):
            return
        data = db_rpg_player.get_player(
            ctx.message.author.id,
            ctx.message.author.display_name,
            ctx.message.author.avatar_url,
        )
        for _ in range(num):
            data.add_pet(RPGPet())
        db_rpg_player.update_player(data)
        await self.bot.send_message(
            destination=ctx.channel, content="{} cats added".format(num)
        )

    @rpg.command(pass_context=1, hidden=True)
    async def clearpets(self, ctx: Context):
        if not await self.bot.pre_command(
            message=ctx.message,
            channel=ctx.channel,
            command="rpg clearpets",
            owner_check=True,
        ):
            return
        db_rpg_player.set_stat(ctx.message.author.id, "pets", [])
        await self.bot.send_message(
            destination=ctx.channel, content="Slaughtering pets complete"
        )

    @rpg.command(pass_context=1, aliases=["Pets", "Pet", "pet"])
    async def pets(self, ctx: Context, *args):
        if not await self.bot.pre_command(
            message=ctx.message, channel=ctx.channel, command="rpg pets"
        ):
            return

        # Get specified player
        if len(ctx.message.mentions) > 0:
            u = ctx.message.mentions[0]
        else:
            u = ctx.message.author
        data = db_rpg_player.get_player(u.id, u.display_name, u.avatar_url)

        # Release pets subcommand
        if len(args) > 0 and args[0] in ["remove", "release", "r"]:
            if len(data.pets) <= 0:
                await self.bot.send_message(
                    destination=ctx.channel, content="You have no pets to remove..."
                )
                return
            if len(args) <= 1 < len(data.pets):
                await self.bot.send_message(
                    destination=ctx.channel, content="Please say which pet to remove"
                )
                return
            try:
                num_to_remove = int(args[1]) - 1
            except ValueError:
                await self.bot.send_message(
                    destination=ctx.channel, content="Thats not a number..."
                )
                return
            if num_to_remove >= len(data.pets):
                await self.bot.send_message(
                    destination=ctx.channel, content="You do not have that many pets..."
                )
                return
            # pet: RPGPet
            pet = data.pets[num_to_remove]
            data.pets.remove(pet)
            db_rpg_player.update_player(data)
            c = "Your pet named {} was released into the wild".format(pet.name)
            await self.bot.send_message(destination=ctx.channel, content=c)
            return

        # List pets subcommand
        if len(data.pets) <= 0:
            c = "You do not have any cuties at the moment, try defeating a boss and maybe it will leave you a reward!"
            await self.bot.send_message(destination=ctx.channel, content=c)
            return
        embed = discord.Embed(colour=RPG_EMBED_COLOR)
        embed.set_author(name="{}'s pets:".format(u.display_name), url=u.avatar_url)
        for i in range(len(data.pets)):
            pet = data.pets[i]
            stats = "Number: {}\nExp: {} (L{})\nDamage: {}\nWeaponskill: {}".format(
                i + 1,
                shorten_number(pet.exp),
                pet.get_level(),
                pet.get_damage(),
                pet.get_weaponskill(),
            )
            embed.add_field(name=pet.name, value=stats)
        await self.bot.send_message(destination=ctx.channel, embed=embed)

    @rpg.command(pass_context=1, hidden=True, aliases=["resetbusy"])
    async def clearbusy(self, ctx: Context, *args):
        if not await self.bot.pre_command(
            message=ctx.message,
            channel=ctx.channel,
            command="rpg clearbusy",
            owner_check=True,
        ):
            return
        try:
            user = await self.bot.get_member_from_message(
                ctx=ctx, args=args, in_text=True
            )
        except ValueError:
            user = ctx.message.author

        db_rpg_player.reset_busy(user.id)
        await self.bot.send_message(
            ctx.channel, 'Busy status of player"{}" reset'.format(user.display_name)
        )

    def quit(self):
        pass


def setup(bot):
    bot.add_cog(RPGGame(bot))
