import logging
import random
import time

import util
from game import Actions, Agent, Directions
from logs.search_logger import log_function
from pacman import GameState
from util import manhattanDistance

import math
def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function.
    """
    # Get current position and food
    pos = currentGameState.getPacmanPosition()
    food = currentGameState.getFood()
    food_list = food.asList()
    capsules = currentGameState.getCapsules()  # Get power pellets
    
    # Get ghost positions and states
    ghost_states = currentGameState.getGhostStates()
    
    # Calculate distance to closest food
    if food_list:
        min_food_dist = min(manhattanDistance(pos, food) for food in food_list)
        # Consider average distance to all food for future planning
        avg_food_dist = sum(manhattanDistance(pos, food) for food in food_list) / len(food_list)
    else:
        min_food_dist = 0
        avg_food_dist = 0
    
    # Calculate distance to closest capsule (power pellet)
    if capsules:
        min_capsule_dist = min(manhattanDistance(pos, capsule) for capsule in capsules)
        # Consider average distance to all capsules
        avg_capsule_dist = sum(manhattanDistance(pos, capsule) for capsule in capsules) / len(capsules)
    else:
        min_capsule_dist = 0
        avg_capsule_dist = 0
    
    # Calculate ghost distances and check if they're scared
    min_ghost_dist = float('inf')
    ghost_scared = False
    for ghost in ghost_states:
        ghost_dist = manhattanDistance(pos, ghost.getPosition())
        if ghost_dist < min_ghost_dist:
            min_ghost_dist = ghost_dist
        if ghost.scaredTimer > 0:
            ghost_scared = True
    
    # Base score
    score = currentGameState.getScore()
    
    # Add food-based score (considering both immediate and future food)
    if min_food_dist > 0:
        score += 20.0 / (min_food_dist + 1)  # Increased weight for immediate food
        score += 10.0 / (avg_food_dist + 1)   # Future food potential
    
    # Add capsule-based score (considering both immediate and future power pellets)
    if min_capsule_dist > 0:
        score += 30.0 / (min_capsule_dist + 1)  # Increased weight for immediate power pellet
        score += 15.0 / (avg_capsule_dist + 1)  # Future power pellet potential
    
    # Ghost handling with distance-based scaling
    if ghost_scared:
        # When ghosts are scared, we want to chase them
        if min_ghost_dist < 3:
            score += 100.0 / (min_ghost_dist + 1)  # Increased bonus for being close to scared ghosts
    else:
        # When ghosts are not scared, avoid them with distance-based scaling
        if min_ghost_dist < 2:
            score -= 500.0  # Severe penalty for being close to ghosts
        elif min_ghost_dist < 3:
            score -= 50.0 / (min_ghost_dist + 1)
        else:
            # When ghosts are far away, reduce their impact on decision making
            score -= 10.0 / (min_ghost_dist + 1)
    
    # Additional survival bonus (reduced to encourage food collection)
    if not currentGameState.isLose():
        score += 50  # Reduced survival bonus to encourage food collection
    
    # Add a small constant bonus to encourage movement
    score += 1.0
    
    return score

class Q2_Agent(Agent):

    def __init__(self, evalFn = 'betterEvaluationFunction', depth = '3'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)
        self.start_time = None
        self.time_limit = 29  # Leave 1 seconds buffer for safety
        
        # Add position history tracking
        self.position_history = []  # Track recent positions
        self.max_history = 10  # Keep last 10 positions
        
        # Add visited positions tracking
        self.visited_positions = {}  # Position -> visit count
        
        # Add state cache for performance
        self.state_cache = {}
        
        # Add branch limiting
        self.max_branches = 3  # Maximum number of branches to consider at each level

    def detect_oscillation(self):
        """
        Detect if Pacman is oscillating between positions
        Returns True if an oscillation pattern is detected
        """
        if len(self.position_history) < 6:
            return False
            
        # Check for 2-position cycle (A-B-A-B-A-B)
        if (self.position_history[-1] == self.position_history[-3] == self.position_history[-5] and
            self.position_history[-2] == self.position_history[-4] == self.position_history[-6]):
            return True
            
        # Check for 3-position cycle (A-B-C-A-B-C)
        if (len(self.position_history) >= 9 and
            self.position_history[-1] == self.position_history[-4] == self.position_history[-7] and
            self.position_history[-2] == self.position_history[-5] == self.position_history[-8] and
            self.position_history[-3] == self.position_history[-6] == self.position_history[-9]):
            return True
            
        return False

    @log_function
    def getAction(self, gameState: GameState):
        """
        Returns the minimax action using alpha-beta pruning with adaptive depth
        """
        if self.start_time is None:
            self.start_time = time.time()

        # Update position history
        current_pos = gameState.getPacmanPosition()
        self.position_history.append(current_pos)
        if len(self.position_history) > self.max_history:
            self.position_history.pop(0)
            
        # Update visited positions
        self.visited_positions[current_pos] = self.visited_positions.get(current_pos, 0) + 1
        
        # Clear state cache for new search
        self.state_cache = {}

        def minimax(state, depth, agentIndex, alpha, beta):
            # Check time limit
            if time.time() - self.start_time > self.time_limit:
                # If time limit reached, return best immediate action
                legal_actions = state.getLegalActions(agentIndex)
                if not legal_actions:
                    return self.evaluationFunction(state), Directions.STOP
                
                # For Pacman, choose action that maximizes immediate evaluation
                if agentIndex == 0:
                    best_value = float('-inf')
                    best_action = Directions.STOP
                    for action in legal_actions:
                        successor = state.generateSuccessor(agentIndex, action)
                        value = self.evaluationFunction(successor)
                        if value > best_value:
                            best_value = value
                            best_action = action
                    return best_value, best_action
                # For ghosts, choose action that minimizes immediate evaluation
                else:
                    best_value = float('inf')
                    best_action = Directions.STOP
                    for action in legal_actions:
                        successor = state.generateSuccessor(agentIndex, action)
                        value = self.evaluationFunction(successor)
                        if value < best_value:
                            best_value = value
                            best_action = action
                    return best_value, best_action

            # Terminal states
            if state.isWin() or state.isLose() or depth == 0:
                return self.evaluationFunction(state), Directions.STOP
            
            # Get legal actions
            legal_actions = state.getLegalActions(agentIndex)
            if not legal_actions:
                return self.evaluationFunction(state), Directions.STOP
            
            # Remove STOP action if there are other options
            if Directions.STOP in legal_actions and len(legal_actions) > 1:
                legal_actions.remove(Directions.STOP)
            
            # Action ordering for Pacman
            if agentIndex == 0:
                # Pre-evaluate actions and sort by score
                action_scores = []
                for action in legal_actions:
                    successor = state.generateSuccessor(agentIndex, action)
                    score = self.evaluationFunction(successor)
                    action_scores.append((action, score))
                
                # Sort actions by score and limit branches
                action_scores.sort(key=lambda x: x[1], reverse=True)
                legal_actions = [a for a, _ in action_scores[:self.max_branches]]
            
            # Initialize best action
            best_action = Directions.STOP
            
            # Pacman is maximizer (agent 0)
            if agentIndex == 0:
                value = float('-inf')
                for action in legal_actions:
                    successor = state.generateSuccessor(agentIndex, action)
                    successor_value, _ = minimax(successor, depth - 1, 1, alpha, beta)
                    
                    # Apply oscillation penalty
                    successor_pos = successor.getPacmanPosition()
                    if successor_pos in self.position_history:
                        recency = self.position_history.count(successor_pos)
                        successor_value -= recency * 20
                    
                    if successor_value > value:
                        value = successor_value
                        best_action = action
                    
                    alpha = max(alpha, value)
                    if beta <= alpha:
                        break
                return value, best_action
            
            # Ghosts are minimizers (agent > 0)
            else:
                value = float('inf')
                next_agent = (agentIndex + 1) % state.getNumAgents()
                for action in legal_actions:
                    successor = state.generateSuccessor(agentIndex, action)
                    successor_value, _ = minimax(successor, depth - 1, next_agent, alpha, beta)
                    
                    if successor_value < value:
                        value = successor_value
                        best_action = action
                    
                    beta = min(beta, value)
                    if beta <= alpha:
                        break
                return value, best_action

        # Adaptive depth based on game state
        num_agents = gameState.getNumAgents()
        num_food = len(gameState.getFood().asList())
        
        # Adjust depth based on game state
        if self.detect_oscillation():
            search_depth = 2  # Reduce depth when oscillating
        elif num_food < 3:  # Very few food dots left
            search_depth = 3 * num_agents  # Shallow search for endgame
        elif num_food < 6:  # Few food dots
            search_depth = 2 * num_agents
        else:  # Many food dots
            search_depth = num_agents  # Minimal depth for most of the game

        # Start minimax search with adaptive depth
        _, best_action = minimax(gameState, search_depth, 0, float('-inf'), float('inf'))
        return best_action