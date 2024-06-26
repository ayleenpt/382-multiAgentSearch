# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        # Check if there are no food pellets left
        if newFood.count() == 0:
            return successorGameState.getScore()

        # Distance to the closest food
        closestFoodDist = min([util.manhattanDistance(newPos, food) for food in newFood.asList()])

        # Distance to the closest ghost
        closestGhostDist = min([util.manhattanDistance(newPos, ghost.getPosition()) for ghost in newGhostStates])

        # Check if the closest ghost is scared
        closestGhostScared = any([ghost.scaredTimer > 0 for ghost in newGhostStates])

        score = successorGameState.getScore()
        if closestGhostDist < 2 and not closestGhostScared:
            score -= 10  # Avoid ghosts if they are too close
        elif closestGhostDist > 2 and closestFoodDist != 0:
            score += 1.0 / closestFoodDist  # Prioritize moving closer to food
        elif closestGhostScared:
            score += 10  # Chase scared ghosts

        return score

def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        def minimax(state, depth, agentIndex):
            if depth == self.depth or state.isWin() or state.isLose():
                return self.evaluationFunction(state)
            
            if agentIndex == 0: # maximize for pacman
                bestValue = float("-inf")
                bestAction = None
                for action in state.getLegalActions(agentIndex):
                    successor = state.generateSuccessor(agentIndex, action)
                    value = minimax(successor, depth, 1)
                    if value > bestValue:
                        bestValue = value
                        bestAction = action
                if depth == 0: # return action only at level 0
                    return bestAction
                return bestValue
            
            else: # minimize for ghosts
                bestValue = float("inf")
                for action in state.getLegalActions(agentIndex):
                    successor = state.generateSuccessor(agentIndex, action)
                    if agentIndex == (state.getNumAgents() - 1):
                        value = minimax(successor, (depth + 1), 0)
                    else:
                        value = minimax(successor, depth, (agentIndex + 1))
                    bestValue = min(bestValue, value)
                return bestValue
        
        return minimax(gameState, 0, 0)

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        def alpha_beta_search(state):
            alpha = float("-inf")
            beta = float("inf")
            bestValue = float("-inf")
            bestAction = None

            for action in state.getLegalActions(0):  # Assuming Pacman is always agent 0
                successor = state.generateSuccessor(0, action)
                value = min_value(successor, 1, 0, alpha, beta)
                if value > bestValue:
                    bestValue = value
                    bestAction = action
                alpha = max(alpha, bestValue)
            return bestAction

        def max_value(state, depth, alpha, beta):
            if depth == self.depth or state.isWin() or state.isLose():
                return self.evaluationFunction(state)

            v = float("-inf")
            for action in state.getLegalActions(0):
                successor = state.generateSuccessor(0, action)
                v = max(v, min_value(successor, 1, depth, alpha, beta))
                if v > beta:
                    return v
                alpha = max(alpha, v)
            return v

        def min_value(state, ghostIndex, depth, alpha, beta):
            if state.isWin() or state.isLose():
                return self.evaluationFunction(state)

            v = float("inf")
            for action in state.getLegalActions(ghostIndex):
                successor = state.generateSuccessor(ghostIndex, action)
                if ghostIndex == state.getNumAgents() - 1:
                    v = min(v, max_value(successor, depth + 1, alpha, beta))
                else:
                    v = min(v, min_value(successor, ghostIndex + 1, depth, alpha, beta))
                if v < alpha:
                    return v
                beta = min(beta, v)
            return v

        return alpha_beta_search(gameState)

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        def expectimax(state, depth, agentIndex):
            if depth == self.depth or state.isWin() or state.isLose():
                return self.evaluationFunction(state)
            
            if agentIndex == 0: # maximize for pacman
                bestValue = float("-inf")
                bestAction = None
                for action in state.getLegalActions(agentIndex):
                    successor = state.generateSuccessor(agentIndex, action)
                    value = expectimax(successor, depth, 1)
                    if value > bestValue:
                        bestValue = value
                        bestAction = action
                if depth == 0: # return action only at level 0
                    return bestAction
                return bestValue
            
            else: # take average for ghosts
                value = 0
                count = 0
                for action in state.getLegalActions(agentIndex):
                    successor = state.generateSuccessor(agentIndex, action)
                    if agentIndex == (state.getNumAgents() - 1):
                        value += expectimax(successor, (depth + 1), 0)
                    else:
                        value += expectimax(successor, depth, (agentIndex + 1))
                    count += 1
                return (value / count)
        
        return expectimax(gameState, 0, 0)

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    Calculates a score based on Pacman's position, the positions of the food
    pellets, ghosts, capsules, and Pacman's current score. It prioritizes
    actions that move Pacman closer to food pellets, capsules, and scared
    ghosts, while avoiding actions that lead Pacman towards dangerous ghosts.

    """
    # Extracting useful information from the current game state
    pacmanPosition = currentGameState.getPacmanPosition()
    foodGrid = currentGameState.getFood()
    ghostStates = currentGameState.getGhostStates()
    scaredTimes = [ghostState.scaredTimer for ghostState in ghostStates]
    capsules = currentGameState.getCapsules()
    score = currentGameState.getScore()

    # Initialize the evaluation score
    evalScore = score

    # Distance to the closest food pellet
    closestFoodDist = float('inf')
    for food in foodGrid.asList():
        dist = util.manhattanDistance(pacmanPosition, food)
        if dist < closestFoodDist:
            closestFoodDist = dist

    # Check if the closest ghost is scared
    closestGhostDist = float('inf')
    for ghostState in ghostStates:
        dist = util.manhattanDistance(pacmanPosition, ghostState.getPosition())
        if dist < closestGhostDist:
            closestGhostDist = dist

    if closestGhostDist < 2 and not any(scaredTimes):
        evalScore -= 100  # Avoid ghosts if they are too close and not scared
    elif closestGhostDist > 2 and closestFoodDist != float('inf'):
        evalScore += 1.0 / closestFoodDist  # Prioritize moving closer to food
    elif any(scaredTimes):
        evalScore += 100  # Chase scared ghosts

    # Distance to the closest capsule
    closestCapsuleDist = float('inf')
    for capsule in capsules:
        dist = util.manhattanDistance(pacmanPosition, capsule)
        if dist < closestCapsuleDist:
            closestCapsuleDist = dist

    if closestCapsuleDist != float('inf'):
        evalScore += 10.0 / closestCapsuleDist  # Prioritize moving closer to capsules

    return evalScore

# Abbreviation
better = betterEvaluationFunction
