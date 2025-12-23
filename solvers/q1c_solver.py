#---------------------#
# DO NOT MODIFY BEGIN #
#---------------------#

import logging

import util
from problems.q1c_problem import q1c_problem

#-------------------#
# DO NOT MODIFY END #
#-------------------#
from game import Directions, Actions
import time

def q1c_solver(problem: q1c_problem):
    """
    A smarter solver that evaluates the cost-benefit ratio of collecting each food dot.
    Considers:
    1. Distance to food
    2. Time limit
    3. Potential score gain vs. time cost
    """
    start_time = time.time()
    TIME_LIMIT = 9.9
    
    # Get initial state
    current_pos, food_list = problem.getStartState()
    path = []
    
    while food_list and time.time() - start_time < TIME_LIMIT:
        # Find most valuable food dot to collect
        best_food = None
        best_score_per_step = float('-inf')
        remaining_time = TIME_LIMIT - (time.time() - start_time)
        
        for food in food_list:
            # Find path to this food
            temp_path = find_path_to_food(current_pos, food, problem.startingGameState)
            if not temp_path:
                continue
                
            # Calculate cost-benefit ratio
            path_length = len(temp_path)
            if path_length == 0:
                continue
                
            # Estimate time to reach this food (assuming 0.1s per step)
            estimated_time = path_length * 0.1
            
            # Skip if we don't have enough time to reach this food
            if estimated_time > remaining_time:
                continue
                
            # Calculate score per step (10 points per food dot)
            score_per_step = 10.0 / path_length
            
            if score_per_step > best_score_per_step:
                best_score_per_step = score_per_step
                best_food = food
        
        if best_food is None:
            break
            
        # Find and add path to best food
        temp_path = find_path_to_food(current_pos, best_food, problem.startingGameState)
        if temp_path:
            path.extend(temp_path)
            current_pos = best_food
            food_list.remove(best_food)
        else:
            break
    
    return path

def find_path_to_food(start, goal, game_state):
    """Simple BFS to find path to a specific food dot"""
    queue = util.Queue()
    queue.push((start, []))
    visited = set([start])
    
    while not queue.isEmpty():
        pos, path = queue.pop()
        
        if pos == goal:
            return path
            
        x, y = pos
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            dx, dy = Actions.directionToVector(action)
            next_x, next_y = int(x + dx), int(y + dy)
            next_pos = (next_x, next_y)
            
            if not game_state.hasWall(next_x, next_y) and next_pos not in visited:
                visited.add(next_pos)
                queue.push((next_pos, path + [action]))
    
    return None