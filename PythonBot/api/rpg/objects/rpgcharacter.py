import math

from api.rpg import constants as rpgc

# Player starting stats
DEFAULT_HEALTH = 100
DEFAULT_ARMOR = 0
DEFAULT_DAMAGE = 10
DEFAULT_WEAPONSKILL = 1


class RPGCharacter:
    def __init__(self, name, picture_url, health, maxhealth, damage, weaponskill, critical, element=rpgc.element_none):
        self.name = name
        self.picture_url = picture_url
        self.health = health
        self.maxhealth = maxhealth
        self.damage = damage
        self.weaponskill = weaponskill
        self.critical = critical

    def get_level(self):
        return 1

    @staticmethod
    def adjust_stats(n, stat, item, amount=1):
        if item:
            m = item.benefit.get(stat)
            if m:
                if m[0] == "*":
                    return int(math.floor(n * (math.pow(m[1], amount))))
                if m[0] == "-":
                    return max(0, n - (amount * m[1]))
                if m[0] == "+":
                    return n + (amount * m[1])
        return n

    @staticmethod
    def elemental_effect(n, a_elem, d_elem):
        if a_elem != rpgc.element_none:
            if a_elem == (-1 * d_elem):
                n = math.floor(n * 1.2)
            if a_elem == d_elem:
                n = math.floor(n * 0.8)
        return n

    # Add (negative) health, returns true if successful
    def add_health(self, n: int, death=True, element=rpgc.element_none):
        self.health = int(max(0, min(self.get_max_health(), self.health + n)))

    def get_max_health(self):
        return self.maxhealth

    def get_health(self):
        if self.health > self.get_max_health():
            self.health = self.get_max_health()
        return self.health

    def get_damage(self, element=rpgc.element_none):
        return self.damage

    def get_critical(self):
        return int(self.critical)

    def get_weaponskill(self):
        return int(self.weaponskill)

    def get_element(self):
        return rpgc.element_none

    def __str__(self, **kwargs):
        return "{} ({}/{})".format(self.name, self.health, self.maxhealth)
