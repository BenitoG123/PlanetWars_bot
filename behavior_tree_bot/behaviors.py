import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
import math
import logging

def do_nothing(state):
    return True


def get_attacked_planets(state): #within 5 turns
    IDs = {}
    vulnerable = {}
    for planet in state.my_planets():
      IDs[planet.ID] = planet
    for fleet in state.enemy_fleets():
        if fleet.destination_planet in IDs:
            if fleet.turns_remaining <= 5:
              if fleet.destination_planet in vulnerable.keys():
                  vulnerable[IDs[fleet.destination_planet]] += fleet.num_ships
              else:
                vulnerable[IDs[fleet.destination_planet]] = fleet.num_ships
              logging.info(f"turns to my planet {fleet.turns_remaining}")
              
    return vulnerable

def strength(state, p):
        return p.num_ships \
               + sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID) \
               - sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)


def attack_neutral_planet_near(state):
    neutral_planets = [planet for planet in state.neutral_planets()
                       if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    list = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    strongest = list[0]
    for neutral in neutral_planets:
        distance = state.distance(neutral.ID, strongest.ID)
        if (distance < 10) and (neutral.num_ships + 2 < strongest.num_ships):
            issue_order(state, strongest.ID, neutral.ID, neutral.num_ships + 2)
    return True


def attack_enemy_planet_near(state):
    enemy_planets = [planet for planet in state.enemy_planets()
                       if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    list = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    strongest = list[0]
    for enemy in enemy_planets:
        distance = state.distance(enemy.ID, strongest.ID)
        if (distance < 10) and (enemy.num_ships + 2 < strongest.num_ships):
            issue_order(state, strongest.ID, enemy.ID, enemy.num_ships + 2)
    return True

def attack_not_mine(state):
    my_list = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    target_list = sorted(state.my_planets(), key=lambda p: p.num_ships)
    strong = my_list[0]
    weak = target_list[0]

    if weak.num_ships + (weak.growth_rate * state.distance(weak.ID, strong.ID)) + 1 < strong.num_ships:
        issue_order(state, strong.ID, weak.ID, weak.num_ships + ((weak.growth_rate * state.distance(weak.ID, strong.ID)) + 1))
    else:
        issue_order(state, strong.ID, weak.ID, math.floor(strong.num_ships * 0.5))
    return True



def defend_vulnerable(state):
    vulnerable = get_attacked_planets(state)
    strong_planets = []
    for planet in state.my_planets():
        if planet not in vulnerable.keys():
            strong_planets.append(planet)
    strong_planets = sorted(strong_planets, key=lambda p: p.num_ships)
    for w_planet, ships in vulnerable.items:
        if w_planet.ships <= ships:
            needed_ships = ships - w_planet.ships + 1
            for s_planet in strong_planets:
                if s_planet.ships > needed_ships:
                    issue_order(state, s_planet.ID, w_planet.ID, needed_ships)
    return True

def defend_against_fleets(state):
    frontline = get_frontline_planets(state)
    #planet_order = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    attacked = {}
    for fleet in state.enemy_fleets():
        if fleet.destination_planet in attacked.keys():
            attacked[fleet.destination_planet] += fleet.num_ships
        else:
            attacked[fleet.destination_planet] = fleet.num_ships
    for planet in state.my_planets():
        if planet.ID in attacked.keys():
            if planet.num_ships < attacked[planet.ID] + 1:
                done = False
                for f_planet in frontline:
                    if done == False:
                        if f_planet.num_ships > planet.num_ships - attacked[planet.ID] + 1:
                            issue_order(state, f_planet.ID, planet.ID, planet.num_ships - attacked[planet.ID] + 1)
    return True



def get_frontline_planets(state): #currently 5 turns away or less
    frontline = set()
    for enemy in state.enemy_planets():
        for mine in state.my_planets():
            if state.distance(enemy.ID, mine.ID) <= 5:
                frontline.add(mine)
    for neutral in state.neutral_planets():
        for mine in state.my_planets():
            if state.distance(neutral.ID, mine.ID) <= 5:
                frontline.add(mine)
    return frontline

def reinforce_frontline(state):
    frontline = get_frontline_planets(state)
    front_planets = len(frontline)
    for planet in state.my_planets():
        if planet not in frontline:
            for f_planet in frontline:
                if planet.num_ships > 1:
                    issue_order(state, planet.ID, f_planet.ID, math.floor(planet.num_ships/front_planets)-1)
    return True


'''def attack_capturable_neutrals(state):
    frontline = get_frontline_planets(state)
    neutrals = sorted(state.neutral_planets(), key=lambda p: p.num_ships)
    for neutral in neutrals:
        for f_planet in frontline:
            if f_planet.num_ships > neutral.num_ships + 2:
                issue_order(state, f_planet.ID, neutral.ID, neutral.num_ships + 2)
                break'''

def attack_weak_neutrals(state):
    neutral_planets = sorted(state.neutral_planets(), key=lambda p: p.num_ships)
    IDs = {}
    for p in neutral_planets:
        IDs[p.ID] = p
    for fleet in state.my_fleets():
        if fleet.destination_planet in IDs.keys():
            IDs.pop(fleet.destination_planet)
    
    for neutral in IDs.values():
        for my_planet in state.my_planets():
          if my_planet.num_ships > (neutral.num_ships + 2):
            logging.info(f"my planet {my_planet.ID}")
            logging.info(f"neutral planet {my_planet.ID}")
            issue_order(state, my_planet.ID, neutral.ID, neutral.num_ships + 2)
            break
    return True

def attack_weak_enemies(state):
    enemy_planets = sorted(state.enemy_planets(), key=lambda p: p.num_ships)
    IDs = {}
    for p in enemy_planets:
        IDs[p.ID] = p
    for fleet in state.my_fleets():
        if fleet.destination_planet in IDs.keys():
            IDs.pop(fleet.destination_planet)
    already_attacked = []
    for my_planet in state.my_planets():
        for enemy in IDs.values():
          if my_planet.num_ships > (enemy.num_ships + 2):
              if enemy not in already_attacked:
                issue_order(state, my_planet.ID, enemy.ID, enemy.num_ships + 2)
                already_attacked.append(enemy)
    return True

'''def attack_capturable_enemies(state):
    frontline = get_frontline_planets(state)
    enemies = sorted(state.enemy_planets(), key=lambda p: p.num_ships)
    for enemy in enemies:
        ships = enemy.num_ships
        for f_planet in frontline:
            ships += (state.distance(f_planet.ID, enemy.ID) * enemy.growth_rate)
            if f_planet.num_ships > enemy.num_ships + 5:
                issue_order(state, f_planet.ID, enemy.ID, enemy.num_ships + 5)
                break'''



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
    required_percent = smallest_ship_count/total_planet_ships + 0.01
    
    for planet in state.my_planets():
        logging.info(f"planet_ships: {planet.num_ships}")
        logging.info(f"sent ships: {math.floor(planet.num_ships * required_percent)}")
        issue_order(state, planet.ID, weakest_planet.ID, math.floor(planet.num_ships * required_percent))
    return True

def same_percent_attack(state, my_ships, enemy_planet, enemy_ships):

    required_percent = enemy_ships/my_ships + 0.01
    for planet in state.my_planets():
        logging.info(f"planet_ships: {planet.num_ships}")
        logging.info(f"sent ships: {math.floor(planet.num_ships * required_percent)}")
        issue_order(state, planet.ID, enemy_planet.ID, math.floor(planet.num_ships * required_percent))
    return True

def differnt_percent_attack(state, enemy_planet, enemy_ships):

    ordered_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)

    required_percent = 0.5 #start at 50%
    for planet in ordered_planets:
        if planet.num_ships <= 10: #don't attack if only 10 ships
            continue
        if enemy_ships <= 0:
            break
        #logging.info(f"planet_ships: {planet.num_ships}")
        #logging.info(f"sent ships: {math.floor(planet.num_ships * required_percent)}")
        if planet.num_ships > enemy_ships + 20:
            issue_order(state, planet.ID, enemy_planet.ID, enemy_ships + 5)
        else:
            send_ships = math.floor(planet.num_ships*required_percent)
            issue_order(state, planet.ID, enemy_planet.ID, send_ships)
            enemy_ships -= send_ships
            required_percent -= 0.1
            if required_percent <= 0.2: #minimum 20%
                required_percent = 0.2

    return True


def total_planet_distance(state, destination_planet):
    distance = 0
    for planet in state.my_planets():
        #logging.info(f"my planet x {planet.x}")
        #logging.info(f"my planet y {planet.y}")
        #logging.info(f"destination planet x {destination_planet.x}")
        #logging.info(f"destination planet y {destination_planet.y}")
        distance += math.sqrt((destination_planet.x - planet.x)**2 + (destination_planet.y - planet.y)**2)
    return distance

def all_attack_closest_neutral_planet(state): 
    '''this attacks one neutral planet with every planet'''

    # (2) Find total ships
    
    closest_planet = None
    shortest_distance = 1000000
    for neutral in state.neutral_planets():
        distance = total_planet_distance(state, neutral)
        if distance < shortest_distance:
            shortest_distance = distance
            closest_planet = neutral

    differnt_percent_attack(state, closest_planet, closest_planet.num_ships)

    return True

def all_attack_closest_enemy_planet(state): 
    '''this attacks one neutral planet with every planet'''

    # (2) Find total ships
    
    closest_planet = None
    shortest_distance = 1000000
    for enemy in state.enemy_planets():
        distance = total_planet_distance(state, enemy)
        if  distance< shortest_distance:
            shortest_distance = distance
            closest_planet = enemy

    differnt_percent_attack(state, closest_planet, closest_planet.num_ships)

    return True



def defend_planets(state): #send 25% of ships from strong to weak
    '''above average defends below average'''

    planet_list = sorted(state.my_planets(), key=lambda p: p.num_ships)
    
    while(True):
        length = len(planet_list)
        if length <= 1:
            break
        issue_order(state, planet_list[0].ID, planet_list[length - 1].ID, math.floor(planet_list[0].num_ships * 0.25))
        planet_list.pop(length - 1)
        planet_list.pop(0)
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
