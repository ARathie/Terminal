import gamelib
import random
import math
from sys import maxsize


'''
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
'''

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()

    def on_game_start(self, config):
        '''
        Read in config and perform any initial setup here
        '''
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]

    def on_turn(self, cmd):
        '''
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        '''
        game_state = gamelib.GameState(self.config, cmd)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))

        self.starter_strategy(game_state)

        game_state.submit_turn()

    '''
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safey be replaced for your custom algo.
    '''
    def starter_strategy(self, game_state):

        if game_state.turn_number == 0:
            self.turn_one_defences(game_state) # implement
            self.deploy_attackers2(game_state) # implement
        else:
            self.build_defences2(game_state) # implement
            self.deploy_attackers2(game_state) # implement



    def turn_one_defences(self, game_state):

        tower_locations = [[3, 13], [24, 13], [1, 12], [10, 13], [17, 13]]
        game_state.attempt_spawn(DESTRUCTOR, tower_locations)


        tower_locations = [[1, 13], [5, 13], [7, 13], [23, 13], [13, 2], [11, 3]]
        game_state.attempt_spawn(FILTER, tower_locations)


        tower_locations = [[22, 13], [13, 13], [15, 13], [9, 13], [11, 13], [19, 13], [12, 3]]
        game_state.attempt_spawn(FILTER, tower_locations)

    def build_defences2(self, game_state):

        future_destructors1 = [[21, 13], [14, 13], [6, 13], [26, 12], [19, 12], [12, 12], [6, 12], [4, 11], [2, 12], [22, 12], [21, 11], [25, 11]]
        future_destructors2 = [[17, 12], [8, 12], [15, 12], [3, 12], [10, 12], [2, 12], [22, 12], [21, 12], [4, 12], [5, 12]]

        future_encryptors1 = [[23, 12], [22, 11], [21, 10], [20, 9], [19, 8], [18, 7], [17, 6], [16, 5], [15, 4], [14, 3]]
        future_encryptors2 = [[24, 10], [23, 9], [22, 8], [21, 7], [20, 6], [19, 5], [18, 4], [17, 3], [16, 2], [15, 1], [14, 0]]

        for starting_DF in [[3, 13], [24, 13], [1, 12], [10, 13], [17, 13]]:
            game_state.attempt_spawn(DESTRUCTOR, starting_DF)

        for starting_FF1 in [[1, 13], [5, 13], [7, 13], [23, 13], [13, 2], [11, 3]]:
            game_state.attempt_spawn(FILTER, starting_FF1)

        for starting_FF2 in [[22, 13], [13, 13], [15, 13], [9, 13], [11, 13], [19, 13], [12, 3]]:
            game_state.attempt_spawn(FILTER, starting_FF2)

        if (game_state.turn_number % 3 != 0) or (game_state.turn_number == 0):
            for my_location in future_destructors1:
                game_state.attempt_spawn(DESTRUCTOR, my_location)

        elif (game_state.turn_number % 3 == 0):
            for my_location in future_encryptors1:
                game_state.attempt_spawn(ENCRYPTOR, my_location)
            for my_location in future_encryptors2:
                game_state.attempt_spawn(ENCRYPTOR, my_location)


        for starting_FF3 in [[0, 13], [2, 13], [4, 13], [8, 13], [12, 13], [16, 13], [18, 13], [20, 13]]:
            game_state.attempt_spawn(FILTER, starting_FF3)


        for my_location in future_destructors2:
            game_state.attempt_spawn(DESTRUCTOR, my_location)
        for my_location in future_encryptors1:
            game_state.attempt_spawn(ENCRYPTOR, my_location)
        for my_location in future_encryptors2:
            game_state.attempt_spawn(ENCRYPTOR, my_location)


    def deploy_attackers2(self, game_state):

        if game_state.turn_number % 3 != 0 and game_state.turn_number > 15:

            game_state.attempt_spawn(EMP, [11, 2])
            game_state.attempt_spawn(EMP, [11, 2])

            # game_state.attempt_spawn(SCRAMBLER, [13, 0])

            for i in range(30):
                game_state.attempt_spawn(PING, [13, 0])

        else:
            for i in range(35):
                game_state.attempt_spawn(PING, [13, 0])





if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
