import gamelib
import random
import math
import warnings
import json
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
    
def flipArray(array, flip):
    if flip == False:
        return array
    newArray = []
    for i in array:
        newArray.append([27-i[0], i[1]])
    return newArray



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
        self.prevHealth = 30
        self.flip = False
        self.futureFlip = False
        self.currentSide = 0
        self.PINGattack = True
        self.EMPattack = False
        self.DesM = False
        self.DesL = False
        self.DesR = False
        self.midDesR = False
        self.targetsL = 0
        self.targetsR = 0
        self.saveUp = False
        self.deployed = False
        self.deployed2 = False
        self.missingForSwitch = 0
        self.attackedLPrev = False
        self.attackedRPrev = False
        self.largeAttackOption = False
        self.pingRushL = False
        self.pingRushR = False
        self.opposingEMP = 0

        self._1Fil = [[ 1, 13],[3,13], [ 11, 10]]
        self._1Des = [[ 2, 13],[ 9, 9]]
        
        self._1Enc = [[ 8, 7]]
        self._2Enc = [[ 9, 7]]
        self._3Enc = [[6, 7], [7, 7], [5, 8]]

        self.AttFil = [[3,12], [4, 11]]
        self.Att2Fil = [[6,11],[7,11],[8,11]]
        self.Att3Fil = [[9,12],[10,12]]
        
        self.edge = [[0, 13]]
        self.edge2 = [[3, 10],[4, 9],[5, 9],[6, 9]]
        self.edgeDes = [[2, 12]]
        self.edgeFil = [[1, 13]]

        self._2Fil = [[11, 12]]
        self._2Des = [[12, 12]]
        self._2Set = [[12, 12],[11, 12]]

        self._MSet = [[13,12],[13,13],[14,12],[14,13]]

        self._3Fil = [[ 6, 11]]
        self._3Des = [[ 5, 11]]
        self._3Set = [[ 5, 11], [6, 11]]

        self._4Des = [[ 12, 12]]
        self._4Fil = [[12,13]]
        self._4Set = [[12, 12],[12,13]]

        self._5Des = [[2, 12]]
        self._5Fil = [[4,13]]
        self._5Set = [[2, 12],[4,13]]

        self._6Des = [[6, 12]]
        self._6Fil = [[6,13]]
        self._6Set = [[6, 12],[6,13]]

        self._7Des = [[11,12]]
        self._7Fil = [[12,13]]
        self._7Set = [[11,12],[12,13]]

        self._8Des = [[7, 13]]
        self._8Fil = [[8,13]]
        self._8Set = [[7, 13],[8,13]]

        self._9Des = [[1, 12]]
        self._10Ses = [[12, 13],[11, 13]]

        self.rail = [[7,7],[8,8]]
        self.edgeHoopla = [[5, 10]]
        self.hoopla = [[10, 11]]

        self.gate = [[3, 12]]
        self.rank = [[11, 11]]
        
        self.flank = [[1,14],[2,15],[3,16]]
        self.flank2 = [[2,16],[3,15]]
        self.peekHole = [[15,12]]

        self.haasjeOver = [[6,9],[7,7]]
        self.haasjeOverExcl = [[ 5, 10],[ 6, 10],[ 5, 9],[ 5, 8],[ 6, 8],[ 6, 7]]

        self.pingRushFlank = [[3, 10], [4, 9],[5,10]]

        self.initExclusionList = [[0,0]]
        self.exclusionList = [[0,0]]

    def on_frame(self, turn_state):
        state = json.loads(turn_state)
        turnInfo = state["turnInfo"] 
        if turnInfo[2] == 1:
            p2units = state["p2Units"]
            for unit in p2units[4]:
                if (unit[0] <= 13 and not self.flip) or (unit[0] >= 14 and self.flip): 
                    self.opposingEMP += 2

 


    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        #gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        self.starter_strategy(game_state)

        game_state.submit_turn()

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safey be replaced for your custom algo.
    """

    def starter_strategy(self, game_state):

        self.exclusionList = self.initExclusionList.copy()
        self.PINGattack = False
        self.EMPattack = False
        self.saveUp = False



        if game_state.turn_number == 0:
            self.deploy(game_state, self._1Des, DESTRUCTOR,         flip =      self.flip)
            self.deploy(game_state, self._1Fil, FILTER,             flip =      self.flip)
            self.deploy(game_state, self._1Des, DESTRUCTOR,         flip = not  self.flip)
            self.deploy(game_state, self._1Fil, FILTER,             flip = not  self.flip)
            return

        self.analyze(game_state)

        if self.pingRushL:
            self.pingRushDefense(game_state, False)
        if self.pingRushR:
            self.pingRushDefense(game_state, True)

        self.deploy_attackers(game_state)
        self.buildFirewalls(game_state)

        if self.opposingEMP > 3:
            gamelib.debug_write('Fighting against EMP line, turn {}'.format(game_state.turn_number))
 
        if ((self.targetsL <= 4 and not self.flip) or (self.targetsR <= 4 and self.flip)) and self.deployed2:
            self.opposingEMP -= 2

        self.opposingEMP -= 1
        if self.opposingEMP > 6:
            self.opposingEMP = 6
        if self.opposingEMP < 0:
            self.opposingEMP = 0



        if self.EMPattack or self.PINGattack:
            self.remove(game_state, [self.Att3Fil[1]], flip =      self.flip)
            self.remove(game_state, [self.Att3Fil[1]], flip = not  self.flip)

    def buildFirewalls(self, game_state):
        self.remove(game_state, self.gate, flip = not self.flip)
        if self.EMPattack:
            self.exclusionList.extend(flipArray(self.gate, flip = not self.flip))
        #gamelib.debug_write('exclude {}, turn {}'.format(self.exclusionList, game_state.turn_number))

        if self.opposingEMP > 4:
            self.deploy(game_state, self._1Des, FILTER,         flip =      self.flip)
        else:
            self.deploy(game_state, self._1Des, DESTRUCTOR,         flip =      self.flip)
        self.deploy(game_state, self._1Fil, FILTER,             flip =      self.flip)


        if self.DesM == True and self.EMPattack and self.deployed:
            self.deploy(game_state, self.hoopla, FILTER,        flip =      self.flip)
            self.deploy(game_state, [self.rail[1]], FILTER,        flip =      self.flip)
            self.deploy(game_state, self.hoopla, FILTER,        flip = not  self.flip)
        elif not self.DesM:
            self.remove(game_state, self.hoopla,                flip =      self.flip)
            self.remove(game_state, self.hoopla,                flip = not  self.flip)

        if self.deployed:
            self.deploy(game_state, [self.rail[1]], FILTER,        flip =      self.flip)

        if self.EMPattack == True:
            if (self.flip == False and self.DesL) or (self.flip == True and self.DesR):
                self.deploy(game_state, self.edgeHoopla, FILTER, flip =      self.flip)
            else:
                self.deploySet(game_state, self._3Set,         flip =  self.flip)
            self.deploy(game_state, self.AttFil, FILTER,         flip =      self.flip)

            if (self.opposingEMP > 4) and not self.flip:
                self.deploy(game_state, self._1Enc, ENCRYPTOR,        flip = False)
                if (self.enemyEncL > 0):
                    self.deploy(game_state, self._2Enc, ENCRYPTOR,        flip = False)
                if (self.enemyEncL > 1):
                    self.deploy(game_state, [self._3Enc[0]], ENCRYPTOR,        flip = False)
                if (self.enemyEncL > 2):
                    self.deploy(game_state, [self._3Enc[1]], ENCRYPTOR,        flip = False)

            if (self.opposingEMP > 4) and self.flip:
                self.deploy(game_state, self._1Enc, ENCRYPTOR,        flip = True)
                if (self.enemyEncR > 0):
                    self.deploy(game_state, self._2Enc, ENCRYPTOR,        flip = True)
                if (self.enemyEncR > 1):
                    self.deploy(game_state, [self._3Enc[0]], ENCRYPTOR,        flip = True)
                if (self.enemyEncR > 2):
                    self.deploy(game_state, [self._3Enc[1]], ENCRYPTOR,        flip = True)
 
            self.deploy(game_state, self.Att2Fil, FILTER,         flip =      self.flip)
            self.deploy(game_state, self.edge, FILTER,             flip =      self.flip)

        self.deploy(game_state, self._1Des, DESTRUCTOR,         flip = not  self.flip)
        self.deploy(game_state, self._1Fil, FILTER,             flip = not  self.flip)




        if self.deployed2 == True:
            if self.EMPattack == False and self.PINGattack == False:
                self.deploy(game_state, self.gate, FILTER,             flip = not self.flip)
                self.deploy(game_state, self.gate, FILTER,             flip =     self.flip)
            self.remove(game_state, self.gate, flip = self.flip)
            self.remove(game_state, self.gate, flip = not self.flip)

        self.deploySet(game_state, self._3Set,         flip =  self.flip)
        self.deploySet(game_state, self._3Set,         flip = not  self.flip)


        self.deploy(game_state, self.edge, FILTER,             flip =      self.flip)
        self.deploy(game_state, self.edge, FILTER,             flip = not  self.flip)

        self.repairCycle(game_state)


        self.deploySet(game_state, self._MSet,              flip =   self.flip)

        if self.EMPattack:
            self.deploy(game_state, self.Att3Fil, FILTER,         flip =      self.flip)

        self.deploy(game_state, self._2Fil, FILTER,         flip =   self.flip)
        self.deploySet(game_state, self._2Set,              flip =   self.flip)
        self.deploy(game_state, self.AttFil, FILTER,        flip =   self.flip)

        if self.EMPattack == False and self.PINGattack == False and not self.deployed2:
            self.deploy(game_state, self.AttFil, FILTER,        flip = not  self.flip)
            self.remove(game_state, self.gate, flip = not self.flip)
            return

        if self.saveUp == False and self.deployed == False:
            self.deployed = True 
            gamelib.debug_write('Deployed!, turn {}'.format(game_state.turn_number))

        self.deploySet(game_state, self._2Set,         flip = not  self.flip)
        self.deploySet(game_state, self._5Set,         flip = not  self.flip)

        self.deploy(game_state, self.AttFil, FILTER,         flip = not  self.flip)
        self.deploy(game_state, self.Att2Fil, FILTER,         flip = not  self.flip)
        self.deploy(game_state, self.Att3Fil, FILTER,         flip = not  self.flip)

        self.deploy(game_state, self.rail, FILTER,           flip = not  self.flip)
        if self.saveUp == False and self.deployed2 == False:
            self.deployed2 = True 
            gamelib.debug_write('Fully deployed!, turn {}'.format(game_state.turn_number))


        self.deploy(game_state, self.edgeHoopla, FILTER, flip = self.flip)
        self.deploy(game_state, self.edgeHoopla, FILTER, flip = not self.flip)

        self.deploySet(game_state, self._3Set,         flip =  self.flip)
        self.deploySet(game_state, self._6Set,         flip =  not self.flip)
        self.deploySet(game_state, self._5Set,         flip =  self.flip)
        self.deploySet(game_state, self._6Set,         flip =  self.flip)

        self.deploySet(game_state, self._10Ses, flip = not  self.flip)
        self.deploySet(game_state, self._10Ses, flip =      self.flip)

        self.deploy(game_state, self._2Enc, ENCRYPTOR,        flip = self.flip)
        self.deploy(game_state, self._2Enc, ENCRYPTOR,        flip = not self.flip)

        self.deploy(game_state, self._1Enc, ENCRYPTOR,        flip = self.flip)
        self.deploy(game_state, self._1Enc, ENCRYPTOR,        flip = not self.flip)

        self.deploySet(game_state, self._8Set,         flip = not self.flip)
        self.deploySet(game_state, self._8Set,         flip = self.flip)

        self.deploy(game_state, self._9Des, DESTRUCTOR,         flip = not  self.flip)
        self.deploy(game_state, self._9Des, DESTRUCTOR,         flip =      self.flip)

        self.deploy(game_state, self._3Enc, ENCRYPTOR,        flip = not self.flip)
        self.deploy(game_state, self._3Enc, ENCRYPTOR,        flip = self.flip)

        self.remove(game_state, self.gate, flip = not self.flip)

    def pingRushDefense(self, game_state, flip = True):
        Loc0 = flipArray([[0,13]], flip)
        Loc1 = flipArray([[1,13]], flip)
        Loc2 = flipArray([[2,13]], flip)
        Loc3 = flipArray([[3,13]], flip)

        self.deploy(game_state, Loc0, FILTER)
        self.deploy(game_state, Loc1, FILTER)
        self.deploy(game_state, Loc2, FILTER)
        self.deploy(game_state, Loc3, DESTRUCTOR)

        if game_state.contains_stationary_unit(Loc3[0]):
            unit = game_state.game_map[Loc3[0]][0]
            if unit.unit_type == FILTER:
                self.remove(game_state, Loc3)
        
        self.deploy(game_state, self._9Des, DESTRUCTOR, flip = flip)
        self.deploy(game_state, self._5Set, DESTRUCTOR, flip = flip)
        return
        


    def analyze(self, game_state):
        self.targetsL = 0
        self.targetsR = 0
        self.enemyEncL = 0
        self.enemyEncR = 0
        totalL = 0
        totalR = 0

        if self.opposingEMP < 2:
            if self.checkMissing(game_state, [[1,13]]) > 0 and game_state.turn_number > 1 and not self.pingRushL:
                if self.checkMissing(game_state, [[1,14],[2,15],[3,16]], flip = False) == 3 and self.checkMissing(game_state, [[2,14],[1,15]], flip = False) > 0:
                    self.pingRushL = True
                    gamelib.debug_write('PINGRUSH L, turn{}'.format(game_state.turn_number))
            if self.checkMissing(game_state, [[26,13]]) > 0 and game_state.turn_number > 1 and not self.pingRushR:
                if self.checkMissing(game_state, [[1,14],[2,15],[3,16]], flip = True) == 3 and self.checkMissing(game_state, [[2,14],[1,15]], flip = True) > 0:
                    self.pingRushR = True
                    gamelib.debug_write('PINGRUSH R, turn{}'.format(game_state.turn_number))

        firewall_locations = game_state.game_map.get_all_enemy_firewall_locations()
        for location in firewall_locations:
            unit = game_state.game_map[location][0]
            if unit.x >= 14:
                if unit.unit_type == ENCRYPTOR and unit.x >= 16 and unit.y <= 19:
                    self.enemyEncR += 1
                    totalR += 2
                else:
                    totalR += 1
            else:
                if unit.unit_type == ENCRYPTOR and unit.x <= 11 and unit.y <= 19:
                    self.enemyEncL += 1
                    totalL += 2
                else:
                    totalL += 1
            if unit.y < 17:
                if unit.x <= 13 and ((unit.x >= 7 and unit.y <= 16) or (unit.x >= 3 and unit.y <= 14)):
                    self.targetsL += 1 
                    if unit.unit_type == DESTRUCTOR:
                        self.targetsL += 1
                    if unit.unit_type == ENCRYPTOR:
                        self.targetsL += 2
                if unit.x >= 14  and ((unit.x <= 22 and unit.y <= 16) or (unit.x <= 24 and unit.y <= 14)):
                    self.targetsR += 1
                    if unit.unit_type == DESTRUCTOR:
                        self.targetsR += 1
                    if unit.unit_type == ENCRYPTOR:
                        self.targetsR += 2


        if game_state.turn_number == 1:
            gamelib.debug_write('targetL={} targetsR={}, turn{}'.format(self.targetsL, self.targetsR, game_state.turn_number))
            if abs(self.targetsR-self.targetsL) < 3:
                if totalR > totalL:
                    self.flip = True
                else:
                    self.flip = False
            else:
                if self.targetsR > self.targetsL:
                    self.flip = True
                else:
                    self.flip = False

        bits_me = game_state.get_resource(game_state.BITS,0)

        if self.deployed == True and bits_me >= 7 and self.opposingEMP < 1:
            if self.targetsL >= self.targetsR+6 and self.targetsR < 8:
                self.flip = False
            elif self.targetsR >= self.targetsL+6 and self.targetsL < 8:
                self.flip = True

        #self.DesL = False
        self.DesM = False
        #self.DesR = False

        if game_state.turn_number == 0:
            return

        firewall_locations = game_state.game_map.get_all_enemy_firewall_locations()
        for location in firewall_locations:
            unit = game_state.game_map[location][0]
            if unit.y == 14 and unit.unit_type == DESTRUCTOR:
                if unit.x >= 1 and unit.x <= 4:
                    if self.DesL == False:
                        self.DesL = True
                        gamelib.debug_write('avoidL, turn{}'.format(game_state.turn_number))
                if unit.x >= 8 and unit.x <= 19:
                    self.DesM = True
                if unit.x >= 23 and unit.x <= 26:
                    if self.DesR == False:
                        self.DesR = True
                        gamelib.debug_write('avoidR, turn{}'.format(game_state.turn_number))

        if not self.flip and self.opposingEMP > 4:
            self.DesL = True
        if self.flip and self.opposingEMP > 4:
            self.DesR = True

    def repairCycle(self, game_state):
        # patch up vulnerable edge
        if self.opposingEMP < 2:
            if game_state.contains_stationary_unit([3,13]):
                unit = game_state.game_map[3, 13][0]
                if unit.stability < 45:
                    self.deploy(game_state, [[4, 13]], FILTER, flip = False)
            else:
                self.deploy(game_state, [[4, 13]], FILTER, flip = False)

            if game_state.contains_stationary_unit([24,13]):
                unit = game_state.game_map[24, 13][0]
                if unit.stability < 45:
                    self.deploy(game_state, [[23, 13]], FILTER, flip = False)
            else:
                self.deploy(game_state, [[23, 13]], FILTER, flip = False)


        counter = 2;
        firewall_locations = game_state.game_map.get_all_firewall_locations()
        for location in firewall_locations:
            unit = game_state.game_map[location][0]
            if (unit.stability < 30 and unit.unit_type == FILTER):
                if game_state.contains_stationary_unit(location):
                    game_state.attempt_remove(location)
                    counter -= 1
                    if counter == 0:
                        break    

    def deploy_attackers(self, game_state, flip = False):

        DEF_S = flipArray([[10,3]], self.flip)
        DEF2_S = flipArray([[14,0]], self.flip)
        RUSH_S = flipArray([[2,11]], self.flip)

        if (self.flip == False and self.DesL) or (self.flip == True and self.DesR):
            EMP_S = flipArray([[3,10]], self.flip)
            SCR_S = flipArray([[4,9]], self.flip)
        else:
            EMP_S = flipArray([[2,11]], self.flip)
            SCR_S = flipArray([[3,10]], self.flip)

        bits_me = game_state.get_resource(game_state.BITS,0)
        bits_he = game_state.get_resource(game_state.BITS,1)

       
        # ping attack?

        damage_LB = self.checkReceivedDamage(game_state, [4,9], 1000 ,0) # 0 is top right, 1 is top legft
        steps_LB = len(game_state.find_path_to_edge([4,9], 0))

        damage_LM = self.checkReceivedDamage(game_state, [9,4], 1000 ,0) # 0 is top right, 1 is top legft
        steps_LM = len(game_state.find_path_to_edge([9,4], 0))
        
        damage_RB = self.checkReceivedDamage(game_state, [18,4], 1000 ,1) # 0 is top right, 1 is top legft
        steps_RB = len(game_state.find_path_to_edge([18,4], 1))
        
        damage_RM = self.checkReceivedDamage(game_state, [23,9], 1000 ,1) # 0 is top right, 1 is top legft
        steps_RM = len(game_state.find_path_to_edge([14,0], 1))

        damage = damage_LB[0]
        steps = steps_LB
        target_edge = 0
        PING_S = [[4,9]]
        unit_type = PING
        if damage_LM[0] < damage or (damage_LM[0] == damage and steps_LM < steps): 
            damage = damage_LM[0]
            PING_S = [[9,4]]
            steps = steps_LM
            unit_type = SCRAMBLER
        if damage_RB[0] < damage or (damage_RB[0] == damage and steps_RB < steps): 
            damage = damage_RB[0]
            PING_S = [[18,4]]
            target_edge = 1
            steps = steps_RB
            unit_type = PING
        if damage_RM[0] < damage or (damage_RM[0] == damage and steps_RM < steps): 
            damage = damage_RM[0]
            PING_S = [[23,9]]
            target_edge = 1
            steps = steps_RM
            unit_type = SCRAMBLER

        if game_state.turn_number < 10:
            #if self.opposingEMP > 2:
                #self.deploy(game_state, EMP_S, EMP)
                #self.EMPattack = True
                #return
            if bits_he >= 11:
                self.deploy(game_state, PING_S, SCRAMBLER)
                self.exclusionList.extend(game_state.find_path_to_edge(PING_S[0], target_edge))
                gamelib.debug_write('launching scramblers to counter attack w damage {} turn{}'.format(damage, game_state.turn_number))
                self.PINGattack = True
                return
            if bits_me < 7:
                self.deploy(game_state, SCR_S, SCRAMBLER, 1)
                if self.opposingEMP < 1:
                    self.deploy(game_state, DEF_S, SCRAMBLER, 1)
                else:
                    self.deploy(game_state, SCR_S, SCRAMBLER, 1)
                return
            else:
                if damage >= 15*2*2 or game_state.turn_number < 2 or self.opposingEMP > 0 or (self.flip == False and self.targetsL >= 8) or (self.flip == True and self.targetsR >= 8):
                    self.deploy(game_state, EMP_S, EMP, 2)
                    self.deploy(game_state, SCR_S, SCRAMBLER)
                    self.EMPattack = True
                else:
                    self.deploy(game_state, PING_S, SCRAMBLER)
                    self.deploy(game_state, PING_S, SCRAMBLER)
                    self.exclusionList.extend(game_state.find_path_to_edge(PING_S[0], target_edge))
                    gamelib.debug_write('launching ping w damage {} turn{}'.format(damage, game_state.turn_number))
                    self.PINGattack = True
            return


        if game_state.turn_number < 20:
            if self.opposingEMP > 3:
                self.deploy(game_state, EMP_S, EMP)
                self.deploy(game_state, SCR_S, SCRAMBLER)
                self.EMPattack = True
                return
            if bits_he >= 14:
                self.deploy(game_state, PING_S, SCRAMBLER)
                self.exclusionList.extend(game_state.find_path_to_edge(PING_S[0], target_edge))
                gamelib.debug_write('launching scramblers to counter attack w damage {} turn{}'.format(damage, game_state.turn_number))
                self.PINGattack = True
                return
            if bits_me >= 10:
                if damage >= 15*2*5 or self.opposingEMP > 0 or (self.flip == False and self.targetsL >= 8) or (self.flip == True and self.targetsR >= 8):
                    self.deploy(game_state, EMP_S, EMP, 3)
                    self.deploy(game_state, SCR_S, SCRAMBLER)
                    self.EMPattack = True
                else:
                    self.deploy(game_state, PING_S, SCRAMBLER)
                    self.exclusionList.extend(game_state.find_path_to_edge(PING_S[0], target_edge))
                    gamelib.debug_write('launching ping w damage {} turn{}'.format(damage, game_state.turn_number))
                    self.PINGattack = True
            return
        

        if game_state.turn_number >= 20:
            #if self.opposingEMP > 3:
                #self.deploy(game_state, EMP_S, EMP)
                #self.deploy(game_state, SCR_S, SCRAMBLER)
                #self.EMPattack = True
            if bits_me >= 10:
                if damage >= 15*2*5 or self.opposingEMP > 0 or (self.flip == False and self.targetsL >= 8) or (self.flip == True and self.targetsR >= 8):
                    self.deploy(game_state, SCR_S, SCRAMBLER, 1)
                    self.deploy(game_state, EMP_S, EMP, 4)
                    self.deploy(game_state, SCR_S, SCRAMBLER)
                    self.EMPattack = True
                else:
                    self.deploy(game_state, PING_S, SCRAMBLER)
                    self.exclusionList.extend(game_state.find_path_to_edge(PING_S[0], target_edge))
                    gamelib.debug_write('launching ping w damage {} turn{}'.format(damage, game_state.turn_number))
                    self.PINGattack = True
            return

    def deploy(self, game_state, locations, unit_type, amount=20, flip = False):
        isFirewall = (unit_type == FILTER or unit_type == DESTRUCTOR or unit_type == ENCRYPTOR)
        if self.saveUp == True and isFirewall:
            return
        new_locations = flipArray(locations, flip)
        for i in range(amount):
            for location in new_locations:
                exclude = False
                for exclusion in self.exclusionList:
                    if exclusion == location:
                        exclude = isFirewall
                        break
                if game_state.can_spawn(unit_type, location, 1) and not exclude:
                    game_state.attempt_spawn(unit_type, location, 1)
                if game_state.contains_stationary_unit(location) == False and not exclude and isFirewall:
                    self.saveUp = True
                    return

    def deploySet(self, game_state, locations, flip = False):
        if self.saveUp == True:
            return
        new_locations = flipArray(locations, flip)
        missing = self.checkMissing(game_state, new_locations)
        if missing == len(locations) and missing*2 > game_state.get_resource(game_state.CORES,0):
            gamelib.debug_write('not enough resources for set deployment, turn{}'.format(game_state.turn_number))
            self.saveUp = True
            return

        for i in range(int(len(new_locations)/2)):
            exclude = False
            location = new_locations[2*i] # destructor
            for exclusion in self.exclusionList:
                    if exclusion == location:
                        exclude = True
                        break
            if exclude == False:
                if game_state.can_spawn(DESTRUCTOR, location, 1) and not exclude:
                    game_state.attempt_spawn(DESTRUCTOR, location, 1)
                if game_state.contains_stationary_unit(location) == False and not exclude:
                    self.saveUp = True
                    return        
            exclude = False
            location = new_locations[2*i+1] # filter
            for exclusion in self.exclusionList:
                    if exclusion == location:
                        exclude = True
                        break
            if exclude == False:
                if game_state.can_spawn(FILTER, location, 1) and not exclude:
                    game_state.attempt_spawn(FILTER, location, 1)
                if game_state.contains_stationary_unit(location) == False and not exclude:
                    self.saveUp = True
                    return

    def checkReceivedDamage(self, game_state, start_location, health, target_edge):
        path = game_state.find_path_to_edge(start_location, target_edge)
        endpoint = path[-1]
        if (endpoint[1]-endpoint[0] != 14 and target_edge == 1) or (endpoint[0]+endpoint[1] != 41 and target_edge == 0):
            gamelib.debug_write('cant reach edge. Path length {}, last point ({},{}), turn {}'.format(len(path), endpoint[0], endpoint[1], game_state.turn_number))
            return [10000, endpoint[0], endpoint[1]]   
        damage = 0.0
        for location in path:
            inRange = game_state.game_map.get_locations_in_range(location, 3.5)
            for target in inRange:
                if target[1] > 13 and game_state.contains_stationary_unit(target):
                    unit = game_state.game_map[target][0]
                    if unit.unit_type == DESTRUCTOR:
                        damage += 16.0
                        if damage >= health:
                            endpoint = location
                            return [damage, endpoint[0], endpoint[1]]
        return [damage, endpoint[0], endpoint[1]]

    def checkDealtDamage(self, game_state, start_location, target_location):
        path = game_state.find_path_to_point(start_location, target_location)
        damage = 0
        steps = len(path)
        for location in path:
            inRange = game_state.game_map.get_locations_in_range(location, 5.5)
            for target in inRange:
                if target[1] > 13 and game_state.contains_stationary_unit(target):
                    damage += 1
                    break
        return [damage, steps]

    def checkMissing(self, game_state, locations, flip = False):
        counter = 0
        new_locations  = flipArray(locations, flip)
        for location in new_locations:
            #exclude = False
            #for exclusion in self.exclusionList:
                #if exclusion == location:
                    #exclude = True
                    #break
            #if exclude == False and not game_state.contains_stationary_unit(location):
            if not game_state.contains_stationary_unit(location):
                counter += 1
        return counter

    def remove(self, game_state, locations, flip = False):
        removed = False
        locations = flipArray(locations, flip)
        for location in locations:
            if game_state.contains_stationary_unit(location):
                if game_state.attempt_remove(location) != None:
                    removed = True
        return removed

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()