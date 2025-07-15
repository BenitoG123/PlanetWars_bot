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
    #not_defending = Check(not_already_defending)
    not_dead = Check(havent_lost_yet)
    can_i_go_for_it = Check(opportunity_check)
    #need_to_defend = Check(if_need_reinforcement)
    easy_enemy = Check(should_attack_enemy)
    easy_neutral = Check(should_attack_neutral)
    ok_enemy = Check(can_attack_enemy)
    ok_neutral = Check(can_attack_neutral)
    not_won_yet = Check(any_other_planets)
    any_neutral = Check(if_neutral_planet_available)
    any_enemy = Check(if_enemy_planet_available)
    biggest_fleet = Check(have_largest_fleet)
    
    # actions
    attack_best_enemies = Action(best_enemy_attack)
    attack_best_neutrals = Action(best_neutral_attack)
    attack_ok_enemies = Action(best_enemy_attack)
    attack_ok_neutrals = Action(best_neutral_attack)
    go_for_it = Action(opportunity_attack)
    #attack_any = Action(attack_not_mine)
    total_defend = Action(defend_all_vulnerable)
    #reinforce = Action(reinforce_frontline)
    nothing = Action(do_nothing)
    
    #sequences
    #root = Sequence(name='High Level Ordering of Strategies')
    attack_best_enemy_sequence = Sequence(name='Primary Enemy Attack Sequence')
    attack_best_neutral_sequence = Sequence(name='Primary Neutral Attack Sequence')
    attack_ok_enemy_sequence = Sequence(name='Secondary Enemy Attack Sequence')
    attack_ok_neutral_sequence = Sequence(name='Secondary Neutral Attack Sequence')
    defend_self_sequence = Sequence(name='Defense Sequence')
    am_i_ahead = Sequence(name='Do I have the advantage sequence')
    last_ditch = Sequence(name='Last Ditch Attack')
    #do_something = Sequence(name='Do something semi-usefull')

    #selectors
    root = Selector(name='High Level Ordering of Strategies')
    #round1 = Selector(name='First Priority')
    #round2 = Selector(name='Second Priority')
    #second_level_strategy = Selector(name='Second Level Strategy')
    #third_level_strategy = Selector(name='Third Level Strategy')
    #stall_or_attack_selector = Selector(name='Stall or Attack (end game)')
    #stall_strategy = Sequence(name='Stall Strategy')

    #decorators
    #always_true_defense = AlwaysSucceed(name='Always Succeed Decorator')
    #always_true_neutral = AlwaysSucceed(name='Always Succeed Decorator')
   

    #construct Tree

    #I lost count
    #root.child_nodes = [round1, round2]
    #round1.child_nodes = [attack_enemy_sequence, attack_neutral_sequence, defend_self_sequence, do_something]
    #round2.child_nodes = [attack_enemy_sequence, attack_neutral_sequence, defend_self_sequence, do_something]
    root.child_nodes = [am_i_ahead, attack_best_enemy_sequence, attack_best_neutral_sequence, attack_ok_neutral_sequence, attack_ok_enemy_sequence, defend_self_sequence, nothing]
    am_i_ahead.child_nodes = [any_enemy, can_i_go_for_it, go_for_it]
    attack_best_enemy_sequence.child_nodes = [not_won_yet, not_dead, any_enemy, easy_enemy, attack_best_enemies]
    attack_best_neutral_sequence.child_nodes = [not_won_yet, not_dead, any_neutral, easy_neutral, attack_best_neutrals]
    attack_ok_enemy_sequence.child_nodes = [not_won_yet, not_dead, any_enemy, ok_enemy, attack_ok_enemies]
    attack_ok_neutral_sequence.child_nodes = [not_won_yet, not_dead, any_neutral, ok_neutral, attack_ok_neutrals]
    defend_self_sequence.child_nodes = [not_won_yet, not_dead, total_defend]
    #do_something.child_nodes = [not_dead, not_won_yet, attack_any]


    #attempt 3 or 4ish
    #root.child_nodes = [defense, neutral_attack, enemy_attack, nothing]
    #defense.child_nodes = [need_to_defend, defend]
    #neutral_attack.child_nodes = [any_neutral, any_weak_neutral, attack_neutrals, reinforce]
    #enemy_attack.child_nodes = [any_enemy, any_weak_enemy, attack_enemies]




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
