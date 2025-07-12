import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
import math
import logging


def all_attack_weakest_enemy_planet(state): 
    '''this attacks one enemy planet with every planet'''

        # (2) Find total ships
    total_planet_ships = sum(planet.num_ships for planet in state.my_planets())
    logging.info(f"total_planet_ships: {total_planet_ships}")
    
    ID_to_planet = {}
    for planet in state.enemy_planets(): 
        ID_to_planet[planet.ID] = (planet, planet.num_ships)

    remove_these_planets = set()
    
    for id, (n_planet, ships) in ID_to_planet.items():
        logging.info(f"{id} {n_planet} {ships}")
        for my_fleet in state.my_fleets():
            if my_fleet.destination_planet == id:
                if ships - my_fleet.num_ships <= 0:
                    remove_these_planets.add(id) #get rid of planets we already sent enough fleets to
                else:
                    ID_to_planet[id] = (planet, ships - my_fleet.num_ships)

    for id in remove_these_planets:
        ID_to_planet.pop(id)
    weakest_planet = None
    smallest_ship_count = 100000

    for planet, ships in ID_to_planet.values():
        if ships < smallest_ship_count:
            weakest_planet = planet
            smallest_ship_count = ships

    #calculate what percent of ships each planet needs to send and add 3 percent
    required_percent = weakest_planet.num_ships/total_planet_ships + 0.05
    
    for planet in state.my_planets():
        logging.info(f"planet_ships: {planet.num_ships}")
        logging.info(f"sent ships: {math.floor(planet.num_ships * required_percent)}")
        issue_order(state, planet.ID, weakest_planet.ID, math.floor(planet.num_ships * required_percent))
    return True


'''def attack_weakest_enemy_planet(state): 
    #this only attacks from one planet to another and always sends half of ships at planet

    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)
    logging.info(f"strongest planet: {strongest_planet}")

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)
'''

'''def spread_to_weakest_neutral_planet(state):
    #this only attacks from one planet to another and always sends half of ships at planet
    
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)
'''


def all_attack_weakest_neutral_planet(state): 
    '''this attacks one neutral planet with every planet'''

    # (2) Find total ships
    total_planet_ships = sum(planet.num_ships for planet in state.my_planets())
    logging.info(f"total_planet_ships: {total_planet_ships}")
    
    ID_to_planet = {}
    for planet in state.neutral_planets(): 
        ID_to_planet[planet.ID] = (planet, planet.num_ships)

    remove_these_planets = set()
    
    for id, (n_planet, ships) in ID_to_planet.items():
        logging.info(f"{id} {n_planet} {ships}")
        for my_fleet in state.my_fleets():
            if my_fleet.destination_planet == id:
                if ships - my_fleet.num_ships <= 0:
                    remove_these_planets.add(id) #get rid of planets we already sent enough fleets to
                else:
                    ID_to_planet[id] = (planet, ships - my_fleet.num_ships)

    for id in remove_these_planets:
        ID_to_planet.pop(id)

    weakest_planet = None
    smallest_ship_count = 100000

    for planet, ships in ID_to_planet.values():
        if ships < smallest_ship_count:
            weakest_planet = planet
            smallest_ship_count = ships

    #calculate what percent of ships each planet needs to send and add 3 percent
    required_percent = weakest_planet.num_ships/total_planet_ships + 0.05
    
    for planet in state.my_planets():
        logging.info(f"planet_ships: {planet.num_ships}")
        logging.info(f"sent ships: {math.floor(planet.num_ships * required_percent)}")
        issue_order(state, planet.ID, weakest_planet.ID, math.floor(planet.num_ships * required_percent))
    return True

def defend_planets(state):
    '''this defends one planet with every other planet'''

    planet_list = sorted(state.my_planets(), key=lambda p: p.num_ships)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.my_planets(), key=lambda t: t.num_ships, default=None)
    
    for planet in planet_list:
        issue_order(state, planet.ID, weakest_planet.ID, math.floor(planet.num_ships * 0.05))
    return True


'''def spread_to_neutral_with_all(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))
    #median_planet = my_planets[math.floor(len(my_planet)/2)]

    neutral_planets = [planet for planet in state.neutral_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    neutral_planets.sort(key=lambda p: p.num_ships) #neutral planets that I am not alraedy attacking

    target_planets = iter(neutral_planets)

    try: #currently attacks one at a time, maybe switch having multiple planets attack
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        sent_ships = 0
        while True:
            required_ships = target_planet.num_ships + 1
            
            #send 30% of ships from planet to target
            ships = math.floor(my_planet.num_ships*0.3)
            issue_order(state, my_planet.ID, target_planet.ID, ships)
            my_planet = next(my_planets)
            sent_ships += ships
            if sent_ships > required_ships:
                sent_ships = 0 #reset sent ships
                target_planet = next(target_planets)

    except StopIteration:
        return '''

def spread_to_neutral_with_half(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))
    median_planet = my_planets[math.floor(len(my_planet)/2)]

    neutral_planets = [planet for planet in state.neutral_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    neutral_planets.sort(key=lambda p: p.num_ships) #neutral planets that I am not alraedy attacking

    target_planets = iter(neutral_planets)

    try: #currently attacks one at a time, maybe switch having multiple planets attack
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        sent_ships = 0
        while True:
            required_ships = target_planet.num_ships + 0.01
            
            #If planet has above average ships, send 30% of ships
            if my_planet.num_ships > median_planet.num_ships:
                ships = math.floor(my_planet.num_ships*0.3)
                issue_order(state, my_planet.ID, target_planet.ID, ships)
                my_planet = next(my_planets)
                sent_ships += ships
                if sent_ships > required_ships:
                    target_planet = next(target_planets)
            else:
                sent_ships = 0 #reset sent ships
                my_planet = next(my_planets)
        

    except StopIteration: #once go through all planets once, 
                          #so may not go to all neutral planets in one turn, 
                          #but that might be fine
        return
    
def spread(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))
    #median_planet = my_planets[math.floor(len(my_planet)/2)]

    neutral_planets = [planet for planet in state.neutral_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    neutral_planets.sort(key=lambda p: p.num_ships) #neutral planets that I am not alraedy attacking

    target_planets = iter(neutral_planets)

    try: #currently attacks one at a time, maybe switch having multiple planets attack
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            required_ships = target_planet.num_ships + 1

            if my_planet.num_ships > required_ships:
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)
        

    except StopIteration:
        return
