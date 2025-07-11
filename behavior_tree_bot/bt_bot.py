#!/usr/bin/env python
#

"""
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

from planet_wars import PlanetWars, finish_turn


# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots
def setup_behavior_tree():

    # Top-down construction of behavior tree
    root = Selector(name='High Level Ordering of Strategies')

    initial_offensive_plan = Sequence(name='Initial Offensive Strategy')
    weak_enemy_check = Check(if_weak_enemy_planet_available)
    attack_enemy = Action(all_attack_weakest_enemy_planet)
    initial_offensive_plan.child_nodes = [weak_enemy_check, attack_enemy]
   

    second_level_strategy = Selector(name='Second Level Strategy')

    initial_neutral_plan = Sequence(name='Initial Neutral Attack Plan')
    weak_neutral_check = Check(if_weak_neutral_planet_available)
    attack_neutral = Action(all_attack_weakest_neutral_planet)
    initial_neutral_plan.child_nodes = [weak_neutral_check, attack_neutral]

    #initial_offensive_plan.child_nodes = [weak_neutral_check, attack_neutral]

    defend_sequence = Sequence(name="Defense Plan (don't die)")
    weak_owned_planet_check = Check(if_weak_owned_planet)
    defend_action = Action(defend_planets)
    defend_sequence.child_nodes = [weak_owned_planet_check, defend_action]

    third_level_strategy = Selector(name='Third Level Strategy')

    remaining_neutrals_sequence = Sequence(name="Attack Remaining Neutrals")
    any_neutral = Check(if_neutral_planet_available)
    remaining_neutrals_sequence.child_nodes = [any_neutral, attack_neutral]

    stall_or_attack_selector = Selector(name='Stall or Attack (end game)')

    stall_strategy = Sequence(name='Stall Strategy')
    higher_growth_check = Check(have_highest_growth)
    not_biggest_fleet = Check(dont_have_largest_fleet)
    stall_strategy.child_nodes = [higher_growth_check, not_biggest_fleet, defend_action]

    stall_or_attack_selector.child_nodes = [stall_strategy, attack_enemy]

    third_level_strategy.child_nodes = [remaining_neutrals_sequence, stall_or_attack_selector]

    second_level_strategy.child_nodes = [initial_neutral_plan, defend_sequence, third_level_strategy]

    '''spread_sequence = Sequence(name='Spread Strategy')
    neutral_planet_check = Check(if_neutral_planet_available)
    spread_action = Action(spread_to_weakest_neutral_planet)
    spread_sequence.child_nodes = [neutral_planet_check, spread_action]'''

    root.child_nodes = [initial_offensive_plan, second_level_strategy]

    logging.info('\n' + root.tree_to_string())
    return root

# You don't need to change this function
def do_turn(state):
    behavior_tree.execute(planet_wars)

if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
