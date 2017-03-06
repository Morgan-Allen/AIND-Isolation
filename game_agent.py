"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import random
from sample_players import open_move_score
from isolation import Board


class Timeout(Exception):
    """Subclass base exception for code clarity."""
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
    
    
    def get_move(self, game, legal_moves, time_left):

        self.time_left = time_left
        
        # TODO:  How do I figure out if this is an initial move?
        
        # Perform any required initializations, including selecting an initial
        # move from the game board (i.e., an opening book), or returning
        # immediately if there are no legal moves
        
        try:
            # The search method call (alpha beta or minimax) should happen in
            # here in order to avoid timeout. The try/except block will
            # automatically catch the exception raised by the search method
            # when the timer gets close to expiring
            
            if self.method == 'minimax':
                rating, (x, y) = self.minimax(game, 0, True)
                return (x, y)
            
            if self.method == 'alphabeta':
                rating, (x, y) = self.alphabeta(game, 0, True)
                return (x, y)
            
        except Timeout:
            # Handle any actions required at timeout, if necessary
            return (-1, -1)
        
        return (-1, -1)
    
    
    def minimax(self, game, depth, maximizing_player=True):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()
        
        #  TODO:  Get the set of all possible moves at the given time.  Create
        #  a copy of the board for each, apply the move, and pass along to the
        #  next iteration of minimax.
        
        best_rating = 0
        move_picked = (-1, -1)
        
        for move in game.legal_moves():
            step = game.copy()
            step.apply_move(move)
            
            move_rating = 0
            if depth == self.search_depth:
                move_rating = custom_score(game, self)
            else:
                move_rating, (x, y) = self.minimax(step, depth + 1, not maximizing_player)
            
            if not maximizing_player:
                move_rating *= -1
            
            if move_rating > best_rating:
                best_rating = move_rating
                move_picked = move
        
        return best_rating, move_picked
    
    
    def alphabeta(self, game, depth, lower_bound=float("-inf"), upper_bound=float("inf"), maximize=True):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()
        
        #  TODO:  If I recall correctly, alpha-beta pruning works by taking the
        #  upper/lower bounds for other values and excluding any values that
        #  can't affect the outcome.
        #  Alpha is presumably the lower bound, and Beta is presumably the
        #  upper bound.
        
        move_picked = (-1, -1)
        best_score = lower_bound if maximize else upper_bound
        
        for move in game.legal_moves():
            
            if lower_bound >= upper_bound:
                break
            
            step = game.copy()
            step.apply_move(move)
            
            if depth == self.search_depth:
                move_score = custom_score(game, self)
            elif maximize:
                move_score, (x, y) = self.alphabeta(step, depth + 1, lower_bound, float("inf"), False)
            else:
                move_score, (x, y) = self.alphabeta(step, depth + 1, float("-inf"), upper_bound, True)
            
            if move_score > lower_bound and maximize:
                lower_bound = move_score
                move_picked = move
            
            if move_score < lower_bound and not maximize:
                upper_bound = move_score
                move_picked = move
        
        return best_score, move_picked


if __name__ == '__main__':
    
    test_board = Board(4, 4)
    print(test_board.to_string())
    





