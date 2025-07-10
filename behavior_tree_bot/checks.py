

def if_neutral_planet_available(state):
    return any(state.neutral_planets())

def have_highest_growth(state): # checks if I get more ships per turn than opponent
    return sum(planet.growth_rate for planet in state.my_planets()) \
           > sum(planet.growth_rate for planet in state.enemy_planets()) \
           
def my_plant_vulnerable(state): #determine if one of my planets could be taken over by current enemy fleet
    return min(planet.num_ships for planet in state.my_planets()) \
            + sum(fleet.num_ships for fleet in state.my_fleets()) \
          > sum(fleet.num_ships for fleet in state.enemy_fleets())

def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())
