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
        self.troopDeploymentCoords = [13,0]

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        super().on_game_start(config)
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
        game_state = gamelib.AdvancedGameState(self.config, turn_state)
        #p1UnitCount = len(self.jsonState.get('p1Units')[0])
        p2UnitCount = len(self.jsonState.get('p2Units')[0]) + len(self.jsonState.get('p2Units')[1]) + len(self.jsonState.get('p2Units')[2])
        gamelib.debug_write('p2 has {} units'.format(p2UnitCount))
        
        self.reinforceBreachLocation(game_state)

        # line detection #
        # only worry about mirror if we have good defense set up?
        firstRowDefenderCount = game_state.get_enemy_unit_count_for_row(game_state.game_map.FIRST_ENEMY_ROW)
        secondRowDefenderCount = game_state.get_enemy_unit_count_for_row(game_state.game_map.SECOND_ENEMY_ROW)
        thirdRowDefenderCount = game_state.get_enemy_unit_count_for_row(game_state.game_map.THIRD_ENEMY_ROW)
        fourthRowDefenderCount = game_state.get_enemy_unit_count_for_row(game_state.game_map.FOURTH_ENEMY_ROW)
        gamelib.debug_write('row counts: {},{},{},{}'.format(firstRowDefenderCount, secondRowDefenderCount, thirdRowDefenderCount, fourthRowDefenderCount))

        if firstRowDefenderCount > 8:
            self.mirrorEnemy(game_state, game_state.game_map.FIRST_ENEMY_ROW)
        elif secondRowDefenderCount > 6:
            self.mirrorEnemy(game_state, game_state.game_map.SECOND_ENEMY_ROW)
        elif thirdRowDefenderCount > 6:
            self.mirrorEnemy(game_state, game_state.game_map.THIRD_ENEMY_ROW)
        elif fourthRowDefenderCount > 6:
            self.mirrorEnemy(game_state, game_state.game_map.FOURTH_ENEMY_ROW)

        # make sure we haven't blocked ourselves in
        for x in range(4):
            openSpots = game_state.row_openings(13 - x)
            if openSpots == 0:
                # open it back up!
                game_state.attempt_remove([20, 13 - x])

        if game_state.turn_number != 0:
            if p2UnitCount < 8:
                self.attackForMaxPain(game_state)
            else:
                self.attackForMaxDestruction(game_state)
            
        game_state.submit_turn()

    def mirrorEnemy(self, game_state, row_description):
        for location in game_state.game_map.get_row_locations(row_description):
            for unit in game_state.game_map[location]:
                x, y = location
                openSpots = game_state.row_openings(y - 4)
                if openSpots > 2:
                    if x % 2 == 0 and game_state.can_spawn(DESTRUCTOR, [x, y - 4]):
                        game_state.attempt_spawn(DESTRUCTOR, [x, y - 4])
                    elif game_state.can_spawn(FILTER, [x, y - 4]):
                        game_state.attempt_spawn(FILTER, [x, y - 4])

    def reinforceBreachLocation(self, game_state):
        for breach in self.breach_list:
            gamelib.debug_write("They got through our defenses!")
            for x in range(3):
                for location in game_state.game_map.get_locations_in_range(breach, x):
                    x, y = location
                    for unit in game_state.game_map[x,y]:
                        if unit.stability < 35:
                            game_state.attempt_remove(location)
                    if game_state.can_spawn(DESTRUCTOR, location):
                        game_state.attempt_spawn(DESTRUCTOR, location)

    def attackForMaxPain(self, game_state):
        deployLocation = [13, 0]
        lowestPathRisk = 10
        
        for startLocation in game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT):
            if game_state.can_spawn(PING, startLocation) and len(game_state.get_attackers(startLocation, 0)) == 0:
                path = game_state.find_path_to_edge(startLocation, game_state.game_map.TOP_RIGHT)
                pathRisk = 0
                for step in path:
                    pathRisk =+ len(game_state.get_attackers(step, 0))
                
                if pathRisk < lowestPathRisk:
                    lowestPathRisk = pathRisk
                    deployLocation = startLocation

        for startLocation in game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT):
            if game_state.can_spawn(PING, startLocation) and len(game_state.get_attackers(startLocation, 0)) == 0:
                path = game_state.find_path_to_edge(startLocation, game_state.game_map.TOP_LEFT)
                pathRisk = 0
                for step in path:
                    pathRisk =+ len(game_state.get_attackers(step, 0))
                
                if pathRisk < lowestPathRisk:
                    lowestPathRisk = pathRisk
                    deployLocation = startLocation

        gamelib.debug_write('Lowest risk path value = {}'.format(lowestPathRisk))

        while game_state.can_spawn(PING, deployLocation):
            game_state.attempt_spawn(PING, deployLocation)

    def attackForMaxDestruction(self, game_state):
        deployLocation = [13, 0]
        bestPathValue = 0
        targetEdge = game_state.game_map.TOP_RIGHT

        # don't want to start in range of a destructor
        for startLocation in game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT):
            if game_state.can_spawn(EMP, startLocation) and len(game_state.get_attackers(startLocation, 0)) == 0:
                path = game_state.find_path_to_edge(startLocation, game_state.game_map.TOP_RIGHT)
                #pathValue = game_state.get_target_count_for_EMP_locations(path) - game_state.get_attacker_count_for_locations(path)
                pathValue = game_state.get_free_target_count_for_EMP_locations(path)
                if pathValue > bestPathValue:
                    bestPathValue = pathValue
                    deployLocation = startLocation
                    targetEdge = game_state.game_map.TOP_RIGHT
        for startLocation in game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT):
            if game_state.can_spawn(EMP, startLocation) and len(game_state.get_attackers(startLocation, 0)) == 0:
                path = game_state.find_path_to_edge(startLocation, game_state.game_map.TOP_LEFT)
                #pathValue = game_state.get_target_count_for_EMP_locations(path) - game_state.get_attacker_count_for_locations(path)
                pathValue = game_state.get_free_target_count_for_EMP_locations(path)
                if pathValue > bestPathValue:
                    bestPathValue = pathValue
                    deployLocation = startLocation
                    targetEdge = game_state.game_map.TOP_LEFT

        gamelib.debug_write('Best path value = {}'.format(bestPathValue))

        
        if game_state.number_affordable(EMP) > 2:
            path = game_state.find_path_to_edge(deployLocation, targetEdge)
            if path[len(path) - 1] in game_state.game_map.get_edge_locations(targetEdge):
                ''' # ENCRYPTORs have not been useful yet
                if game_state.number_affordable(ENCRYPTOR) > 0:
                    # find a good place to put it!
                    encryptorPlaced = False
                    for step in game_state.find_path_to_edge(deployLocation, targetEdge):
                        x, y = step
                        if y == 13 and not encryptorPlaced:
                            if game_state.can_spawn(ENCRYPTOR, [x-1,y]):
                                game_state.attempt_spawn(ENCRYPTOR, [x-1,y])
                                encryptorPlaced = True
                            elif game_state.can_spawn(ENCRYPTOR, [x+1,y]):
                                game_state.attempt_spawn(ENCRYPTOR, [x+1,y])
                                encryptorPlaced = True
                            else:
                                gamelib.debug_write('Wanted to spawn encryptor but could not find suitable location!')
                '''

                while game_state.can_spawn(EMP, deployLocation):
                    game_state.attempt_spawn(EMP, deployLocation)
            else:
                gamelib.debug_write('No path to the enemy edge, NOT DEPLOYING TROOPS')

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
