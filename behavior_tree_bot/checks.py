import logging
import math

def have_highest_growth(state): # checks if I get more ships per turn than opponent
    return sum(planet.growth_rate for planet in state.my_planets()) \
           > sum(planet.growth_rate for planet in state.enemy_planets()) \
           
def any_close_enemy_planet(state): #currently 5 turns away or less
    for enemy in state.enemy_planets():
        for mine in state.my_planets():
             if state.distance(enemy.ID, mine.ID) <= 5:
                 return True
    return False

def get_frontline_planets(state): #currently 5 turns away or less
    frontline = []
    for enemy in state.enemy_planets():
        for mine in state.my_planets():
             if state.distance(enemy.ID, mine.ID) <= 5:
                 frontline.append(mine)
    return frontline

def get_attacked_planets(state): #within 5 turns
    IDs = {}
    vulnerable = {} #planet -> ships attacking it
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

def any_planet_attacked(state):
    if len(get_attacked_planets(state)) > 0:
        return True
    else:
        return False

def if_need_reinforcement(state):
    vulnerable = get_attacked_planets(state)

    for planet, ships in vulnerable.items():
        for fleet in state.my_fleets():
            if fleet.destination_planet == planet.ID:
                ships -= fleet.num_ships
        if planet.num_ships <= ships:
            return True
    return False

def any_close_enemy_fleet(state): #within 5 turns
    IDs = {}
    #vulnerable = []
    for planet in state.my_planets():
      IDs[planet.ID] = planet
    for fleet in state.enemy_fleets():
        if fleet.destination_planet in IDs:
            if fleet.turns_remaining <= 5:
              #vulnerable.append(IDs[fleet.destination_planet])
              logging.info(f"turns to my planet {fleet.turns_remaining}")
              return True
    return False

           
def my_plant_vulnerable(state): #determine if one of my planets could be taken over by current enemy fleet
    return min(planet.num_ships for planet in state.my_planets()) \
            + sum(fleet.num_ships for fleet in state.my_fleets()) \
          > sum(fleet.num_ships for fleet in state.enemy_fleets())

def dont_have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           < sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets()) + 5

def if_neutral_planet_available(state):
    neutral_planets = [planet for planet in state.neutral_planets()
                       if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    return len(neutral_planets) > 0

def if_neutral_planet_near(state):
    neutral_planets = [planet for planet in state.neutral_planets()
                       if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    list = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    strongest = list[0]
    for neutral in neutral_planets:
        distance = state.distance(neutral.ID, strongest.ID)
        if (distance < 5) and (neutral.num_ships + 2 < strongest.num_ships):
            return True
    return False

def if_enemy_planet_available(state):
    enemy_planets = [planet for planet in state.enemy_planets()
                       if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    return len(enemy_planets) > 0

def if_enemy_planet_near(state):
    enemy_planets = [planet for planet in state.enemy_planets()
                       if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    list = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    strongest = list[0]
    for enemy in enemy_planets:
        distance = state.distance(enemy.ID, strongest.ID)
        if (distance < 5) and (enemy.num_ships + 2 < strongest.num_ships):
            return True
    return False

def strength(state, p):
        return p.num_ships \
               + sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID) \
               - sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)


def not_already_defending(state):
    list = sorted(state.my_planets(), key=lambda p: p.num_ships)
    weakest = list[0]
    for fleet in state.my_fleets():
        if fleet.destination_planet == weakest.ID:
            return True
    return False

def any_other_planets(state):
    list = state.not_my_planets()
    if len(list) > 0:
        return True
    else:
        return False

def if_close_neutral(state):
    neutral_planets = [planet for planet in state.neutral_planets()
                       if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    neutral_planets.sort(key=lambda p: p.num_ships)
    sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)

def if_weak_neutral_available(state):
    neutral_planets = sorted(state.neutral_planets(), key=lambda p: p.num_ships)
    IDs = {}
    for p in neutral_planets:
        IDs[p.ID] = p
    for fleet in state.my_fleets():
        if fleet.destination_planet in IDs.keys():
            IDs.pop(fleet.destination_planet)
    for my_planet in state.my_planets():
        for neutral in IDs.values():
          if my_planet.num_ships > (neutral.num_ships + 2):
              return True
    return False
          
def if_weak_enemy_available(state): #doesn't send more than one fleet to attack, could be bad
    enemy_planets = sorted(state.enemy_planets(), key=lambda p: p.num_ships)
    IDs = {}
    for p in enemy_planets:
        IDs[p.ID] = p
    for fleet in state.my_fleets():
        if fleet.destination_planet in IDs.keys():
            IDs.pop(fleet.destination_planet)
    for my_planet in state.my_planets():
        for enemy in IDs.values():
          distance = state.distance(my_planet.ID, enemy.ID)
          if my_planet.num_ships > (enemy.num_ships + (distance * enemy.growth_rate) + 2):
              return True
    return False

def about_to_lose(state):
   return sum(planet.num_ships for planet in state.my_planets()) <= 0

def total_planet_distance(state, destination_planet):
    distance = 0
    for planet in state.my_planets():
        distance += math.sqrt((destination_planet.x - planet.x)**2 + (destination_planet.y - planet.y)**2)
    return distance

def closest_neutral_not_too_big(state):
    closest_planet = None
    shortest_distance = 1000000
    for neutral in state.neutral_planets():
        distance = total_planet_distance(state, neutral)
        if  distance< shortest_distance:
            shortest_distance = distance
            closest_planet = neutral

    return closest_planet.num_ships < sum(planet.num_ships for planet in state.my_planets())
    

'''def if_weak_neutral_planet_available(state): #currently at 10%
    if if_neutral_planet_available(state):
      total_planet_ships = sum(planet.num_ships for planet in state.my_planets())
      weakest_neutral_ships = min(planet.num_ships for planet in state.neutral_planets())
      if weakest_neutral_ships/total_planet_ships <= 0.5: #less than or equal to 10% of total ships
        return True
      else:
         return False
    else:
        False'''


'''def if_weak_neutral_planet_available(state): #currently at 30%
    
    if if_neutral_planet_available(state): #is there any neutrals?
        pass
    else:
        return False
    # (2) Find total ships
    total_planet_ships = sum(planet.num_ships for planet in state.my_planets())
    logging.info(f"total_planet_ships: {total_planet_ships}")
    
    ID_to_planet = {}
    for planet in state.neutral_planets(): 
        ID_to_planet[planet.ID] = (planet, planet.num_ships)
    
    remove_these_planets = set()

    for id, (n_planet, ships) in ID_to_planet.items():
        #logging.info(f"id:{id} {n_planet} {ships}")
        #logging.info(f"planet: {n_planet}")
        #logging.info(f"ships: {ships}")
        for my_fleet in state.my_fleets():
            if my_fleet.destination_planet == id:
                if ships - my_fleet.num_ships <= 0:
                    #logging.info(f"ships {ships}")
                    #logging.info(f"fleet attacking ships {my_fleet.num_ships}")
                    #logging.info("remove this planet")
                    remove_these_planets.add(id) #get rid of planets we already sent enough fleets to
                else:
                    ID_to_planet[id] = (planet, ships - my_fleet.num_ships)
    for id in remove_these_planets:
        ID_to_planet.pop(id)
    
    if ID_to_planet == {}:
        return False

    weakest_planet = None
    smallest_ship_count = 100000

    logging.info(f"{ID_to_planet}")

    for planet, ships in ID_to_planet.values():
        #logging.info(f"planet {planet} ships {ships}")
        #logging.info(f"ships {ships}")
        if ships < smallest_ship_count:
            weakest_planet = planet
            smallest_ship_count = ships
            logging.info(f"new weakest planet {weakest_planet}")
    logging.info(f"weakest planet {weakest_planet}")
    #calculate what percent of ships each planet needs to send and add 3 percent
    return weakest_planet.num_ships < total_planet_ships * 0.3'''

'''def if_weak_neutral_planet_available(state): #currently at 10%
    total_planet_ships = sum(planet.num_ships for planet in state.my_planets()) \
      + sum(fleet.num_ships for fleet in state.my_fleets())
    planet_ships = {}
    for planet in state.neutral_planets():
      planet_ships[planet] = planet.num_ships #planet -> ships defending it
    for fleet in state.my_fleets():
        if fleet.destination_planet in state.neutral_planets():
          planet_ships[fleet.destination_planet] -= fleet.num_ships

    open_planets = []
    for planet in planet_ships.keys():
       if planet_ships[planet] > 0:
          open_planets.append(planet)
    if (open_planets == []) or (len(state.neutral_planets()) == 0):
       logging.info("no enemy planets left")
       return False
    return min(planet.num_ships for planet in open_planets) <= (total_planet_ships * 0.1) #10% of all my planet ships
  '''

def if_weak_owned_planet(state):
    total_planet_ships = sum(planet.num_ships for planet in state.my_planets()) \
      + sum(fleet.num_ships for fleet in state.my_fleets())
    planet_ships = {}
    for planet in state.my_planets():
      planet_ships[planet] = 0 #planet -> ships defending it
    for fleet in state.my_fleets():
        if fleet.destination_planet in state.my_planets():
          planet_ships[fleet.destination_planet] = fleet.num_ships()
    for planet in state.my_planets():
        logging.info(f"planet: {planet}")
        ships = planet.num_ships
        planet_ships[planet] = planet_ships[planet] + ships
        logging.info(f"{planet.ID} {planet_ships[planet]}")
    if (planet_ships.values() == []) or (len(state.my_planets()) == 0):
       logging.info("exception in weak planets")
       return True
    return min(ships for ships in planet_ships.values()) <= (total_planet_ships/len(state.my_planets()) * 0.7) #70% of average
   

'''def if_weak_enemy_planet_available(state): #currently at 10%
    
    # (2) Find total ships
    total_planet_ships = sum(planet.num_ships for planet in state.my_planets())
    logging.info(f"total_planet_ships: {total_planet_ships}")
    
    ID_to_planet = {}
    for planet in state.enemy_planets(): 
        ID_to_planet[planet.ID] = (planet, planet.num_ships)
    
    remove_these_planets = set()

    for id, (n_planet, ships) in ID_to_planet.items():
        logging.info(f"id:{id} {n_planet} {ships}")
        logging.info(f"planet: {n_planet}")
        logging.info(f"ships: {ships}")
        for my_fleet in state.my_fleets():
            if my_fleet.destination_planet == id:
                if ships - my_fleet.num_ships <= 0:
                    logging.info(f"ships {ships}")
                    logging.info(f"fleet attacking ships {my_fleet.num_ships}")
                    logging.info("remove this planet")
                    remove_these_planets.add(id) #get rid of planets we already sent enough fleets to
                else:
                    ID_to_planet[id] = (planet, ships - my_fleet.num_ships)
    
    for id in remove_these_planets:
        ID_to_planet.pop(id)
    
    if ID_to_planet == {}:
        return False

    weakest_planet = None
    smallest_ship_count = 100000

    logging.info(f"{ID_to_planet}")

    for planet, ships in ID_to_planet.values():
        logging.info(f"planet {planet} ships {ships}")
        logging.info(f"ships {ships}")
        if ships < smallest_ship_count:
            weakest_planet = planet
            smallest_ship_count = ships
            logging.info(f"new weakest planet {weakest_planet}")
    logging.info(f"weakest planet {weakest_planet}")
    #calculate what percent of ships each planet needs to send and add 3 percent
    return weakest_planet.num_ships < total_planet_ships * 0.1'''


'''def if_weak_enemy_planet_available(state): #currently at 10%
    total_planet_ships = sum(planet.num_ships for planet in state.my_planets()) \
      + sum(fleet.num_ships for fleet in state.my_fleets())
    planet_ships = {}
    for planet in state.enemy_planets():
      planet_ships[planet] = planet.num_ships #planet -> ships defending it
    for fleet in state.my_fleets():
        if fleet.destination_planet in state.enemy_planets():
          planet_ships[fleet.destination_planet] -= fleet.num_ships
    
    open_planets = []
    for planet in planet_ships.keys():
       if planet_ships[planet] > 0:
          open_planets.append(planet)
    if (open_planets == []) or (len(state.enemy_planets()) == 0):
       logging.info("no enemy planets left")
       return False
    return min(planet.num_ships for planet in open_planets) <= (total_planet_ships * 0.1) #10% of all my planet ships
   '''

'''def if_weak_enemy_planet_available(state): #currently at 10%
    total_planet_ships = sum(planet.num_ships for planet in state.my_planets())
    if total_planet_ships <= 1:
       total_planet_ships = 1
    weakest_enemy_ships = min(planet.num_ships for planet in state.enemy_planets())
    if weakest_enemy_ships/total_planet_ships <= 0.04: #less than or equal to 20% of total ships
      return True
    else:
       return False'''


'''if not weakest_planet:
        # No legal destination
        return False'''