import logging
import math


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

def havent_lost_yet(state):
    if len(state.my_planets()) == 0:
        return False
    return True

def have_highest_growth(state): # checks if I get more ships per turn than opponent
    return sum(planet.growth_rate for planet in state.my_planets()) \
           > sum(planet.growth_rate for planet in state.enemy_planets()) \
           
def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

def if_neutral_planet_available(state):
    return len(state.neutral_planets()) > 0

def if_enemy_planet_available(state):
    return len(state.enemy_planets()) > 0

def any_other_planets(state):
    return len(state.not_my_planets()) > 0

    

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

def should_attack_neutral(state):
    neutral_planets = [(planet,neutral_strength(state, planet)) for planet in state.neutral_planets()]
    neutral_planets = sorted(neutral_planets, key=lambda x: x[1])

    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    strongest = my_planets[0]

    for neutral, neutral_power in neutral_planets:
        if close_neutral(state, neutral) and (neutral_power + 2 < strongest.num_ships):
            return True
    return False

def should_attack_enemy(state):
    enemy_planets = [(planet,enemy_strength(state, planet)) for planet in state.enemy_planets()]
    enemy_planets = sorted(enemy_planets, key=lambda x: x[1])
    n = 5

    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    strongest = my_planets[0]

    for enemy, enemy_power in enemy_planets:
        if close_enemy(state, enemy, n) and (enemy_power + (n * enemy.growth_rate) < strongest.num_ships):
            return True
    return False

def can_attack_neutral(state):
    neutral_planets = [(planet,neutral_strength(state, planet)) for planet in state.neutral_planets()]
    neutral_planets = sorted(neutral_planets, key=lambda x: x[1])

    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    strongest = my_planets[0]

    for neutral, neutral_power in neutral_planets:
        if (neutral_power + 2 < strongest.num_ships):
            return True
    return False

def can_attack_enemy(state):
    enemy_planets = [(planet,enemy_strength(state, planet)) for planet in state.enemy_planets()]
    enemy_planets = sorted(enemy_planets, key=lambda x: x[1])
    n = 5

    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    strongest = my_planets[0]

    for enemy, enemy_power in enemy_planets:
        if (enemy_power + (n * enemy.growth_rate) < strongest.num_ships):
            return True
    return False

def closest_planet(state, p):
    closest_planet = None
    shortest_distance = 1000000
    for enemy in state.enemy_planets():
        if shortest_distance > state.distance(p.ID, enemy.ID):
            shortest_distance = state.distance(p.ID, enemy.ID)
            closest_planet = enemy
    return closest_planet

def opportunity_check(state):
    for planet in state.my_planets():
        strength = my_strength(state, planet)
        enemy = closest_planet(state, planet)
        if (planet.num_ships >= enemy.num_ships * 2) and (strength >= enemy.num_ships * 2):
            return True
        
    return False

def should_defend(state):
    return min(my_strength(planet) for planet in state.my_planets()) <= 0