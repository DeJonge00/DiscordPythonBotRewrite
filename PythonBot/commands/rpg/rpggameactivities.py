import math
import random

import discord
from discord.ext import commands
from discord.ext.commands import Cog
from discord.ext.commands.context import Context

from api.rpg import constants as rpgc
from api.rpg.objects import rpgplayer as rpgp, rpgweapon as rpgw, rpgarmor as rpga
from core.bot import PythonBot
from database.rpg import player as db_rpg_player

money_sign = "¥"
SHOP_EMBED_COLOR = 0x00969B


class RPGGameActivities(Cog):
    def __init__(self, bot: PythonBot):
        self.bot = bot
        self.bot.rpg_shop = self
        self.weapons = {}
        self.armors = {}

    async def send_shop_help_message(self, url: str, message: discord.Message):
        prefix = await self.bot.get_prefix(message)
        embed = discord.Embed(colour=SHOP_EMBED_COLOR)
        embed.set_author(name="Shop commands", icon_url=url)
        embed.add_field(
            name="Items",
            value="Type '{}shop item' for a list of available items".format(prefix),
            inline=False,
        )
        embed.add_field(
            name="Weapons",
            value="Type '{}shop weapon' for a list of available weapons".format(prefix),
            inline=False,
        )
        embed.add_field(
            name="Armor",
            value="Type '{}shop armor' for the armor sold in this shop".format(prefix),
            inline=False,
        )
        embed.add_field(
            name="Restock",
            value="Weapons and armors refresh every hour".format(prefix),
            inline=False,
        )
        await self.bot.send_message(message.channel, embed=embed)

    # {prefix}shop
    @commands.group(pass_context=1, help="Shop for valuable items!")
    async def shop(self, ctx: Context):
        prefix = await self.bot.get_prefix(ctx.message)
        if ctx.invoked_subcommand is None and (
            ctx.message.content
            in ["{}shop help".format(prefix), "{}shop".format(prefix)]
        ):
            if not await self.bot.pre_command(
                message=ctx.message, channel=ctx.channel, command="shop help"
            ):
                return
            await self.send_shop_help_message(
                ctx.message.author.avatar_url, ctx.message
            )

    # {prefix}shop armor
    @shop.command(
        pass_context=1, aliases=["a", "armour"], help="Buy a shiny new suit of armor!"
    )
    async def armor(self, ctx: Context, *args):
        if not await self.bot.pre_command(
            message=ctx.message, channel=ctx.channel, command="shop armor"
        ):
            return
        player = db_rpg_player.get_player(
            ctx.message.author.id,
            ctx.message.author.display_name,
            ctx.message.author.avatar_url,
        )
        if not await self.bot.rpg_game.check_role(player.role, ctx.message):
            return
        if player.role == rpgc.names.get("role")[-1][0]:
            c = "{}, A cat cannot possibly wear human armor...".format(
                ctx.message.author.mention
            )
            await self.bot.send_message(destination=ctx.channel, content=c)
            return
        if len(args) <= 0:
            embed = discord.Embed(colour=SHOP_EMBED_COLOR)
            embed.set_author(name="Shop Armory", icon_url=ctx.message.author.avatar_url)
            embed.add_field(
                name="Your money", value="{}{}".format(money_sign, player.money)
            )
            start = max(0, player.get_level() - 5)
            for i in range(start, start + 10):
                a = self.armors.get(i)
                if a is None:
                    a = rpga.generateArmor(i * 1000)
                    self.armors[i] = a
                t = "Costs: {}".format(a.cost)
                if a.maxhealth != 0:
                    t += ", maxhealth: {}".format(a.maxhealth)
                if a.healthregen != 0:
                    t += ", healthregen: {}".format(a.healthregen)
                if a.money != 0:
                    t += ", money: {}%".format(a.money)
                embed.add_field(name=str(i) + ") " + a.name, value=t, inline=False)
            await self.bot.send_message(destination=ctx.channel, embed=embed)
            return
        try:
            armor = self.armors.get(int(args[0]))
        except ValueError:
            c = "That is not an armor sold in this part of the country"
            await self.bot.send_message(destination=ctx.channel, content=c)
            return
        if armor is None:
            c = "That is not an armor sold in this part of the country"
            await self.bot.send_message(destination=ctx.channel, content=c)
            return
        pa = player.armor
        if not player.buy_armor(armor):
            c = "You do not have the money to buy the {}".format(armor.name)
            await self.bot.send_message(destination=ctx.channel, content=c)
            return
        t = "You have acquired the {} for {}{}".format(
            armor.name, money_sign, armor.cost
        )
        if pa.cost > 3:
            t += "\nYou sold your old armor for {}{}".format(
                money_sign, int(math.floor(0.25 * pa.cost))
            )
        db_rpg_player.update_player(player)
        await self.bot.send_message(destination=ctx.channel, content=t)

    # {prefix}shop item
    @shop.command(
        pass_context=1,
        aliases=["i", "buy", "items"],
        help="Special knowledge on enemy weakpoints",
    )
    async def item(self, ctx: Context, *args):
        if not await self.bot.pre_command(
            message=ctx.message, channel=ctx.channel, command="shop item"
        ):
            return
        player = db_rpg_player.get_player(
            ctx.message.author.id,
            ctx.message.author.display_name,
            ctx.message.author.avatar_url,
        )
        if not await self.bot.rpg_game.check_role(player.role, ctx.message):
            return
        if len(args) <= 0:
            embed = discord.Embed(colour=SHOP_EMBED_COLOR)
            embed.set_author(
                name="Shop inventory", icon_url=ctx.message.author.avatar_url
            )
            embed.add_field(
                name="Your money", value="{}{}".format(money_sign, player.money)
            )
            for i in sorted(rpgc.shopitems.values(), key=lambda l: l.cost):
                t = "Costs: {}{}".format(money_sign, i.cost)
                t += "\nYou can afford {} of this item".format(
                    math.floor(player.money / i.cost)
                )
                for e in i.benefit:
                    x = i.benefit.get(e)
                    t += "\n{}{}{}".format(e, x[0], x[1])
                embed.add_field(name=i.name, value=t, inline=False)
            await self.bot.send_message(destination=ctx.channel, embed=embed)
            return
        item = args[0].lower()
        if item in ["h", "hp"]:
            item = "health"
        if item in ["mh", "mhp"]:
            item = "maxhealth"
        elif item in ["d", "dam", "dmg"]:
            item = "damage"
        elif item in ["c", "crit"]:
            item = "critical"
        if (
            item in ["maxhealth", "health"]
            and player.role == rpgc.names.get("role")[-1][0]
        ):
            c = "{}, this stuff does not work on animals...".format(
                ctx.message.author.mention
            )
            await self.bot.send_message(destination=ctx.channel, content=c)
            return
        if item == "health" and player.health == player.maxhealth:
            await self.bot.send_message(
                destination=ctx.channel, content="You're already full HP"
            )
            return
        item = rpgc.shopitems.get(item)
        if not item:
            await self.bot.send_message(
                destination=ctx.channel, content="That's not an item sold here"
            )
            return
        try:
            a = int(args[1])
        except ValueError:
            if args[1] in ["m", "max"]:
                a = math.floor(player.money / item.cost)
                m = int((player.maxhealth - player.health) / 25)
                if args[0] in ["h", "hp", "health"] and (
                    player.money >= (m * item.cost)
                ):
                    a = m
            else:
                a = 1
        except IndexError:
            a = 1
        if a < 0:
            await self.bot.send_message(
                destination=ctx.channel, content="Lmao, that sounds intelligent"
            )
            return
        if player.buy_item(item, amount=a):
            c = "{} bought {} {} for {}{}".format(
                ctx.message.author.mention, a, item.name, money_sign, a * item.cost
            )
            await self.bot.send_message(destination=ctx.channel, content=c)
            db_rpg_player.update_player(player)
        else:
            c = "{} does not have enough money to buy {} {}\nThe maximum you can afford is {}".format(
                ctx.message.author.mention,
                a,
                item.name,
                math.floor(player.money / item.cost),
            )
            await self.bot.send_message(destination=ctx.channel, content=c)

    # {prefix}shop weapon
    @shop.command(
        pass_context=1, aliases=["w", "weapons"], help="Buy a shiny new weapon!"
    )
    async def weapon(self, ctx: Context, *args):
        if not await self.bot.pre_command(
            message=ctx.message, channel=ctx.channel, command="shop weapon"
        ):
            return
        player = db_rpg_player.get_player(
            ctx.message.author.id,
            ctx.message.author.display_name,
            ctx.message.author.avatar_url,
        )
        if not await self.bot.rpg_game.check_role(player.role, ctx.message):
            return
        if player.role == rpgc.names.get("role")[-1][0]:
            c = "{}, how would you even use a weapon as a cat?".format(
                ctx.message.author.mention
            )
            await self.bot.send_message(destination=ctx.channel, content=c)
            return
        if len(args) <= 0:
            embed = discord.Embed(colour=SHOP_EMBED_COLOR)
            embed.set_author(
                name="Shop Weapons", icon_url=ctx.message.author.avatar_url
            )
            embed.add_field(
                name="Your money", value="{}{}".format(money_sign, player.money)
            )
            start = max(0, player.get_level() - 5)
            for i in range(start, start + 10):
                w = self.weapons.get(i)
                if w is None:
                    w = rpgw.generate_weapon(i * 1000)
                    self.weapons[i] = w
                t = "Costs: {}".format(w.cost)
                if w.damage != 0:
                    t += ", damage + {}".format(w.damage)
                if w.weaponskill != 0:
                    t += ", weaponskill + {}".format(w.weaponskill)
                if w.critical != 0:
                    t += ", critical + {}".format(w.critical)
                embed.add_field(name=str(i) + ") " + w.name, value=t, inline=False)
            await self.bot.send_message(destination=ctx.channel, embed=embed)
            return
        try:
            weapon = self.weapons.get(int(args[0]))
        except ValueError:
            c = "That is not a weapon sold in this part of the country"
            await self.bot.send_message(destination=ctx.channel, content=c)
            return
        if weapon is None:
            c = "That is not an weapon sold in this part of the country"
            await self.bot.send_message(destination=ctx.channel, content=c)
            return
        pw = player.weapon
        if not player.buy_weapon(weapon):
            c = "You do not have the money to buy the {}".format(weapon.name)
            await self.bot.send_message(destination=ctx.channel, content=c)
            return
        t = "You have acquired the {} for {}{}".format(
            weapon.name, money_sign, weapon.cost
        )
        if pw.cost > 3:
            t += "\nYou sold your old weapon for {}{}".format(
                money_sign, int(math.floor(0.25 * pw.cost))
            )
        db_rpg_player.update_player(player)
        await self.bot.send_message(destination=ctx.channel, content=t)

    # {prefix}train
    @commands.command(pass_context=1, aliases=["training"], help="Train your skills!")
    async def train(self, ctx: Context, *args):
        if not await self.bot.pre_command(
            message=ctx.message, channel=ctx.channel, command="train"
        ):
            return
        if len(args) <= 0:
            embed = discord.Embed(colour=SHOP_EMBED_COLOR)
            embed.set_author(
                name="Available Training", icon_url=ctx.message.author.avatar_url
            )
            for i in rpgc.trainingitems.values():
                embed.add_field(
                    name=i.name,
                    value="Minutes per statpoint: {}".format(i.cost),
                    inline=False,
                )
            await self.bot.send_message(destination=ctx.channel, embed=embed)
            return
        training = args[0]
        if training in ["ws", "weapon"]:
            training = "weaponskill"
        elif training in ["hp", "h", "health"]:
            training = "maxhealth"
        training = rpgc.trainingitems.get(training)
        if not training:
            await self.bot.send_message(
                destination=ctx.channel, content="Thats not an available training"
            )
            return
        try:
            a = int(args[1])
        except (ValueError, IndexError):
            a = math.ceil(rpgp.mintrainingtime / training.cost)

        player = db_rpg_player.get_player(
            ctx.message.author.id,
            ctx.message.author.display_name,
            ctx.message.author.avatar_url,
        )
        if not await self.bot.rpg_game.check_role(player.role, ctx.message):
            return
        if (
            player.role == rpgc.names.get("role")[-1][0]
            and training.name == "maxhealth"
        ):
            c = "{}, awww. So cute. A cat trying to fight a dummy".format(
                ctx.message.author.mention
            )
            await self.bot.send_message(destination=ctx.channel, content=c)
            return
        if player.busydescription != rpgp.BUSY_DESC_NONE:
            c = "Please make sure you finish your other shit first"
            await self.bot.send_message(destination=ctx.channel, content=c)
            return
        c = ctx.message.channel

        time = math.ceil(a * training.cost)
        if not (
            rpgp.mintrainingtime
            <= time
            <= int(rpgp.maxtrainingtime + (0.5 * player.extratime))
        ):
            m = "You can train between {} and {} points".format(
                math.ceil(rpgp.mintrainingtime / training.cost),
                math.floor(
                    int(rpgp.maxtrainingtime + (0.5 * player.extratime)) / training.cost
                ),
            )
            await self.bot.send_message(destination=ctx.channel, content=m)
            return
        player.set_busy(rpgp.BUSY_DESC_TRAINING, time, c.id)
        player.buy_training(training, amount=a)
        db_rpg_player.update_player(player)
        m = "{}, you are now training your {} for {} minutes".format(
            ctx.message.author.mention, training.name, int(math.ceil(a * training.cost))
        )
        await self.bot.send_message(destination=ctx.channel, content=m)

    # {prefix}work
    @commands.command(
        pass_context=1, aliases=["Work"], help="Work for some spending money!"
    )
    async def work(self, ctx: Context, *args):
        if not await self.bot.pre_command(
            message=ctx.message, channel=ctx.channel, command="work"
        ):
            return
        try:
            time = int(args[0])
        except (ValueError, IndexError):
            time = rpgp.mintrainingtime

        player = db_rpg_player.get_player(
            ctx.message.author.id,
            ctx.message.author.display_name,
            ctx.message.author.avatar_url,
        )
        if not await self.bot.rpg_game.check_role(player.role, ctx.message):
            return
        if player.role == rpgc.names.get("role")[-1][0]:
            m = "{}, I'm sorry, but we need someone with more... height...".format(
                ctx.message.author.mention
            )
            await self.bot.send_message(destination=ctx.channel, content=m)
            return
        if player.busydescription != rpgp.BUSY_DESC_NONE:
            c = "Please make sure you finish your other shit first"
            await self.bot.send_message(destination=ctx.channel, content=c)
            return

        # Set busy time
        if not (
            rpgp.minworkingtime <= time <= (rpgp.maxworkingtime + player.extratime)
        ):
            c = "You can work between {} and {} minutes".format(
                rpgp.minworkingtime, (rpgp.maxworkingtime + player.extratime)
            )
            await self.bot.send_message(destination=ctx.channel, content=c)
            return

        db_rpg_player.set_busy(
            player.userid, math.ceil(time), ctx.channel.id, rpgp.BUSY_DESC_WORKING
        )
        money = time * pow((player.get_level()) + 1, 1 / 2) * 120
        if player.role == rpgc.names.get("role")[0][0]:  # role == Peasant
            money *= 1.15
        db_rpg_player.add_stats(player.userid, "money", int(money))
        work = random.choice(
            [
                "cleaning the stables",
                "sharpening the noble's weapon",
                "assisting the smith",
                "scaring crows",
                "a lewdly clothed maid",
                "collecting herbs",
                "writing tales and songs",
                "guarding the city gates",
                "gathering military intelligence",
                "summoning demons",
                "brewing potions",
                "chopping wood",
                "mining valuable ore",
            ]
        )
        c = "{}, you are now {} for {} minutes".format(
            ctx.message.author.mention, work, time
        )
        await self.bot.send_message(destination=ctx.channel, content=c)


def setup(bot):
    bot.add_cog(RPGGameActivities(bot))
