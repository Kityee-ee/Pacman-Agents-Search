#---------------------#
# DO NOT MODIFY BEGIN #
#---------------------#

import logging

import util
from problems.q1b_problem import q1b_problem

def q1b_solver(problem: q1b_problem):
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
    def __init__(self):
        self.frontier = util.PriorityQueue()  # Expands lowest cost node first
        self.explored = set()
        self.g_cost = {}
        self.path = {}
        self.target_food = None  # Store the target food dot
        self.frontier_nodes = set()  # Track nodes in frontier

def is_reachable(start, goal, game_state):
    """
    Check if a goal position is reachable from the start position using BFS.
    """
    queue = util.Queue()
    queue.push(start)
    visited = set([start])
    
    while not queue.isEmpty():
        pos = queue.pop()
        
        if pos == goal:
            return True
            
        x, y = pos
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Four directions
            next_x, next_y = x + dx, y + dy
            next_pos = (next_x, next_y)
            
            if not game_state.hasWall(next_x, next_y) and next_pos not in visited:
                queue.push(next_pos)
                visited.add(next_pos)
    
    return False

def count_surrounding_walls(pos, game_state):
    """
    Count the number of walls surrounding a position.
    Returns a lower number for positions with fewer obstacles.
    """
    x, y = pos
    walls = 0
    
    # Check all four directions
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        next_x, next_y = x + dx, y + dy
        if game_state.hasWall(next_x, next_y):
            walls += 1
    
    return walls

def find_reachable_food(start, food_list, game_state):
    """
    Find all reachable food dots from the start position using a single BFS.
    Returns a list of reachable food positions.
    """
    queue = util.Queue()
    queue.push(start)
    visited = set([start])
    reachable_food = []
    
    while not queue.isEmpty():
        pos = queue.pop()
        
        # Check if this position has food
        if pos in food_list:
            reachable_food.append(pos)
            
        x, y = pos
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Four directions
            next_x, next_y = x + dx, y + dy
            next_pos = (next_x, next_y)
            
            if not game_state.hasWall(next_x, next_y) and next_pos not in visited:
                queue.push(next_pos)
                visited.add(next_pos)
    
    return reachable_food

def astar_initialise(problem: q1b_problem):
    astarData = AStarData()
    start_state = problem.getStartState()
    food_list = problem.startingGameState.getFood().asList()
    
    # Find all reachable food dots in one BFS
    reachable_food = find_reachable_food(start_state, food_list, problem.startingGameState)
    
    # Select the closest reachable food dot
    if reachable_food:
        min_distance = float('inf')
        min_walls = float('inf')  # For tiebreaking
        
        for food_pos in reachable_food:
            x1, y1 = start_state
            x2, y2 = food_pos
            distance = abs(x1 - x2) + abs(y1 - y2)
            
            # Count walls around this food dot
            walls = count_surrounding_walls(food_pos, problem.startingGameState)
            
            # Update if this is a better choice
            if distance < min_distance or (distance == min_distance and walls < min_walls):
                min_distance = distance
                min_walls = walls
                astarData.target_food = food_pos
    
    # If no reachable food found, return empty path
    if not astarData.target_food:
        return astarData
    
    astarData.g_cost[start_state] = 0
    h_cost = astar_heuristic(start_state, astarData.target_food)
    astarData.frontier.push((start_state, 0), h_cost)
    astarData.frontier_nodes.add(start_state)  # Add start state to frontier tracking
    
    return astarData

def astar_loop_body(problem: q1b_problem, astarData: AStarData):
    if astarData.frontier.isEmpty():
        return True, []
    
    current_state, current_g_cost = astarData.frontier.pop()
    # Safely remove from frontier tracking if it exists
    if current_state in astarData.frontier_nodes:
        astarData.frontier_nodes.remove(current_state)
    
    if problem.isGoalState(current_state):
        path = []
        state = current_state
        while state in astarData.path:
            prev_state, action = astarData.path[state]
            path.append(action)
            state = prev_state
        return True, path[::-1]
    
    astarData.explored.add(current_state)
    
    # Check if current position is a dead end
    successors = list(problem.getSuccessors(current_state))
    if len(successors) == 1:
        # Dead end - only one way to go
        successor, action, step_cost = successors[0]
        if successor not in astarData.explored:
            new_g_cost = current_g_cost + step_cost
            if successor not in astarData.g_cost or new_g_cost < astarData.g_cost[successor]:
                astarData.g_cost[successor] = new_g_cost
                astarData.path[successor] = (current_state, action)
                f_cost = new_g_cost + astar_heuristic(successor, astarData.target_food)
                
                if successor in astarData.frontier_nodes:
                    astarData.frontier.update((successor, new_g_cost), f_cost)
                else:
                    astarData.frontier.push((successor, new_g_cost), f_cost)
                    astarData.frontier_nodes.add(successor)
        return False, []
    
    # Calculate current distance to target
    current_x, current_y = current_state
    target_x, target_y = astarData.target_food
    current_dist = abs(current_x - target_x) + abs(current_y - target_y)
    
    # Sort successors by how much they move towards the target
    successors_with_priority = []
    for successor, action, step_cost in successors:
        new_g_cost = current_g_cost + step_cost
        
        # Skip if successor is explored and we don't have a better path
        if successor in astarData.explored:
            if successor in astarData.g_cost and new_g_cost >= astarData.g_cost[successor]:
                continue
            # If we found a better path, remove from explored to allow re-expansion
            astarData.explored.remove(successor)
            
        # Calculate new distance to target
        new_x, new_y = successor
        new_dist = abs(new_x - target_x) + abs(new_y - target_y)
        
        # Calculate improvement (negative means moving away from target)
        improvement = current_dist - new_dist
        
        # Add to list with priority
        successors_with_priority.append((successor, action, step_cost, improvement))
    
    # Sort successors by improvement (highest first)
    successors_with_priority.sort(key=lambda x: x[3], reverse=True)
    
    # Process successors in order of improvement
    for successor, action, step_cost, _ in successors_with_priority:
        new_g_cost = current_g_cost + step_cost
        
        # Only update if we found a better path
        if successor not in astarData.g_cost or new_g_cost < astarData.g_cost[successor]:
            astarData.g_cost[successor] = new_g_cost
            astarData.path[successor] = (current_state, action)
            
            # Calculate new f_cost
            f_cost = new_g_cost + astar_heuristic(successor, astarData.target_food)
            
            # Always use update if node is in frontier
            if successor in astarData.frontier_nodes:
                astarData.frontier.update((successor, new_g_cost), f_cost)
            else:
                astarData.frontier.push((successor, new_g_cost), f_cost)
                astarData.frontier_nodes.add(successor)
    
    return False, []

def astar_heuristic(current, target_food):
    """
    A simple heuristic using Manhattan distance to the target food dot.
    """
    if not target_food:
        return 0
    
    # Calculate Manhattan distance to the target food
    x1, y1 = current
    x2, y2 = target_food
    return abs(x1 - x2) + abs(y1 - y2)