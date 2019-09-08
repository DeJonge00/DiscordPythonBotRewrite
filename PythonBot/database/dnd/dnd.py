import database.common as common

RPG_DND_DATABASE = 'rpgdnd'

SOURCE_TABLE = 'sources'
RACE_TABLE = 'playableraces'
CLASS_TABLE = 'playableclasses'
SUBCLASS_TABLE = 'playablesubclasses'
BACKGROUND_TABLE = 'backgrounds'

ASC = 1
DESC = -1


def get_table(table):
    return common.get_table(RPG_DND_DATABASE, table)


def reset_database():
    get_table(SOURCE_TABLE).delete_many({})
    get_table(RACE_TABLE).delete_many({})
    get_table(CLASS_TABLE).delete_many({})
    get_table(SUBCLASS_TABLE).delete_many({})
    get_table(BACKGROUND_TABLE).delete_many({})


def fill_sources():
    sources = [
        {'id': 0, 'name': 'Player Handbook', 'shortname': 'PHB', 'enabled': True},
        {'id': 1, 'name': 'Dungeon Master\'s Guide', 'shortname': 'DMG', 'enabled': True},
        {'id': 2, 'name': 'Xanathar\'s Guide To Everything', 'shortname': 'XGtE', 'enabled': False},
        {'id': 3, 'name': 'Unearthed Arcana', 'shortname': 'UA', 'enabled': False},
        {'id': 4, 'name': 'Homebrew', 'shortname': 'HB', 'enabled': False},
        {'id': 5, 'name': 'Monster Manual', 'shortname': 'MM', 'enabled': False},
        {'id': 6, 'name': 'Volo\'s Guide to Monsters', 'shortname': 'VGtM', 'enabled': False},
        {'id': 7, 'name': 'Mordenkainen\'s Tome of Foes', 'shortname': 'MToF', 'enabled': False},
        {'id': 8, 'name': 'Tomb of Annihalation', 'shortname': 'ToA', 'enabled': False},
        {'id': 9, 'name': 'Guildmasters\' Guide to Ravnica', 'shortname': 'GGtR', 'enabled': False},
        {'id': 10, 'name': 'Aquisitions Incorperated', 'shortname': 'AI', 'enabled': False},
        {'id': 11, 'name': 'Sword Coast Adventurer\'s Guide', 'shortname': 'SCAG', 'enabled': False},
        {'id': 12, 'name': 'Curse of Strahd', 'shortname': 'CoS', 'enabled': False},
        {'id': 13, 'name': 'Ghosts of Saltmarsh', 'shortname': 'GoS', 'enabled': False}
    ]
    get_table(SOURCE_TABLE).insert_many(sources)


def get_sources():
    s = list(get_table(SOURCE_TABLE).find({}, {'_id': 0}))
    return sorted(s, key=lambda l: l.get('name')) if s else []


def fill_races():
    races = [
        {'id': 0, 'name': 'Aarakocra', 'source': 6},
        {'id': 1, 'name': 'Aasimar', 'source': 6},
        {'id': 2, 'name': 'Bugbear', 'source': 6},
        {'id': 3, 'name': 'Changeling', 'source': 3},
        {'id': 4, 'name': 'Dragonborn', 'source': 0},
        {'id': 5, 'name': 'Dwarf', 'source': 0},
        {'id': 6, 'name': 'Eladrin', 'source': 3},
        {'id': 7, 'name': 'Elf', 'source': 0},
        {'id': 8, 'name': 'Firbolg', 'source': 6},
        {'id': 9, 'name': 'Genasi', 'source': 3},
        {'id': 10, 'name': 'Gith', 'source': 7},
        {'id': 11, 'name': 'Goblin', 'source': 6},
        {'id': 12, 'name': 'Goliath', 'source': 3},
        {'id': 13, 'name': 'Gnome', 'source': 0},
        {'id': 14, 'name': 'Grung', 'source': 6},
        {'id': 15, 'name': 'Half-Elf', 'source': 0},
        {'id': 16, 'name': 'Half-Dwarf', 'source': 4},
        {'id': 17, 'name': 'Half-Orc', 'source': 0},
        {'id': 18, 'name': 'Halfling', 'source': 0},
        {'id': 19, 'name': 'Hobgoblin', 'source': 6},
        {'id': 20, 'name': 'Human', 'source': 0},
        {'id': 21, 'name': 'Kalashtar', 'source': 4},
        {'id': 22, 'name': 'Kenku', 'source': 6},
        {'id': 23, 'name': 'Kobold', 'source': 6},
        {'id': 24, 'name': 'Lizardfolk', 'source': 6},
        {'id': 25, 'name': 'Minotaur', 'source': 3},
        {'id': 26, 'name': 'Orc', 'source': 6},
        {'id': 27, 'name': 'Shifter', 'source': 3},
        {'id': 28, 'name': 'Tabaxi', 'source': 6},
        {'id': 29, 'name': 'Tiefling', 'source': 0},
        {'id': 30, 'name': 'Tortle', 'source': 4},
        {'id': 31, 'name': 'Triton', 'source': 6},
        {'id': 32, 'name': 'Yuan-Ti Pureblood', 'source': 6},
        {'id': 33, 'name': 'Warforged', 'source': 3}
    ]
    get_table(RACE_TABLE).insert_many(races)


def get_races(source='all'):
    f = {} if source == 'all' else {'source': {'$in': source}}
    r = list(get_table(RACE_TABLE).find(f, {'_id': 0}))
    return sorted(r, key=lambda l: l.get('name')) if r else []


def fill_backgrounds():
    backgrounds = [
        {'id': 0, 'name': 'Acolyte', 'source': 0},
        {'id': 1, 'name': 'Anthropologist', 'source': 8},
        {'id': 2, 'name': 'Archaeologist', 'source': 8},
        {'id': 3, 'name': 'Azorius Functionary', 'source': 9},
        {'id': 4, 'name': 'Charlatan', 'source': 0},
        {'id': 5, 'name': 'City Watch', 'source': 11},
        {'id': 6, 'name': 'Clan Crafter', 'source': 11},
        {'id': 7, 'name': 'Cloistered Scholar', 'source': 11},
        {'id': 8, 'name': 'Courtier', 'source': 11},
        {'id': 9, 'name': 'Criminal', 'source': 0},
        {'id': 10, 'name': 'Entertainer', 'source': 0},
        {'id': 11, 'name': 'Faction Agent', 'source': 11},
        {'id': 12, 'name': 'Far Traveler', 'source': 11},
        {'id': 13, 'name': 'Folk Hero', 'source': 0},
        {'id': 14, 'name': 'Gladiator', 'source': 0},
        {'id': 15, 'name': 'Guild Artisan', 'source': 0},
        {'id': 16, 'name': 'Guild Merchant', 'source': 0},
        {'id': 17, 'name': 'Haunted One', 'source': 12},
        {'id': 18, 'name': 'Hermit', 'source': 0},
        {'id': 19, 'name': 'Inheritor', 'source': 11},
        {'id': 20, 'name': 'Investigator', 'source': 11},
        {'id': 21, 'name': 'Knight', 'source': 0},
        {'id': 22, 'name': 'Knight of the Order', 'source': 11},
        {'id': 23, 'name': 'Mercenary Veteran', 'source': 11},
        {'id': 24, 'name': 'Noble', 'source': 0},
        {'id': 25, 'name': 'Outlander', 'source': 0},
        {'id': 26, 'name': 'Pirate', 'source': 0},
        {'id': 27, 'name': 'Sage', 'source': 0},
        {'id': 28, 'name': 'Sailor', 'source': 0},
        {'id': 29, 'name': 'Soldier', 'source': 0},
        {'id': 30, 'name': 'Spy', 'source': 0},
        {'id': 31, 'name': 'Urban Bounty Hunter', 'source': 11},
        {'id': 32, 'name': 'Urchin', 'source': 0},
        {'id': 33, 'name': 'Uthgardt Tribe Member', 'source': 11},
        {'id': 34, 'name': 'Waterdhavian Noble', 'source': 11},
        {'id': 35, 'name': 'Boros Legionnaire', 'source': 9},
        {'id': 36, 'name': 'Celebrity Adventurer’s Scion', 'source': 10},
        {'id': 37, 'name': 'Dimir Operative', 'source': 9},
        {'id': 38, 'name': 'Gambler', 'source': 10},
        {'id': 39, 'name': 'Goldari Agent', 'source': 9},
        {'id': 40, 'name': 'Gruul Anarch', 'source': 9},
        {'id': 41, 'name': 'Izzet Engineer', 'source': 9},
        {'id': 42, 'name': 'Marine', 'source': 13},
        {'id': 43, 'name': 'Plaintiff', 'source': 10},
        {'id': 43, 'name': 'Rakdos Cultist', 'source': 9}
    ]
    get_table(BACKGROUND_TABLE).insert_many(backgrounds)


def get_backgrounds(source='all'):
    f = {} if source == 'all' else {'source': {'$in': source}}
    r = list(get_table(BACKGROUND_TABLE).find(f, {'_id': 0}))
    return sorted(r, key=lambda l: l.get('name')) if r else []


def fill_database():
    fill_sources()
    fill_races()
    fill_backgrounds()


if __name__ == '__main__':
    reset_database()
    fill_database()
