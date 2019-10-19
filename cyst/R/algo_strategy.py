import gamelib
import random
import math
import warnings
from sys import maxsize

"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

Additional functions are made available by importing the AdvancedGameState 
class from gamelib/advanced.py as a replcement for the regular GameState class 
in game.py.

You can analyze action frames by modifying algocore.py.

The GameState.map object can be manually manipulated to create hypothetical 
board states. Though, we recommended making a copy of the map to preserve 
the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]


    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        gamelib.debug_write('{} to build defenses with'.format(game_state.get_resource(game_state.CORES)))
        gamelib.debug_write('{} to build army with'.format(game_state.get_resource(game_state.BITS)))
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        #always try to build walls
        self.buildWalls(game_state)

        if game_state.get_resource(game_state.BITS) >= 12:
            self.deployShockTroops(game_state)

        game_state.submit_turn()

    #def deployBruisers(self, game_state):

    def deployShockTroops(self, game_state):
        while game_state.can_spawn(PING, [3, 10]):
            game_state.attempt_spawn(PING, [3,10])

    def buildWalls(self, game_state):    
        firewall_locations_part1 = [[0, 13], [1, 13], [2, 13], [3, 13], [4, 13], [5, 13], [6, 13], 
                                    [7, 13], [8, 13], [9, 13], [10, 13], [11, 13], [12, 13], [13, 13],
                                    [14, 13], [15, 13], [16, 13], [17, 13], [18, 13], [19, 13], [20, 13], [21, 13]]
        for location in firewall_locations_part1:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
        
        tower_locations_part1 = [[24, 12], [21, 12], [26, 12]]
        for location in tower_locations_part1:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)

        firewall_locations_part2 = [[22, 13], [23, 13]]
        for location in firewall_locations_part2:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)

        tower_locations_part2 = [[23, 12], [22, 12], [20, 12], [19, 12], [18, 12]]
        for location in tower_locations_part2:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)

    

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
