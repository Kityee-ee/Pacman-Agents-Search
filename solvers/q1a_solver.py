#---------------------#
# DO NOT MODIFY BEGIN #
#---------------------#

import logging

import util
from problems.q1a_problem import q1a_problem

def q1a_solver(problem: q1a_problem):
    astarData = astar_initialise(problem)
    num_expansions = 0
    terminate = False
    while not terminate:
        num_expansions += 1
        terminate, result = astar_loop_body(problem, astarData)
    print(f'Number of node expansions: {num_expansions}')
    return result

#-------------------#
# DO NOT MODIFY END #
#-------------------#

class AStarData:
    # YOUR CODE HERE
    def __init__(self):
        # create frontier, actual cost (gn) and path 
        # self.frontier = []
        self.frontier = util.PriorityQueue() #expands lowest cost node first
        self.explored = set()
        self.g_cost = {}
        self.path = {}


def astar_initialise(problem: q1a_problem):
    # YOUR CODE HERE
    astarData = AStarData()
    start_state = problem.getStartState()
    
    # Get the goal state (first food dot) and store it
    food_list = problem.startingGameState.getFood().asList()
    astarData.goal_state = food_list[0] if food_list else None
    
    # Initialize costs and frontier
    astarData.g_cost[start_state] = 0
    
    # Calculate heuristic for start state
    h_cost = astar_heuristic(start_state, astarData.goal_state) if astarData.goal_state else 0
    
    # Push to frontier with priority = h_cost (since g_cost = 0)
    astarData.frontier.push((start_state, 0), h_cost)
    
    return astarData

def astar_loop_body(problem: q1a_problem, astarData: AStarData):
    # YOUR CODE HERE
    # return terminate (bool) , path (list)

    # Check if frontier is empty
    if astarData.frontier.isEmpty():
        return True, []
    
    # Pop the node with lowest f(n)
    current_state, current_g_cost = astarData.frontier.pop()
    
    # Check if goal reached (at food dot)
    if problem.isGoalState(current_state):
        # Reconstruct path
        path = []
        state = current_state
        while state in astarData.path:
            prev_state, action = astarData.path[state]
            path.append(action)
            state = prev_state
        return True, path[::-1]
    
    # Add to explored set
    astarData.explored.add(current_state)
    
    # Expand current state
    for successor, action, step_cost in problem.getSuccessors(current_state):
        # Skip if already explored
        if successor in astarData.explored:
            continue
        
        # Calculate new g(n)
        new_g_cost = current_g_cost + step_cost
        
        # Check if we found a better path to successor
        if successor not in astarData.g_cost or new_g_cost < astarData.g_cost[successor]:
            # Update costs and path
            astarData.g_cost[successor] = new_g_cost
            astarData.path[successor] = (current_state, action)
            
            # Calculate f(n) = g(n) + h(n)
            f_cost = new_g_cost + astar_heuristic(successor, astarData.goal_state)
            
            # Add to frontier
            astarData.frontier.push((successor, new_g_cost), f_cost)
    
    return False, []

def astar_heuristic(current, goal):
    # YOUR CODE HERE
    x1, y1 = current 
    x2, y2 = goal 
    return abs(x1 - x2) + abs(y1 - y2)
