import random, math
from random import randint
from api.rpg import constants as rpgc


class RPGWeapon:
    def __init__(
        self,
        name="Training Sword",
        cost=0,
        element=1,
        damage=0,
        weaponskill=0,
        critical=0,
    ):
        self.name = name
        self.cost = cost
        self.element = element
        self.damage = damage
        self.weaponskill = weaponskill
        self.critical = critical

    def __str__(self):
        return "{}: d+{}, ws+{}, c+{}".format(
            self.name, self.damage, self.weaponskill, self.critical
        )

    def as_dict(self):
        return {
            "name": self.name,
            "cost": self.cost,
            "element": self.element,
            "damage": self.damage,
            "weaponskill": self.weaponskill,
            "critical": self.critical,
        }


def dict_to_weapon(weapon: dict):
    return RPGWeapon(
        name=weapon.get("name"),
        cost=weapon.get("cost"),
        element=weapon.get("element"),
        damage=weapon.get("damage"),
        weaponskill=weapon.get("weaponskill"),
        critical=weapon.get("critical"),
    )


def generate_weapon(cost: int):
    name = str(random.choice(rpgc.prefixes))
    i = random.choice(list(rpgc.elementnames.keys()))
    name += (
        " "
        + rpgc.elementnames.get(i)[1]
        + " "
        + str(random.choice(rpgc.weapons))
        + " "
        + str(random.choice(rpgc.suffixes))
    )

    damage = weaponskill = critical = 0
    points = math.floor(cost / 90)
    first = randint(0, 99)
    if first < 45:
        r = randint(0, points)
        damage += r
        points -= r
    elif first < 80:
        r = randint(0, points)
        weaponskill += math.floor(r / 3)
        points -= r
    else:
        r = randint(0, points)
        critical += math.floor(r / 7)
        points -= r

    second = randint(0, 99)
    if second < 45:
        damage += points
    elif second < 80:
        weaponskill += math.floor(points / 3)
    else:
        critical += math.floor(points / 7)
    return RPGWeapon(
        name=name,
        cost=cost,
        element=i,
        damage=damage,
        weaponskill=weaponskill,
        critical=critical,
    )
