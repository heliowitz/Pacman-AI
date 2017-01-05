# multiAgents.py
# --------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

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
    some Directions.X for some X in the set {North, South, West, East, Stop}
    """
    # Collect legal moves and successor states

    legalMoves = gameState.getLegalActions()

    # Choose one of the best actions
    scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
    bestScore = max(scores)
    bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
    chosenIndex = random.choice(bestIndices) # Pick randomly among the best

    return legalMoves[chosenIndex]

  def evaluationFunction(self, currentGameState, action):
    successorGameState = currentGameState.generatePacmanSuccessor(action)
    newPos = successorGameState.getPacmanPosition()
    oldFood = currentGameState.getFood()
    pacPos = successorGameState.getPacmanPosition()
    ghostPos = successorGameState.getGhostPositions()[0]

    eval = 0
    # Whether or not the successor state has a food pellet
    hasFood = currentGameState.hasFood(newPos[0], newPos[1])
    if hasFood: # If there's food at the successor, return 1.
		  eval = 2
    else: # If the state doesn't have food
      pQueue = util.PriorityQueue() # Create a priorityQueue
      foodRemaining = currentGameState.getNumFood() # Gets the number of pellets left

      if foodRemaining >= 7:
        queueLimit = 7 # Will consider the closest 7 food pellets
      else:
        queueLimit = foodRemaining # Will consider all remaining food pellets

      # Determine the locations of the closest food pellets to Pacman 
      for a, itemA in enumerate(oldFood):
        for b, itemB in enumerate(itemA):
          if itemB:
            currentFood = (a,b)
            if len(pQueue.heap) >= queueLimit: #pQueue has reached the limit.
              furthestFood = pQueue.pop() # Pop the current furthest food being considered
              # If the new considered food is closer than the furthest away food in the pQueue:
              if manhattanDistance(newPos, currentFood) < manhattanDistance(newPos, furthestFood):
                pQueue.push(currentFood, float(1)/float(manhattanDistance(newPos, currentFood)))
              else:
                pQueue.push(furthestFood, float(1)/float(manhattanDistance(newPos, furthestFood)))
            else:
  						pQueue.push(currentFood, float(1)/float(manhattanDistance(newPos, currentFood)))

      # Find the average reciprocal of all considered food distances 
      aggregateFoodDistance = 0
      for index in range(0, len(pQueue.heap)):
        aggregateFoodDistance += manhattanDistance(newPos, pQueue.pop())
        eval = float(queueLimit)/float(aggregateFoodDistance)
    
    if action=="Stop": # Reward no points for stopping
      eval = 0
    elif manhattanDistance(pacPos, ghostPos) <= 1: # If the ghost is right beside Pacman
      eval = -10000
    return eval

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
    layer = 0 # starting at the top of the tree with Pacman to move
    legalPacmanMoves = gameState.getLegalActions(0) 
    legalPacmanMoves.remove('Stop')
    values = []

    # Choose one of the best actions
    for index, action in enumerate(legalPacmanMoves):
      values.append((self.getValue(1, gameState.generateSuccessor(0, action)), action))
    bestValue = max(values)
    return bestValue[1]
    util.raiseNotDefined()


  def getValue(self, layer, gameState):
    if gameState.isWin(): # If the state is a win state (terminal)
      return 10000
    elif gameState.isLose(): # If the state is a lose state (terminal)
      return -10000

    elif layer >= 2*self.depth: # If reached depth 
      return self.evaluationFunction(gameState)
    
    elif layer%2==0: # If state is Pacman's move
      layer += 1
      values = [] 
      legalPacmanMoves = gameState.getLegalActions(0) 
      legalPacmanMoves.remove('Stop')
      # Get max value of the state's successor states
      for index, action in enumerate(legalPacmanMoves):
        values.append(self.getValue(layer, gameState.generateSuccessor(0, action)))
      return max(values)
    
    else: # State is Ghost's move
      layer += 1
      values = [] 
      legalGhostMoves = gameState.getLegalActions(1) 
      for index, action in enumerate(legalGhostMoves):
      # Get min value of the state's succesor states
        values.append(self.getValue(layer, gameState.generateSuccessor(1, action)))  
      return min(values)

class AlphaBetaAgent(MultiAgentSearchAgent):


  def getAction(self, gameState):
    """
      Returns the minimax action using self.depth and self.evaluationFunction
    """
    layer = 0 # starting at the top of the tree with Pacman to move
    legalPacmanMoves = gameState.getLegalActions(0) 
    legalPacmanMoves.remove('Stop')
    values = []

    # Choose one of the best actions
    for index, action in enumerate(legalPacmanMoves):
      values.append((self.getMinValue(gameState.generateSuccessor(0, action), 1, float("-inf"), float("inf")), action))
      bestValue = max(values)
    return bestValue[1]
    util.raiseNotDefined()

  def getMaxValue(self, gameState, layer, alpha, beta): # Get max value
    if gameState.isWin(): # If the state is a win state (terminal)
      return 10000
    elif gameState.isLose(): # If the state is a lose state (terminal)
      return -10000
    elif layer >= 2*self.depth: # If the state reaches the depth limit
      return self.evaluationFunction(gameState)
    else:
      layer += 1
      value = float("-inf")
      # Get max value of the minValue of state's successors
      for action in gameState.getLegalActions(0):
        value = max(value, self.getMinValue(gameState.generateSuccessor(0, action), layer, alpha, beta))
        if value >= beta:
          return value
        else:
          alpha = max(alpha, value)
    return value

  def getMinValue(self, gameState, layer, alpha, beta): # Get min value
    if gameState.isWin(): # If the state is a win state (terminal)
      return 10000
    elif gameState.isLose(): # If the state is a lose state (terminal)
      return -10000
    elif layer >= 2*self.depth: # If the state reaches the depth limit 
      return self.evaluationFunction(gameState)
    else:
      layer += 1
      value = float("inf")
      # Get min value of the maxValue of state's successors 
      for action in gameState.getLegalActions(1):
        value = min(value, self.getMaxValue(gameState.generateSuccessor(1, action), layer, alpha, beta))
        if value <= alpha:
          return value
        else:
          beta = min(beta, value)
    return value
    
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
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
  """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
  """
  "*** YOUR CODE HERE ***"
  util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction

class ContestAgent(MultiAgentSearchAgent):
  """
    Your agent for the mini-contest
  """

  def getAction(self, gameState):
    """
      Returns an action.  You can use any method you want and search to any depth you want.
      Just remember that the mini-contest is timed, so you have to trade off speed and computation.

      Ghosts don't behave randomly anymore, but they aren't perfect either -- they'll usually
      just make a beeline straight towards Pacman (or away from him if they're scared!)
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()
