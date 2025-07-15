import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
import math
import logging

def do_nothing(state):
    return True

def my_strength(state, p):
        return p.num_ships \
               + sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID) \
               - sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)

def enemy_strength(state, p):
        return p.num_ships \
               + sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID) \
               - sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID)

def neutral_strength(state, p):
    power = p.num_ships - sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)
    if (power < 0):
        power = -1*power
    power  -= sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID)
    return power

def close_neutral(state, p):
    if len(state.enemy_planets()) == 0:
        enemy_distance = 10000
    else:
        enemy_distance = min(state.distance(p.ID, enemy.ID) for enemy in state.enemy_planets())
    my_distance = min(state.distance(p.ID, mine.ID) for mine in state.my_planets())

    return my_distance < enemy_distance
        
def close_enemy(state, p, c): #if enemy is close to me
    for mine in state.my_planets():
        if state.distance(p.ID, mine.ID) <= c:
            return True
    return False


def best_neutral_attack(state):
    neutral_planets = [(planet,neutral_strength(state, planet)) for planet in state.neutral_planets()]
    neutral_planets = sorted(neutral_planets, key=lambda x: x[1])

    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    
    for neutral, neutral_power in neutral_planets:
        for mine in my_planets:
            total_ships = neutral_power + 2
            if total_ships > 0:
                if close_neutral(state, neutral) and (total_ships < mine.num_ships):
                    logging.info(f"attack neutral {mine.ID, neutral.ID}")
                    issue_order(state, mine.ID, neutral.ID, total_ships)
                    break
    return True

def best_enemy_attack(state):
    enemy_planets = [(planet,enemy_strength(state, planet)) for planet in state.enemy_planets()]
    enemy_planets = sorted(enemy_planets, key=lambda x: x[1])

    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    
    for enemy, enemy_power in enemy_planets:
        for mine in my_planets:
            distance = state.distance(enemy.ID, mine.ID)
            total_ships = enemy_power + (distance*enemy.growth_rate) + 2
            if total_ships > 0:
                if close_enemy(state, enemy, 5) and (total_ships < mine.num_ships):
                    issue_order(state, mine.ID, enemy.ID, total_ships)
                    break
    return True

def ok_neutral_attack(state):
    neutral_planets = [(planet,neutral_strength(state, planet)) for planet in state.neutral_planets()]
    neutral_planets = sorted(neutral_planets, key=lambda x: x[1])

    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)

    for neutral, neutral_power in neutral_planets:
        for mine in my_planets:
            total_ships = neutral_power + 2
            if total_ships > 0:
                if (total_ships < mine.num_ships):
                    issue_order(state, mine.ID, neutral.ID, total_ships)
                    break
    return True

def ok_enemy_attack(state):
    logging.info("try ok attack")
    enemy_planets = [(planet,enemy_strength(state, planet)) for planet in state.enemy_planets()]
    enemy_planets = sorted(enemy_planets, key=lambda x: x[1])

    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    
    for enemy, enemy_power in enemy_planets:
        for mine in my_planets:
            if (enemy_power < mine.num_ships):
                logging.info("ok attack order went through")
                issue_order(state, mine.ID, enemy.ID, enemy_power)
                
                break
    return True

def closest_planet(state, p):
    closest_planet = None
    shortest_distance = 1000000
    for enemy in state.enemy_planets():
        if shortest_distance > state.distance(p.ID, enemy.ID):
            shortest_distance = state.distance(p.ID, enemy.ID)
            closest_planet = enemy
    return closest_planet

def opportunity_attack(state):
    for planet in state.my_planets():
        enemy = closest_planet(state, planet)
        if planet.num_ships >= enemy.num_ships * 2:
            issue_order(state, planet.ID, enemy.ID, math.floor(enemy.num_ships * 1.5))
        
    return True

'''def attack_not_mine(state):
    my_list = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    target_list = sorted(state.my_planets(), key=lambda p: p.num_ships)
    strong = my_list[0]
    weak = target_list[0]

    if weak.num_ships + (weak.growth_rate * state.distance(weak.ID, strong.ID)) + 1 < strong.num_ships:
        issue_order(state, strong.ID, weak.ID, weak.num_ships + ((weak.growth_rate * state.distance(weak.ID, strong.ID)) + 1))
    else:
        issue_order(state, strong.ID, weak.ID, math.floor(strong.num_ships * 0.5))
    return True'''


def defend_all_vulnerable(state):
    vulnerable = []
    excess = []
    for p in state.my_planets():
        strength = my_strength(state, p)
        if strength <= 0:
            vulnerable.append((p, -1*strength))
        else:
            excess.append((p, strength))
    
    vulnerable = sorted(excess, key=lambda p: p[1])
    excess = sorted(excess, key=lambda p: p[1], reverse=True)

    for i, (strong, extra) in enumerate(excess):
        if (strong.num_ships <= 1) or (extra <= 1):
            continue
        for j, (weak, need) in enumerate(vulnerable):
            if need < 0:
                continue
            if (extra > need + 1) and (strong.num_ships > need + 1):
                issue_order(state, strong.ID, weak.ID, need + 1)
                vulnerable[j] = (weak, -1)
                excess[i] = (strong, extra - (need+1))
            elif (extra < strong.num_ships):
                issue_order(state, strong.ID, weak.ID, extra - 1)
                vulnerable[j] = (weak, need - (extra - 1))
                excess[i] = (strong, 0)
                break
            else:
                issue_order(state, strong.ID, weak.ID, strong.num_ships -1)
                vulnerable[j] = (weak, need - (strong.num_ships - 1))
                excess[i] = (strong, 0)
                break
                    
    return True

'''def defend_some_vulnerable(state):
    avg = sum(strength(planet) for planet in my_planets) / len(my_planets)'''