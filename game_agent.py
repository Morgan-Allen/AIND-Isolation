"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""

from sample_players import open_move_score
from isolation import Board



class Timeout(Exception):
    #  TODO:  Subclass base exception for code clarity.
    pass


def custom_score(game, player):
    # TODO: Replace with custom implementation.
    return open_move_score(game, player)


class CustomPlayer:

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout
        self.verbose = False
    
    
    def get_move(self, game, legal_moves, time_left):
        self.time_left = time_left
        
        #  TODO:  Consider adding an opening book to evaluate moves?
        #  TODO:  You need to add iterative deepening as well!
        
        try:
            # The search method call (alpha beta or minimax) should happen in
            # here in order to avoid timeout. The try/except block will
            # automatically catch the exception raised by the search method
            # when the timer gets close to expiring
            
            if self.method == 'minimax':
                rating, (x, y) = self.minimax(game, 1, True)
                return (x, y)
            
            if self.method == 'alphabeta':
                rating, (x, y) = self.alphabeta(game, 1, True)
                return (x, y)
            
        except Timeout:
            # Handle any actions required at timeout, if necessary
            return (-1, -1)
        
        return (-1, -1)    
    
    
    def minimax(self, game, depth, maximize=True):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()
        
        #  TODO:  Get the set of all possible moves at the given time.  Create
        #  a copy of the board for each, apply the move, and pass along to the
        #  next iteration of minimax.
        
        verbose = depth == self.search_depth and self.verbose
        best_score = float("-inf") if maximize else float("inf")
        move_picked = (-1, -1)
        
        if verbose:
            print("Getting next minimax move, maximizing: ", maximize)
        
        for move in game.get_legal_moves():
            
            step = game.forecast_move(move)
            if verbose:
                print("  Checking move: ", move)
            
            move_score = 0
            if depth == self.search_depth:
                move_score = self.score(step, self)
            else:
                move_score, _ = self.minimax(step, depth + 1, not maximize)
            
            if verbose:
                print("  Score is: ", move_score)
            
            if (move_score > best_score and maximize) or (move_score < best_score and not maximize):
                best_score = move_score
                move_picked = move
        
        if verbose:
            print("  Best score:  ", best_score )
            print("  Move picked: ", move_picked)
        return best_score, move_picked
    
    
    def alphabeta(self, game, depth, lower_bound=float("-inf"), upper_bound=float("inf"), maximize=True):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()
        
        #  TODO:  If I recall correctly, alpha-beta pruning works by taking the
        #  upper/lower bounds for other values and excluding any values that
        #  can't affect the outcome.
        #  Alpha is presumably the lower bound, and Beta is presumably the
        #  upper bound.
        verbose = depth == self.search_depth and self.verbose
        
        move_picked = (-1, -1)
        best_score = lower_bound if maximize else upper_bound
        
        for move in game.get_legal_moves():
            
            if lower_bound >= upper_bound:
                break
            
            step = game.forecast_move(move)
            
            if depth == self.search_depth:
                move_score = self.score(step, self)
            elif maximize:
                move_score, _ = self.alphabeta(step, depth + 1, lower_bound, float("inf"), False)
            else:
                move_score, _ = self.alphabeta(step, depth + 1, float("-inf"), upper_bound, True)
            
            if move_score > lower_bound and maximize:
                lower_bound = move_score
                move_picked = move
            
            if move_score < lower_bound and not maximize:
                upper_bound = move_score
                move_picked = move
        
        if verbose:
            print("Getting next alphabeta move: ", move_picked)
        return best_score, move_picked


if __name__ == '__main__':
    
    player_1 = CustomPlayer(2)
    player_2 = CustomPlayer(2)
    test_board = Board(player_1, player_2, 4, 4)
    
    player_1.verbose = True
    test_board.play(1000)
    
    print(test_board.to_string())
    





