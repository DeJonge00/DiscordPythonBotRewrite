from discord import Message

from api.rpg import constants as rpgc


async def check_role(self, role: str, message: Message, error='You') -> bool:
    if role not in [x[0] for x in rpgc.names.get("role")]:
        await self.bot.say("{} are still Undead. "
                           "Please select a class with '{}rpg role' in order to start to play!"
                           .format(error, await self.bot._get_prefix(message)))
        return False
    return True
