from api.rpg.objects.rpgcharacter import RPGCharacter
import math


class RPGPet(RPGCharacter):
    def __init__(self, name='Kittycat',
                 picture_url='https://i.pinimg.com/236x/da/9f/28/da9f286defe9f112ebc5c58ced971747--black-cats-cat-art.jpg',
                 health=1, maxhealth=1, damage=1, weaponskill=1, critical=0, exp=0):
        self.exp = exp
        super(RPGPet, self).__init__(name, picture_url, health, maxhealth, damage, weaponskill, critical)

    def add_exp(self, n: int):
        if self.health <= 0:
            return
        lvl = self.get_level()
        self.exp += n
        lvl = self.get_level() - lvl
        if lvl > 0:
            self.damage += 10 * lvl
            self.weaponskill += lvl

    @staticmethod
    def get_level_by_exp(exp: int):
        return int(math.sqrt(exp) / 15) + 1

    def get_level(self):
        return RPGPet.get_level_by_exp(self.exp)

    def as_dict(self):
        return {
            'name': self.name,
            'picture_url': self.picture_url,
            'health': self.health,
            'maxhealth': self.maxhealth,
            'damage': self.damage,
            'weaponskill': self.weaponskill,
            'critical': self.critical,
            'exp': self.exp
        }


def dict_to_pet(pet: dict):
    return RPGPet(
        name=pet.get('name'),
        picture_url=pet.get('picture_url'),
        health=pet.get('health'),
        maxhealth=pet.get('maxhealth'),
        damage=pet.get('damage'),
        weaponskill=pet.get('weaponskill'),
        critical=pet.get('critical'),
        exp=pet.get('exp')
    )
