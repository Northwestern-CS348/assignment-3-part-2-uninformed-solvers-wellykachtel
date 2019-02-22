from game_master import GameMaster
from read import *
from util import *

class TowerOfHanoiGame(GameMaster):

    def __init__(self):
        super().__init__()
        
    def produceMovableQuery(self):
        """
        See overridden parent class method for more information.

        Returns:
             A Fact object that could be used to query the currently available moves
        """
        return parse_input('fact: (movable ?disk ?init ?target)')

    def getGameState(self):
        """
        Returns a representation of the game in the current state.
        The output should be a Tuple of three Tuples. Each inner tuple should
        represent a peg, and its content the disks on the peg. Disks
        should be represented by integers, with the smallest disk
        represented by 1, and the second smallest 2, etc.

        Within each inner Tuple, the integers should be sorted in ascending order,
        indicating the smallest disk stacked on top of the larger ones.

        For example, the output should adopt the following format:
        ((1,2,5),(),(3, 4))

        Returns:
            A Tuple of Tuples that represent the game state
        """
        result = self.kb.kb_ask(parse_input("fact: (on ?disk ?peg)"));
        peg1 = list(filter(lambda binding: binding[0].bindings[1].constant.element == 'peg1', result.list_of_bindings))
        peg2 = list(filter(lambda binding: binding[0].bindings[1].constant.element == 'peg2', result.list_of_bindings))
        peg3 = list(filter(lambda binding: binding[0].bindings[1].constant.element == 'peg3', result.list_of_bindings))

        disksPeg1 = []
        disksPeg2 = []
        disksPeg3 = []

        for binding in peg1:
            disk = binding[0].bindings[0].constant.element[4:]
            disksPeg1.append(int(disk))
        for binding in peg2:
            disk = binding[0].bindings[0].constant.element[4:]
            disksPeg2.append(int(disk))
        for binding in peg3:
            disk = binding[0].bindings[0].constant.element[4:]
            disksPeg3.append(int(disk))

        disksPeg1.sort()
        peg1Tuple = tuple(disksPeg1)
        disksPeg2.sort()
        peg2Tuple = tuple(disksPeg2)
        disksPeg3.sort()
        peg3Tuple = tuple(disksPeg3)


        return (peg1Tuple, peg2Tuple, peg3Tuple)


    def makeMove(self, movable_statement):
        """
        Takes a MOVABLE statement and makes the corresponding move. This will
        result in a change of the game state, and therefore requires updating
        the KB in the Game Master.

        The statement should come directly from the result of the MOVABLE query
        issued to the KB, in the following format:
        (movable disk1 peg1 peg3)

        Args:
            movable_statement: A Statement object that contains one of the currently viable moves

        Returns:
            None
        """
        disk = movable_statement.terms[0].term.element
        startingPeg = movable_statement.terms[1].term.element
        endingPeg = movable_statement.terms[2].term.element
        # find what the moving disk is on top of, another disk or base
        fact1 = self.kb.kb_ask(parse_input("fact: (ontop " + disk + " ?object)"))
        diskIsOn = fact1.list_of_bindings[0][0].bindings[0].constant.element
        # find what is on the top of the peg that disk is being moved to
        fact2 = self.kb.kb_ask(parse_input("fact: (top ?disk " + endingPeg + ")"))
        topOfEndingPeg = fact2.list_of_bindings[0][0].bindings[0].constant.element if fact2 else 'base'

        addStatement1 = "fact: (top " + disk + " " + endingPeg + ")"
        addStatement2 = "fact: (on " + disk + " " + endingPeg + ")"
        addStatement3 = "fact: (ontop " + disk + " " + topOfEndingPeg + ")"
        maybeAddStatement4 = "fact: (top " + diskIsOn + " " + startingPeg + ")" # only add if diskIsOn is not a base
        maybeAddStatement5 = "fact: (empty " + startingPeg + ")" #only add if diskIsOn is base

        retractStatement1 = "fact: (top " + disk + " " + startingPeg + ")"
        retractStatement2 = "fact: (on " + disk + " " + startingPeg + ")"
        retractStatement3 = "fact: (ontop " + disk + " " + diskIsOn + ")"
        retractStatement4 = "fact: (empty " + endingPeg + ")"
        maybeRetractStatement5 = "fact: (top " + topOfEndingPeg + " " + endingPeg + ")"

        self.kb.kb_retract(parse_input(retractStatement1))
        self.kb.kb_retract(parse_input(retractStatement2))
        self.kb.kb_retract(parse_input(retractStatement3))
        self.kb.kb_retract(parse_input(retractStatement4))
        if topOfEndingPeg != 'base':
            self.kb.kb_retract(parse_input(maybeRetractStatement5))

        self.kb.kb_add(parse_input(addStatement1))
        self.kb.kb_add(parse_input(addStatement2))
        self.kb.kb_add(parse_input(addStatement3))
        if diskIsOn != 'base':
            self.kb.kb_add(parse_input(maybeAddStatement4))
        else:
            self.kb.kb_add(parse_input(maybeAddStatement5))



        """self.kb.kb_retract(fact1.list_of_bindings[0][1][0])
        if fact2:
            self.kb.kb_retract(fact2.list_of_bindings[0][1][0])
        self.kb.kb_retract(parse_input("fact: (on " + disk + " " + startingPeg + ")"))
        self.kb.kb_add(parse_input("fact: (on " + disk + " " + endingPeg + ")"))
        self.kb.kb_add(parse_input("fact: (ontop " + disk + " " + topOfEndingPeg + ")"))
        self.kb.kb_add(parse_input("fact: (top " + disk + " " + endingPeg + ")"))
        if diskIsOn != 'base':
            self.kb.kb_add(parse_input("fact: (top " + diskIsOn + " " + startingPeg + ")"))"""

    def reverseMove(self, movable_statement):
        """
        See overridden parent class method for more information.

        Args:
            movable_statement: A Statement object that contains one of the previously viable moves

        Returns:
            None
        """
        pred = movable_statement.predicate
        sl = movable_statement.terms
        newList = [pred, sl[0], sl[2], sl[1]]
        self.makeMove(Statement(newList))

class Puzzle8Game(GameMaster):

    def __init__(self):
        super().__init__()

    def produceMovableQuery(self):
        """
        Create the Fact object that could be used to query
        the KB of the presently available moves. This function
        is called once per game.

        Returns:
             A Fact object that could be used to query the currently available moves
        """
        return parse_input('fact: (movable ?piece ?initX ?initY ?targetX ?targetY)')

    def getGameState(self):
        """
        Returns a representation of the the game board in the current state.
        The output should be a Tuple of Three Tuples. Each inner tuple should
        represent a row of tiles on the board. Each tile should be represented
        with an integer; the empty space should be represented with -1.

        For example, the output should adopt the following format:
        ((1, 2, 3), (4, 5, 6), (7, 8, -1))

        Returns:
            A Tuple of Tuples that represent the game state
        """


        row1 = self.kb.kb_ask(parse_input("fact: (coordinate ?tile ?x pos1)"));
        row2 = self.kb.kb_ask(parse_input("fact: (coordinate ?tile ?x pos2)"));
        row3 = self.kb.kb_ask(parse_input("fact: (coordinate ?tile ?x pos3)"));

        tilesRow1 = [None] * 3
        tilesRow2 = [None] * 3
        tilesRow3 = [None] * 3

        for binding in row1.list_of_bindings:
            tile = binding[0].bindings[0].constant.element[4:]
            order = binding[0].bindings[1].constant.element[3:]
            tilesRow1[int(order) - 1] = int(tile) if int(tile) > 0 else -1
            #tilesRow1.append(int(tile)) if int(tile) > 0 else tilesRow1.append(-1)
        for binding in row2.list_of_bindings:
            tile = binding[0].bindings[0].constant.element[4:]
            order = binding[0].bindings[1].constant.element[3:]
            tilesRow2[int(order) - 1] = int(tile) if int(tile) > 0 else -1
            #tilesRow2.append(int(tile)) if int(tile) > 0 else tilesRow1.append(-1)
        for binding in row3.list_of_bindings:
            tile = binding[0].bindings[0].constant.element[4:]
            order = binding[0].bindings[1].constant.element[3:]
            tilesRow3[int(order) - 1] = int(tile) if int(tile) > 0 else -1
            #tilesRow3.append(int(tile)) if int(tile) > 0 else tilesRow1.append(-1)

        row1Tuple = tuple(tilesRow1)
        row2Tuple = tuple(tilesRow2)
        row3Tuple = tuple(tilesRow3)

        return (row1Tuple, row2Tuple, row3Tuple)

    def makeMove(self, movable_statement):
        """
        Takes a MOVABLE statement and makes the corresponding move. This will
        result in a change of the game state, and therefore requires updating
        the KB in the Game Master.

        The statement should come directly from the result of the MOVABLE query
        issued to the KB, in the following format:
        (movable tile3 pos1 pos3 pos2 pos3)

        Args:
            movable_statement: A Statement object that contains one of the currently viable moves

        Returns:
            None
        """
        tile = movable_statement.terms[0].term.element
        startingX = movable_statement.terms[1].term.element
        startingY = movable_statement.terms[2].term.element
        endingX = movable_statement.terms[3].term.element
        endingY = movable_statement.terms[4].term.element
        # make starting where empty tile is
        # make ending where tile is
        # retract original coordinate of tile
        # retract original coordinate of empty tile
        self.kb.kb_retract(parse_input("fact: (coordinate tile0 " + endingX + " " + endingY + ")"))
        self.kb.kb_retract(parse_input("fact: (coordinate " + tile + " " + startingX + " " + startingY + ")"))
        self.kb.kb_add(parse_input("fact: (coordinate tile0 " + startingX + " " + startingY + ")"))
        self.kb.kb_add(parse_input("fact: (coordinate " + tile + " " + endingX + " " + endingY + ")"))
        pass

    def reverseMove(self, movable_statement):
        """
        See overridden parent class method for more information.

        Args:
            movable_statement: A Statement object that contains one of the previously viable moves

        Returns:
            None
        """
        pred = movable_statement.predicate
        sl = movable_statement.terms
        newList = [pred, sl[0], sl[3], sl[4], sl[1], sl[2]]
        self.makeMove(Statement(newList))
