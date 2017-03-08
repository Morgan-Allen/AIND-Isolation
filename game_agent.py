"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import math
import random


class Timeout(Exception):
    """ Subclass base exception for code clarity. """
    pass


def custom_score(game, player):
    player_rating, player_explored = find_accessible(game, player, 5)
    if player_rating == 0:
        return float("-inf")
    
    oppose_rating, oppose_explored = find_accessible(game, game.get_opponent(player), 5)
    if oppose_rating == 0:
        return float("inf")
    
    return player_rating - oppose_rating


def reflect_score(game, player):
    
    opponent = game.get_opponent(player)
    wide, high = game.width, game.height
    centre = (int(wide / 2), int(high / 2))
    own_pos = game.get_player_location(player)
    opp_pos = game.get_player_location(opponent)
    
    if game.move_count <= 2:
        if opp_pos == None:
            centre_dist = grid_distance(own_pos, centre)
            return 8 - centre_dist
        else:
            if own_pos in game.get_legal_moves(opponent):
                return -8
    
    elif player == game.__player_1__:
        xr, yr = wide - (1 + opp_pos[0]), high - (1 + opp_pos[1])
        if own_pos == (xr, yr):
            return 8
    
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(opponent))
    return own_moves - opp_moves


def improved_with_salt_score(game, player):
    #  This is essentially identical to the 'improved' heuristic, only we add
    #  a small random factor to throw off deterministic evaluation.
    if game.is_loser(player):
        return float("-inf")
    
    if game.is_winner(player):
        return float("inf")
    
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    spice = 1
    score = own_moves - opp_moves
    
    if game.active_player == player:
        score += random.random() * spice
    
    return score


def grid_distance(point_a, point_b):
    x = point_a[0] - point_b[0]
    y = point_a[1] - point_b[1]
    return math.sqrt((x * x) + (y * y))


def find_accessible(game, player, max_generation):
    explored = set()
    position = game.get_player_location(player)
    if position == None:
        return 0, explored
    
    directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                  (1, -2),  (1, 2), (2, -1),  (2, 1)]
    frontier = [position]
    access_rating = 1
    generation = 1
    
    while len(frontier) > 0 and generation <= max_generation:
        new_frontier = []
        
        for point in frontier:
            for direction in directions:
                new_x = point[0] + direction[0]
                new_y = point[1] + direction[1]
                new_point = (new_x, new_y)
                if not game.move_is_legal(new_point):
                    continue
                if new_point in explored:
                    continue
                explored.add(new_point)
                new_frontier.append(new_point)
                access_rating += 1. / generation
        
        frontier = new_frontier
        generation += 1
    
    return access_rating, explored




class CustomPlayer:

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout
    
    
    def get_move(self, game, legal_moves, time_left):
        self.time_left = time_left
        
        #  TODO:  Consider adding an opening book?
        
        max_depth = self.search_depth
        depth = 1 if self.iterative else max_depth
        last_move = (-1, -1)
        
        while max_depth <= 0 or depth <= max_depth:
            move = self.try_move(game, depth)
            if move == False:
                break
            last_move = move
            depth += 1
        return last_move
    
    
    def try_move(self, game, depth):
        move = (-1, -1)
        try:
            # The search method call (alpha beta or minimax) should happen in
            # here in order to avoid timeout. The try/except block will
            # automatically catch the exception raised by the search method
            # when the timer gets close to expiring
            
            if self.method == 'minimax':
                rating, move = self.minimax(game, depth)
            
            if self.method == 'alphabeta':
                rating, move = self.alphabeta(game, depth)
            
        except Timeout:
            # Handle any actions required at timeout, if necessary
            return False
        return move
    
    
    def minimax(self, game, depth, maximize=True):
        return self.alphabeta_common(game, depth, float("-inf"), float("inf"), maximize, False)
    
    
    def alphabeta(self, game, depth, lower_bound=float("-inf"), upper_bound=float("inf"), maximize=True):
        return self.alphabeta_common(game, depth, lower_bound, upper_bound, maximize, True)
    
    
    def alphabeta_common(self, game, depth, lower_bound, upper_bound, maximize, prune):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()
        
        move_picked = (-1, -1)
        best_score = float("-inf") if maximize else float("inf")
        
        for move in game.get_legal_moves():
            
            if prune and lower_bound >= upper_bound:
                break
            
            step = game.forecast_move(move)
            
            if depth <= 1:
                move_score = self.score(step, self)
            else:
                move_score, _ = self.alphabeta_common(step, depth - 1, lower_bound, upper_bound, not maximize, prune)
            
            if move_score > lower_bound and maximize:
                lower_bound = best_score = move_score
                move_picked = move
            
            if move_score < upper_bound and not maximize:
                upper_bound = best_score = move_score
                move_picked = move
        
        return best_score, move_picked





