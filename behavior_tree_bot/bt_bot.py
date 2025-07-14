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
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check, AlwaysSucceed

from planet_wars import PlanetWars, finish_turn


# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots
def setup_behavior_tree():

    # checks
    need_to_defend = Check(if_need_reinforcement)
    any_enemy = Check(if_enemy_planet_available)
    #any_close_fleet = Check(any_close_enemy_fleet)
    #weak_enemy_check = Check(if_weak_enemy_planet_available)
    #weak_neutral_check = Check(if_weak_neutral_planet_available)
    #weak_owned_planet_check = Check(if_weak_owned_planet)
    any_neutral = Check(if_neutral_planet_available)
    any_weak_neutral = Check(if_weak_neutral_available)
    any_weak_enemy = Check(if_weak_enemy_available)
    #higher_growth_check = Check(have_highest_growth)
    #not_biggest_fleet = Check(dont_have_largest_fleet)
    #close_neutral_not_too_big = Check(closest_neutral_not_too_big)
    
    # actions
    attack_enemies = Action(attack_weak_enemies)
    attack_neutrals = Action(attack_weak_neutrals)
    defend = Action(defend_against_fleets)
    reinforce = Action(reinforce_frontline)
    nothing = Action(do_nothing)
    #attack_weak_enemy = Action(all_attack_weakest_enemy_planet)
    #attack_weak_neutral = Action(all_attack_weakest_neutral_planet)
    #defend_action = Action(defend_planets)
    #attack_close_neutral = Action(all_attack_closest_neutral_planet)
    #attack_close_enemy = Action(all_attack_closest_enemy_planet)
    
    #sequences
    defense = Sequence(name='Defense Sequence')
    neutral_attack = Sequence(name='Neutral Attack Sequence')
    enemy_attack = Sequence(name='Enemy Attack Sequence')
    #initial_offensive_plan = Sequence(name='Initial Offensive Strategy')
    #initial_neutral_plan = Sequence(name='Initial Neutral Attack Plan')
    #defend_sequence = Sequence(name="Defense Plan (don't die)")
    #remaining_neutrals_sequence = Sequence(name="Attack Remaining Neutrals")
    #get_close_neutrals_sequence = Sequence(name="Attack Close Neutrals")

    #selectors
    root = Selector(name='High Level Ordering of Strategies')
    #second_level_strategy = Selector(name='Second Level Strategy')
    #third_level_strategy = Selector(name='Third Level Strategy')
    #stall_or_attack_selector = Selector(name='Stall or Attack (end game)')
    #stall_strategy = Sequence(name='Stall Strategy')

    #decorators
    #always_true_defense = AlwaysSucceed(name='Always Succeed Decorator')
    #always_true_neutral = AlwaysSucceed(name='Always Succeed Decorator')
   

    #construct Tree

    #attempt 3 or 4ish
    root.child_nodes = [neutral_attack]
    #root.child_nodes = [defense, neutral_attack, enemy_attack, nothing]
    defense.child_nodes = [need_to_defend, defend]
    neutral_attack.child_nodes = [any_neutral, any_weak_neutral, attack_neutrals, reinforce]
    enemy_attack.child_nodes = [any_enemy, any_weak_enemy, attack_enemies]




    #attempt 2 distance and neutrals
    '''root.child_nodes = [always_true_defense, always_true_neutral, enemy_attack]
    always_true_defense.child_nodes = [defense]
    always_true_neutral.child_nodes = [neutral_attack]
    defense.child_nodes = [any_close_fleet, defend]
    neutral_attack.child_nodes = [any_neutral, attack_neutrals]
    enemy_attack.child_nodes = [any_enemy, attack_enemies]'''



    #get_close_neutrals_sequence.child_nodes = [any_neutral, attack_close_neutral]
    #attempt 1 weak enemies
    '''root.child_nodes = [initial_offensive_plan, second_level_strategy]
    initial_offensive_plan.child_nodes = [weak_enemy_check, attack_weak_enemy]
    second_level_strategy.child_nodes = [initial_neutral_plan, defend_sequence, third_level_strategy]
    initial_neutral_plan.child_nodes = [weak_neutral_check, attack_weak_neutral]
    defend_sequence.child_nodes = [weak_owned_planet_check, defend_action]
    third_level_strategy.child_nodes = [remaining_neutrals_sequence, stall_or_attack_selector]
    remaining_neutrals_sequence.child_nodes = [any_neutral, attack_weak_neutral]
    stall_or_attack_selector.child_nodes = [stall_strategy, attack_weak_enemy]
    stall_strategy.child_nodes = [higher_growth_check, not_biggest_fleet, defend_action]'''


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
