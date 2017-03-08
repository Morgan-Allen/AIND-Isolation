"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""



class Timeout(Exception):
    #  TODO:  Subclass base exception for code clarity.
    pass


def reflect_score(game, player):
    wide, high = game.width, game.height
    xp, yp = game.get_player_location(player)
    
    if xp == wide / 2 and yp == high / 2:
        return wide * high
    
    opp_xy = game.get_player_location(game.get_opponent(player))
    if opp_xy != None:
        xo, yo = opp_xy
        xr, yr = wide - (1 + xo), high - (1 + yo)
        if xp == xr and yp == yr:
            return wide * high
    
    return custom_score(game, player)


def partition_score(game, player):
    player_rating, player_explored = find_accessible(game, player)
    oppose_rating, oppose_explored = find_accessible(game, game.get_opponent(player))
    return player_rating - oppose_rating


def find_accessible(game, player):
    explored = set()
    position = game.get_player_location(player)
    if position == None:
        return 0, explored
    
    directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                  (1, -2),  (1, 2), (2, -1),  (2, 1)]
    frontier = [position]
    access_rating = 1
    generation = 1
    
    while len(frontier) > 0:
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


def custom_score(game, player):
    #  TODO:  This is the same as the 'improved' heuristic from
    #  sample_players.py.  Come up with something new?
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    return float(own_moves - opp_moves)


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





