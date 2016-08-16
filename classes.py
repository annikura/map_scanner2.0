import sys

map_was_loaded = False
data = []
list_pointer = 0


class GlobalConst:
    empty = "None"  # ! changes can lead to problems with files
    not_found = "Not found\n"
    if sys.platform == 'linux':
        encoding = 'koi8-r'
    elif sys.platform in ['win32', 'cygwin']:
        encoding = 'cp1251'
    players_cnt = 8
    town_types = 9
    hex_base = 16
    random_town = "Random town"


class FormatConst:
    roe = "RoE"
    ab = "AB"
    wog = "WoG"
    sod = "SoD"


class GTypeConsts:
    art = {FormatConst.roe: 1,
           FormatConst.ab: 2,
           FormatConst.sod: 2,
           FormatConst.wog: 2}


class VictoryConst:
    none = GlobalConst.empty
    AqArt = "Acquire a specific artifact"
    AccCreat = "Accumulate creatures"
    AccRes = "Accumulate resources"
    UpgTwn = "Upgrade a specific town"
    BldStrct = "Build a grail structure"
    DftHer = "Defeat a specific Hero"
    CptTwn = "Capture a specific town"
    DftMnstr = "Defeat a specific monster"
    FlgDwel = "Flag all creature dwelling"
    FlgMns = "Flag all mines"
    TrnsArt = "Transport a specific artifact"


class LossConst:
    none = GlobalConst.empty
    LsTwn = "Lose a specific town"
    LsHer = "Lose a specific hero"
    TimExp = "Time expires"


def clear():
    global data, map_was_loaded, list_pointer
    data = []
    map_was_loaded = False
    list_pointer = 0


def _get_bool():
    return _get_int() == 1


def _rubbish(x=1):
    global list_pointer
    list_pointer += x


def _get_string(num_size=4):
    global list_pointer
    string_len = _get_int(num_size)
    string = ''
    for _ in range(string_len):
        string += bytes([_get_int()]).decode(GlobalConst.encoding)
    return string


def _get_int(num_size=1):
    global list_pointer
    a = [data[list_pointer + i] for i in range(num_size)]
    list_pointer += num_size
    number = ''
    for i in range(len(a)):
        number = a[i] + number
    return int(number, GlobalConst.hex_base)


def _get_fileline(filename, req_index):
    with open(filename) as file:
        ret_line = GlobalConst.not_found
        for line in file:
            separator = line.find('-')
            line_index = int(line[:separator])
            if line_index == req_index:
                ret_line = line[separator + 1:]
                break
        return ret_line[:ret_line.rfind('\n')]


def _get_given_fileline(filename, num_size=1):
    return _get_fileline(filename, _get_int(num_size))


class MapData:
    def __init__(self):
        global list_pointer
        save_p = list_pointer
        try:
            self.format = _get_given_fileline('formats.txt', num_size=4)
            self.general = GeneralData()
            self.players_meta = PlayersData(self.format)
            self.victory_cond = VictoryCond(self.format)
            self.loss_cond = LossCond()
            self.teams_meta = TeamsData(self.players_meta.active_players)
        finally:
            list_pointer = save_p


class GeneralData:
    def __init__(self):
        self.is_hero_on_map = _get_int() == 1
        # sets as "1" if there are any heroes on the map.
        self.size = _get_int(num_size=4)
        self.layers = _get_int()
        self.name = _get_string()
        self.description = _get_string()
        self.difficulty = _get_given_fileline('difficulties.txt')


class PlayersData:
    def __init__(self, f):
        if f != FormatConst.roe:
            self.level_limit = _get_int()
        else:
            self.level_limit = 0
        self.players = []
        self.human_players = []
        self.computer_players = []
        self.hum_n_comp_players = []
        self.active_players = []
        for player in range(GlobalConst.players_cnt):
            sample = Player(f, player)
            if sample.is_human or sample.is_comp:
                self.players.append(sample)
                self.active_players.append(player)
            if sample.is_human and not sample.is_comp:
                self.human_players.append(player)
            elif sample.is_comp and not sample.is_human:
                self.computer_players.append(player)
            if sample.is_human and sample.is_comp:
                self.hum_n_comp_players.append(player)
        self.players_cnt = len(self.players)


class Player:
    def __init__(self, f, index):
        self.colour = _get_fileline('players.txt', index)
        self.index = index + 1
        self.is_human = _get_int()
        self.is_comp = _get_int()
        self.behavior = _get_given_fileline('behavior.txt')
        if f != FormatConst.ab and f != FormatConst.roe:
            self.ex_town_config = _get_bool()  # what does it do?
        else:
            self.ex_town_config = 1
        town_types_bitmask = _get_int(num_size=2)
        self.available_town_types = []
        for i in range(GlobalConst.town_types):
            if len(bin(town_types_bitmask)) > i and \
               bin(town_types_bitmask)[i] == '1':  # ~ i-th bit is "1"
                self.available_town_types.append(_get_fileline('town_types.txt', i))
        if f != FormatConst.roe:
            self.ex_random_town = _get_bool()
        else:
            self.ex_random_town = town_types_bitmask == \
                                  int("01FF", GlobalConst.hex_base)
        if self.ex_random_town:
            self.available_town_types = [GlobalConst.random_town]  # consts?
        self.is_main_town = _get_bool()
        self.towns = []
        if self.is_main_town:
            if f != FormatConst.roe:
                self.towns.append(Town(priority="Main", ownership=self.colour,
                                       f_create_hero=_get_bool(),
                                       t_type=_get_given_fileline('town_types.txt')))
            else:
                self.towns.append(Town(priority="Main", ownership=self.colour))
        self.ex_random_hero = _get_bool()
        hero_type = _get_int()
        self.heroes = []
        heroes_cnt = 1
        if hero_type != int("FF", GlobalConst.hex_base):  # if hero type == FF there is no any hero
            self.heroes.append(Hero(hero_type=hero_type, face=_get_int(), name=_get_string()))
            if f != FormatConst.roe:
                _rubbish()
                heroes_cnt = _get_int(num_size=4)
        if f != FormatConst.roe:
            for hero in range(heroes_cnt):
                sample = Hero(hero_type=_get_int(), name=_get_string())
                already_exits = False
                for hero_structure in self.heroes:
                    if sample.id == hero_structure.id:
                        already_exits = True
                if not already_exits:
                    self.heroes.append(sample)


class VictoryCond:
    def __init__(self, f):
        self.type = _get_given_fileline('victory_conditions.txt')
        self.ex_standard_ending = True
        self.is_available_for_comp = True
        if self.type != VictoryConst.none:
            self.ex_standard_ending = _get_bool()
            self.is_available_for_comp = _get_bool()
            self.obj_name = GlobalConst.empty
            self.req_quantity = 0
            self.ex_coordinates = False
            self.obj_coordinates = Coordinates(False)
            self.req_hall_level = GlobalConst.empty
            self.req_castle_level = GlobalConst.empty
            if self.type in [VictoryConst.AqArt, VictoryConst.TrnsArt]:
                self.req_quantity = 1
                if self.type in [VictoryConst.AqArt]:
                    self.obj_name = _get_given_fileline('artifacts.txt', num_size=GTypeConsts.art[f])  # AB
                if self.type in [VictoryConst.TrnsArt]:
                    self.obj_name = _get_given_fileline('artifacts.txt')  # AB
            if self.type in [VictoryConst.AccRes, VictoryConst.AccCreat]:
                if self.type == VictoryConst.AccRes:
                    self.obj_name = _get_given_fileline('resources.txt')  # SOD?
                if self.type == VictoryConst.AccCreat:
                    self.obj_name = _get_given_fileline('creatures.txt', num_size=2)  # AB
                self.req_quantity = _get_int(num_size=4)
            if self.type in [VictoryConst.UpgTwn, VictoryConst.BldStrct, VictoryConst.DftHer,
                             VictoryConst.DftMnstr, VictoryConst.CptTwn, VictoryConst.TrnsArt]:
                self.ex_coordinates = True
                self.obj_coordinates = Coordinates()
            if self.type == VictoryConst.UpgTwn:
                self.req_hall_level = _get_given_fileline('hall_levels.txt')
                self.req_castle_level = _get_given_fileline('castle_levels.txt')


class LossCond:
    def __init__(self):
        self.type = _get_given_fileline('loss_conditions.txt')
        self.ex_coordinates = False
        self.obj_coordinates = Coordinates(False)
        self.quantity = 0
        if self.type in [LossConst.LsHer, LossConst.LsTwn]:
            self.quantity = 1
            self.ex_coordinates = True
            self.obj_coordinates = Coordinates()
        if self.type == LossConst.TimExp:
            self.quantity = _get_int(num_size=2)  # in days


class TeamsData:
    def __init__(self, active_players):
        self.quantity = _get_int()
        self.teams = []
        if self.quantity > 0:
            for i in range(self.quantity):
                self.teams.append([])
            for player in range(GlobalConst.players_cnt):
                if player in active_players:
                    self.teams[_get_int()].append(_get_fileline('players.txt', player))


class Town:
    def __init__(self, priority="Unknown", ownership="Unknown",
                 hall_level="Unknown", castle_level="Unknown",
                 f_create_hero=False, t_type="Unknown\n"):
        self.f_create_hero = f_create_hero
        self.type = t_type
        self.hall_level = hall_level
        self.castle_level = castle_level
        self.priority = priority
        self.ownership = ownership
        self.location = Coordinates()


class Hero:
    def __init__(self, hero_type, face=int("FF", GlobalConst.hex_base), name=""):
        if name == "":
            name = _get_fileline('heroes.txt', hero_type)
        if face == int("FF", GlobalConst.hex_base):
            face = hero_type
        self.id = hero_type
        self.name = name
        self.face = face


class Coordinates:
    def __init__(self, flag=True):
        self.x = 0
        self.y = 0
        self.z = 0
        if flag:
            self.x = _get_int()
            self.y = _get_int()
            self.z = _get_int()
