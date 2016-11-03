#!/usr/bin/env python3

import argparse
import codecs

import filework
import classes
from classes import MapData
import consts


parser = argparse.ArgumentParser(prog=consts.prog_name, description=consts.prog_description)

parser.add_argument("filepath", help="path to a map file")
detail_group = parser.add_mutually_exclusive_group()
parser.add_argument("--encoding", help="sets a new encoding ('" +
                                       classes.GlobalConst.encoding +
                                       "' is by default)")

detail_group.add_argument("--none", help="sets the degree of detalization to 'none'", action="store_true")
detail_group.add_argument("--brief", help="sets the degree of detalization to 'brief'", action="store_true")
detail_group.add_argument("--standard", help="sets the degree of detalization to 'standard'", action="store_true")
detail_group.add_argument("--extended", help="sets the degree of detalization to 'extended'", action="store_true")

args = parser.parse_args()
filework.load_map(args.filepath)
map_st = MapData()

det = 2
if args.none:
    det = 0
if args.brief:
    det = 1
if args.extended:
    det = 3

if args.encoding:
    try:
        codecs.lookup(args.encoding)
        filework.set_encoding(args.encoding)
    except LookupError:
        print(args.encoding, "is not an encoding")
        exit(0)

if det >= 1:
    print("-Format:", map_st.format)
    print("-Size:", map_st.general.size, "x", map_st.general.size, "x", map_st.general.layers + 1)
    print("-Name:", map_st.general.name)
    print("-Description:", map_st.general.description)
    print("-Difficulty:", map_st.general.difficulty)
    print("-Number of players:", len(map_st.players_meta.active_players))
    if det >= 2:
        print("\t", len(map_st.players_meta.computer_players), "computer players")
        print("\t", len(map_st.players_meta.hum_n_comp_players), "human or computer players")
        print("\t", len(map_st.players_meta.human_players), "human players")
    if det >= 3:
        print("-Personal data:")
        for player in map_st.players_meta.players:
            print("\tPlayer", player.index)
            print("\t\tColour:", player.colour)
            print("\t\tCan be played by human:", player.is_human == 1)
            print("\t\tCan be played by computer:", player.is_comp == 1)
            if len(player.heroes) != 0:
                print("\t\tHeroes:", end=' ')
            for hero in player.heroes:
                print(hero.name, end=' ')
            print()
        if map_st.players_meta.level_limit != 0:
            print("-Level limit:", map_st.players_meta.level_limit)
    print("-Victory condition:", map_st.victory_cond.type)
    if det >= 2:
        if map_st.victory_cond.type != classes.GlobalConst.empty:
            print("\tStandard ending is also available:", map_st.victory_cond.ex_standard_ending)
            print("\tAvailable for computer players:", map_st.victory_cond.is_available_for_comp)
    if det >= 3:
        if map_st.victory_cond.type in [classes.VictoryConst.AqArt,
                                        classes.VictoryConst.AccCreat,
                                        classes.VictoryConst.AccRes,
                                        classes.VictoryConst.TrnsArt]:
            print("\tObject name:", map_st.victory_cond.obj_name)
            print("\tRequired quantity:", map_st.victory_cond.req_quantity)
    print("-Loss condition:", map_st.loss_cond.type)
    if map_st.loss_cond.type == classes.LossConst.TimExp:
        print("\tin", map_st.loss_cond.quantity // 28, "months and",
              map_st.loss_cond.quantity % 28, "days")
    if map_st.teams_meta.quantity > 0:
        print("-There are", map_st.teams_meta.quantity, "teams")
        if det >= 3:
            for num in range(map_st.teams_meta.quantity):
                print("\tTeam", num + 1)
                for player in map_st.teams_meta.teams[num]:
                    print("\t\t", player)
