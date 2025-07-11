import logging

def if_neutral_planet_available(state):
    return any(state.neutral_planets())

def if_weak_neutral_planet_available(state): #currently at 10%
    if if_neutral_planet_available(state):
      total_planet_ships = sum(planet.num_ships for planet in state.my_planets())
      weakest_neutral_ships = min(planet.num_ships for planet in state.neutral_planets())
      if weakest_neutral_ships/total_planet_ships <= 0.5: #less than or equal to 10% of total ships
        return True
      else:
         return False
    else:
        False

def if_weak_owned_planet(state):
    total_planet_ships = sum(planet.num_ships for planet in state.my_planets())
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
        logging.info(f"{state.my_planets()}")
    if (planet_ships.values() == []) or (len(state.my_planets()) == 0):
       logging.info("exception in weak planets")
       return True
    return min(ships for ships in planet_ships.values()) <= (total_planet_ships/len(state.my_planets()) * 0.8) #80% of average
   

def if_weak_enemy_planet_available(state): #currently at 10%
    total_planet_ships = sum(planet.num_ships for planet in state.my_planets())
    if total_planet_ships <= 1:
       total_planet_ships = 1
    weakest_enemy_ships = min(planet.num_ships for planet in state.enemy_planets())
    if weakest_enemy_ships/total_planet_ships <= 0.04: #less than or equal to 20% of total ships
      return True
    else:
       return False

def have_highest_growth(state): # checks if I get more ships per turn than opponent
    return sum(planet.growth_rate for planet in state.my_planets()) \
           > sum(planet.growth_rate for planet in state.enemy_planets()) \
           
def my_plant_vulnerable(state): #determine if one of my planets could be taken over by current enemy fleet
    return min(planet.num_ships for planet in state.my_planets()) \
            + sum(fleet.num_ships for fleet in state.my_fleets()) \
          > sum(fleet.num_ships for fleet in state.enemy_fleets())

def dont_have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           < sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets()) + 5

'''if not weakest_planet:
        # No legal destination
        return False'''