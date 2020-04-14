from discord import Message

from api.rpg import constants as rpgc
from core.bot import PythonBot
from api.rpg.objects.rpgcharacter import RPGCharacter


async def check_role(bot: PythonBot, role: str, message: Message, error='You') -> bool:
    if role not in [x[0] for x in rpgc.names.get("role")]:
        await bot.send_message("{} are still Undead. "
                               "Please select a class with '{}rpg role' in order to start to play!"
                               .format(error, await bot.get_prefix(message)))
        return False
    return True


async def shorten_exp(exp: int):
    if exp > 1000000000:
        return str(int(exp / 1000000000)) + "B"
    if exp > 1000000:
        return str(int(exp / 1000000)) + "M"
    if exp > 1000:
        return str(int(exp / 1000)) + "K"
    return str(int(exp))


def add_health_rep(players: [RPGCharacter]):
    health_report = ""
    for m in players:
        health_report += m.name + " ({})\n".format(m.get_health())
    if len(health_report) > 0:
        return health_report
    return None


def construct_battle_report(title_length: int, report_actions: [(RPGCharacter, RPGCharacter, int, bool)]) -> (
        list, str):
    battle = []
    text = ''

    for attacker in set([s[0] for s in report_actions]):
        attackers_attacks = [s for s in report_actions if s[0] == attacker]
        for defender in set([x[1] for x in attackers_attacks]):
            hits = [(s[2], s[3]) for s in attackers_attacks if s[1] == defender]
            text += '\n**{}** attacked **{}** {} times for a total of {} damage'.format(attacker.name,
                                                                                        defender.name, len(hits),
                                                                                        sum([x[0] for x in hits]))
            crits = sum([1 for x in hits if x[1]])
            if crits == 1:
                text += ', including a critical!'
            if crits > 1:
                text += ', including {} criticals!'.format(crits)

            # Split up message because of discords character limit
            if len(text) > (900 if len(battle) > 0 else 900 - title_length):
                battle.append(text)
                text = ''

    # Min and max damage
    if len(report_actions) > 0:
        max_char, _, max_dam, _ = max(report_actions, key=lambda item: item[2])
        stats = '**{}** did the most damage ({})'.format(max_char.name, max_dam)
        min_char, _, min_dam, _ = min(report_actions, key=lambda item: item[2])
        if min_dam != max_dam:
            stats += '\n**{}** did the least damage ({})'.format(min_char.name, min_dam)
    else:
        stats = None

    battle.append(text)
    return battle, stats
