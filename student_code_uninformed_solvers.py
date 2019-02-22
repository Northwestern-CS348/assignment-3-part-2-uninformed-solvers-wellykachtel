
from solver import *

class SolverDFS(UninformedSolver):
    def __init__(self, gameMaster, victoryCondition):
        super().__init__(gameMaster, victoryCondition)

    def solveOneStep(self):
        """
        Go to the next state that has not been explored. If a
        game state leads to more than one unexplored game states,
        explore in the order implied by the GameMaster.getMovables()
        function.
        If all game states reachable from a parent state has been explored,
        the next explored state should conform to the specifications of
        the Depth-First Search algorithm.

        Returns:
            True if the desired solution state is reached, False otherwise
        """
        ### use a stack (only use append and pop)
        if self.gm.getGameState() == self.victoryCondition:
            return True
        movables = self.gm.getMovables()
        if not movables:
            self.gm.reverseMove(self.currentState.requiredMovable)
        else:
            for move in movables:
                self.gm.makeMove(move)
                state = GameState(self.gm.getGameState(), self.currentState.depth + 1, move)
                state.parent = self.currentState
                self.currentState.children.append(state)
                self.gm.reverseMove(move)

        childToVisit = self.findNextVisitDFS(self.currentState)
        if childToVisit is None:
            return False
        self.gm.makeMove(childToVisit.requiredMovable)
        self.visited[childToVisit] = True
        new_state = self.gm.getGameState()
        if new_state == self.victoryCondition:
            self.currentState = childToVisit
            return True
        self.currentState = childToVisit

        return False


    # go to next child, if this has been visited, increment nextChildToVisit
    # if the end of the children is reached, run findNextVisit on the parent node
    def findNextVisitDFS(self, node):
        index = node.nextChildToVisit
        if index < len(node.children) and node.children[index] not in self.visited:
            return node.children[index]
        elif index >= len(node.children):
            if node.parent is None:
                return None
            else:
                self.gm.reverseMove(node.requiredMovable)
                return self.findNextVisitDFS(node.parent)
        node.nextChildToVisit += 1
        return self.findNextVisitDFS(node)


class SolverBFS(UninformedSolver):
    def __init__(self, gameMaster, victoryCondition):
        super().__init__(gameMaster, victoryCondition)
        self.bfsqueue = Queue()

    def solveOneStep(self):
        """
        Go to the next state that has not been explored. If a
        game state leads to more than one unexplored game states,
        explore in the order implied by the GameMaster.getMovables()
        function.
        If all game states reachable from a parent state has been explored,
        the next explored state should conform to the specifications of
        the Breadth-First Search algorithm.

        Returns:
            True if the desired solution state is reached, False otherwise
        """
        ### use a queue (only use append and popleft)

        if self.gm.getGameState() == self.victoryCondition:
            return True
        current = self.currentState
        movables = self.gm.getMovables()
        if not movables:
            self.gm.reverseMove(current.requiredMovable)
        else:
            for move in movables:
                self.gm.makeMove(move)
                state = GameState(self.gm.getGameState(), self.currentState.depth + 1, move)
                state.parent = current
                if state not in self.visited:
                    self.bfsqueue.enqueue(state)
                self.gm.reverseMove(move)


        childToVisit = self.bfsqueue.dequeue()
        while childToVisit in self.visited:
            childToVisit = self.bfsqueue.dequeue()

        self.visited[childToVisit] = True

        currentDepth = current.depth
        nextDepth = childToVisit.depth
        if current.parent is None:
            self.gm.makeMove(childToVisit.requiredMovable)
        elif current.parent == childToVisit.parent:
            self.gm.reverseMove(current.requiredMovable)
            self.gm.makeMove(childToVisit.requiredMovable)
        else:
            i = 0
            while i < currentDepth:
                self.gm.reverseMove(current.requiredMovable)
                current = current.parent
                i += 1
            i = 0
            moves = []
            pointerToNext = childToVisit
            while i < nextDepth:
                moves.append(pointerToNext.requiredMovable)
                pointerToNext = pointerToNext.parent
                i += 1
            while moves:
                self.gm.makeMove(moves.pop())

        new_state = self.gm.getGameState()
        if new_state == self.victoryCondition:
            self.currentState = childToVisit
            return True
        self.currentState = childToVisit

        return False


class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)