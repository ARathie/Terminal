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
        # state variables
        self.useShockTroops = True
        self.attackedLastTurn = False
        self.lastEnemyHealth = 30

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
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        #always try to build walls
        self.buildWalls(game_state)

        if self.attackedLastTurn and game_state.enemy_health == self.lastEnemyHealth:
            #our last attack was not successful! change strategies
            self.useShockTroops = not self.useShockTroops
            gamelib.debug_write('our last attack was not successful! Changing strategies.')
            self.attackedLastTurn = False
        elif self.attackedLastTurn:
            gamelib.debug_write('Our last attacked worked!  We did {} damage'.format(self.lastEnemyHealth - game_state.enemy_health))
            self.lastEnemyHealth = game_state.enemy_health
            self.attackedLastTurn = False

        #if shock troops aren't successful, go with the bruisers
        if game_state.get_resource(game_state.BITS) >= 12:
            self.attackedLastTurn = True
            if self.useShockTroops:
                self.deployShockTroops(game_state)
            else:
                self.deployBruisers(game_state)

        game_state.submit_turn()

    def deployBruisers(self, game_state):
        gamelib.debug_write('Sending Bruisers!')
        for x in range(3):
            game_state.attempt_spawn(EMP, [3,10])
        while game_state.can_spawn(PING, [3, 10]):
            game_state.attempt_spawn(SCRAMBLER, [3,10])

    def deployShockTroops(self, game_state):
        gamelib.debug_write('Sending Shock Troops!')
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
