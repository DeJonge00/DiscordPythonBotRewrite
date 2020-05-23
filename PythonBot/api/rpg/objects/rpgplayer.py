import math

from api.rpg import constants as rpgc
from api.rpg.objects import rpgcharacter
from api.rpg.objects.rpgarmor import RPGArmor, dict_to_armor
from api.rpg.objects.rpgpet import RPGPet, dict_to_pet
from api.rpg.objects.rpgshopitem import RPGShopItem
from api.rpg.objects.rpgweapon import RPGWeapon, dict_to_weapon

DEFAULT_ROLE = 'Undead'

# Busydescription status
BUSY_DESC_NONE = 0
BUSY_DESC_ADVENTURE = 1
BUSY_DESC_TRAINING = 2
BUSY_DESC_BOSSRAID = 3
BUSY_DESC_WANDERING = 4
BUSY_DESC_WORKING = 5

# Min and max busy time
minadvtime = 5
maxadvtime = 120
mintrainingtime = 10
maxtrainingtime = 60
minwandertime = 30
maxwandertime = 360
minworkingtime = 30
maxworkingtime = 120


# TODO Add busystatus class


class RPGPlayer(rpgcharacter.RPGCharacter):
    def __init__(self, userid: int, username: str,
                 picture_url='https://i.pinimg.com/originals/97/7b/b8/977bb8f6f1fc78778f3225ed83b1b4ba.jpg', exp=0,
                 level=0, money=0, role=DEFAULT_ROLE, weapon=RPGWeapon(),
                 armor=RPGArmor(), pets: [RPGPet] = [], health=rpgcharacter.DEFAULT_HEALTH,
                 maxhealth=rpgcharacter.DEFAULT_HEALTH,
                 damage=rpgcharacter.DEFAULT_DAMAGE, weaponskill=rpgcharacter.DEFAULT_WEAPONSKILL, critical=0,
                 bosstier=1,
                 kingtimer=0, extratime=0):
        self.userid = userid
        self.role = role
        self.exp = exp
        self.level = level
        self.money = money
        self.weapon = weapon
        self.armor = armor
        self.pets = pets
        self.busytime = 0
        self.busychannel = 0
        self.busydescription = BUSY_DESC_NONE
        self.bosstier = bosstier
        self.kingtimer = kingtimer
        self.extratime = extratime
        super(RPGPlayer, self).__init__(username, picture_url, health, maxhealth, damage, weaponskill, critical)

    @staticmethod
    def get_level_by_exp(exp: int):
        return math.floor(math.sqrt(exp) / 25) + 1

    def resolve_death(self):
        if self.get_health() <= 0 and self.role != rpgc.names.get('role')[-1][0]:
            self.exp = max(0, self.exp - 100 * self.get_level())
            self.money = int(math.floor(self.money * 0.5))
            self.busytime = 0

    def add_exp(self, n: int):
        if self.get_health() <= 0:
            return
        # lvl = self.get_level()
        self.exp += n

    def add_health(self, n: int, death=True, element=rpgc.element_none):
        super().add_health(n)
        if death:
            self.resolve_death()

    def add_money(self, n: int):
        if n < 0:
            return False
        n = (1 + (self.armor.money / 100)) * n
        self.money = int(self.money + n)
        return True

    def subtract_money(self, n: int):
        if n < 0 or self.money - n < 0:
            return False
        self.money = int(math.floor(self.money - n))
        return True

    def get_max_health(self):
        if self.role == rpgc.names.get('role')[-1][0]:
            return rpgcharacter.DEFAULT_HEALTH
        n = self.maxhealth + self.armor.maxhealth
        if self.role == rpgc.names.get('role')[1][0]:
            n *= 0.85
        if self.role == rpgc.names.get('role')[3][0]:
            n *= 1.2
        return int(n)

    def get_element(self):
        return self.armor.element if self.armor.element else rpgc.element_none

    def buy_item(self, item: RPGShopItem, amount=1):
        if not self.subtract_money(int(math.ceil(amount * item.cost))):
            return False
        self.health = min(self.get_max_health(),
                          rpgcharacter.RPGCharacter.adjust_stats(self.get_health(), "health", item, amount=amount))
        self.set_max_health(rpgcharacter.RPGCharacter.adjust_stats(self.maxhealth, "maxhealth", item, amount=amount))
        self.damage = rpgcharacter.RPGCharacter.adjust_stats(self.damage, "damage", item, amount=amount)
        self.critical = rpgcharacter.RPGCharacter.adjust_stats(self.critical, "critical", item, amount=amount)
        return True

    def buy_training(self, item: RPGShopItem, amount=1):
        self.set_max_health(rpgcharacter.RPGCharacter.adjust_stats(self.maxhealth, "maxhealth", item, amount=amount))
        self.weaponskill = rpgcharacter.RPGCharacter.adjust_stats(self.weaponskill, "weaponskill", item, amount=amount)

    def buy_armor(self, item: RPGArmor):
        if not self.subtract_money(item.cost):
            return False
        self.money += int(math.floor(self.armor.cost * 0.25))
        self.armor = item
        self.add_health(0)
        return True

    def buy_weapon(self, item: RPGWeapon):
        if not self.subtract_money(item.cost):
            return False
        self.money += int(math.floor(self.weapon.cost * 0.25))
        self.weapon = item
        return True

    def get_level(self):
        return RPGPlayer.get_level_by_exp(self.exp)

    def get_bosstier(self):
        return self.bosstier

    def add_bosstier(self):
        self.bosstier += 1

    def set_busy(self, action: int, time: int, channel: int):
        self.busytime = time
        self.busychannel = channel
        self.busydescription = action

    def reset_busy(self):
        self.busytime = 0
        self.busychannel = 0
        self.busydescription = BUSY_DESC_NONE

    def set_max_health(self, n: int):
        r = self.get_health() / self.get_max_health()
        self.maxhealth = n
        self.health = int(math.ceil(r * self.get_max_health()))

    def get_damage(self, element=rpgc.element_none):
        n = super().get_damage(element=element)
        n = rpgcharacter.RPGCharacter.elemental_effect(n, self.weapon.element, element)
        if self.role == rpgc.names.get('role')[1][0]:  # role == Sorcerer
            n *= 1.3
        if self.role == rpgc.names.get("role")[-1][0]:  # role == Kitten
            n *= 3
        return int(n + self.weapon.damage)

    def get_weaponskill(self):
        if self.role == rpgc.names.get('role')[-1][0]:
            return 1
        n = super().get_weaponskill()
        return int(n + self.weapon.weaponskill)

    def get_critical(self):
        n = super().get_critical()
        return int(n + self.weapon.critical)

    def do_auto_health_regen(self):
        if self.busydescription == BUSY_DESC_NONE:
            percentage = 0.025 if self.role == rpgc.names.get('role')[4][0] else 0.01
        else:
            percentage = 0.035 if self.role == rpgc.names.get('role')[4][0] else 0.06
        self.add_health((self.get_max_health() * percentage) + self.armor.healthregen)

    def add_pet(self, pet: RPGPet):
        if len(self.pets) >= 3:
            return False
        self.pets.append(pet)
        return True

    def as_dict(self):
        return {
            'stats': {
                'name': self.name,
                'picture_url': str(self.picture_url),
                'health': self.get_health(),
                'maxhealth': self.maxhealth,
                'damage': self.damage,
                'weaponskill': self.weaponskill,
                'critical': self.critical
            },
            'userid': str(self.userid),
            'role': self.role,
            'exp': self.exp,
            'level': self.level,
            'money': self.money,
            'weapon': self.weapon.as_dict(),
            'armor': self.armor.as_dict(),
            'pets': [pet.as_dict() for pet in self.pets],
            'busy': {
                'time': self.busytime,
                'channel': self.busychannel,
                'description': self.busydescription
            },
            'bosstier': self.bosstier,
            'kingtimer': self.kingtimer,
            'extratime': self.extratime
        }


def dict_to_player(player: dict):
    stats = player.get('stats')
    busy = player.get('busy')
    player = RPGPlayer(
        userid=player.get('userid'),
        picture_url=stats.get('picture_url',
                              'https://i.pinimg.com/originals/97/7b/b8/977bb8f6f1fc78778f3225ed83b1b4ba.jpg'),
        username=stats.get('name'),
        exp=player.get('exp'),
        level=player.get('level', 0),
        money=player.get('money'),
        role=player.get('role'),
        weapon=dict_to_weapon(player.get('weapon')),
        armor=dict_to_armor(player.get('armor')),
        pets=[dict_to_pet(pet) for pet in player.get('pets')],
        health=stats.get('health'),
        maxhealth=stats.get('maxhealth'),
        damage=stats.get('damage'),
        weaponskill=stats.get('weaponskill'),
        critical=stats.get('critical'),
        bosstier=player.get('bosstier'),
        kingtimer=player.get('kingtimer'),
        extratime=player.get('extratime')
    )
    bc = 0 if busy.get('channel') == '' else int(busy.get('channel'))
    player.set_busy(action=busy.get('description'), time=busy.get('time'), channel=bc)
    return player
