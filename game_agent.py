

import random


def accessibility_score(game, player):
    """
    Returns a game-state heuristic based on the overall accessibility of the
    board from the perspective of each player, based on the find_accessible
    function below.  Greater accessibility for the player and lower
    accessibility for their opponent increase the score.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The computed score for the current game state.
    """
    player_rating, player_explored = find_accessible(game, player, 5)
    if player_rating == 0:
        return float("-inf")
    
    oppose_rating, oppose_explored = find_accessible(game, game.get_opponent(player), 5)
    if oppose_rating == 0:
        return float("inf")
    
    return player_rating - oppose_rating


def find_accessible(game, player, max_generation):
    """
    Finds and returns all points on the board currently accessible from the
    player's position, together with an aggregate score that gives diminishing
    returns with the number of steps needed to reach there.
    (The max_generation argument limits how far the flood-fill will extend to
    help avoid timeouts.)
    """
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


def reflect_score(game, player):
    """
    Returns a game-state heuristic based on some of the winning gambits
    described in the 'Solving 5x5 Isolation' lecture.  Players will attempt to
    claim the centre square during their opening moves- and failing that, stay
    out of positions which their opponent can mirror.  After that, player 1
    will attempt to mirror their opponent whenever possible.  If that's not
    possible, we fall back on the default 'improved' heuristic based on
    maximising your own freedom of movement and denying that of your opponent.
    
    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The computed score for the current game state.
    """
    
    opponent = game.get_opponent(player)
    wide, high = game.width, game.height
    centre = (int(wide / 2), int(high / 2))
    own_pos = game.get_player_location(player)
    opp_pos = game.get_player_location(opponent)
    
    if game.move_count <= 2:
        if opp_pos == None:
            return 8 if own_pos == centre else 0
        elif own_pos in game.get_legal_moves(opponent) and opp_pos == centre:
            return -8
    
    elif player == game.__player_1__:
        xr, yr = wide - (1 + opp_pos[0]), high - (1 + opp_pos[1])
        if own_pos == (xr, yr):
            return 8
    
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(opponent))
    return own_moves - opp_moves


def improved_with_salt_score(game, player):
    """
    Returns a game-state heuristic identical to the default 'improved'
    heuristic, based on maximising your own freedom of movement and denying
    that of your opponent, but with a small random 'spice' during the player's
    own turn to try and throw off deterministic evaluation.
    
    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The computed score for the current game state.
    """
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



class Timeout(Exception):
    """
    Subclasses Exception for code clarity.
    """
    pass


class CustomPlayer:
    
    def __init__(self, search_depth=3, score_fn=accessibility_score,
                 iterative=True, method='alphabeta', timeout=10.):
        """
        Game-playing agent that chooses a move using a specified evaluation
        function, depth-limited minimax algorithm, alpha-beta pruning and/or
        iterative-deepening search.
        
        Parameters
        ----------
        search_depth : int (optional)
            A strictly positive integer (i.e., 1, 2, 3,...) for the number of
            layers in the game tree to explore for fixed-depth search. (i.e., a
            depth of one (1) would only explore the immediate sucessors of the
            current state.)  Set to -1 to remove any search-depth restriction.
        
        score_fn : callable (optional)
            A function to use for heuristic evaluation of game states.
        
        iterative : boolean (optional)
            Flag indicating whether to perform fixed-depth search (False) or
            iterative deepening search (True).
        
        method : {'minimax', 'alphabeta'} (optional)
            The name of the search method to use in get_move().
        
        timeout : float (optional)
            Time remaining (in milliseconds) when search is aborted. Should be
            a positive value large enough to allow the function to return
            before the timer expires.
        """
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout
    
    
    def get_move(self, game, legal_moves, time_left):
        """
        Searches for the best move from the available legal moves and returns
        a result before the time limit expires.  Will use iterative deepening
        in combination with either minimax or alphabeta if the appropriate
        constructor arguments were set.
        
        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        
        self.time_left = time_left
        
        max_depth = self.search_depth
        depth = 1 if self.iterative else max_depth
        best_move = (-1, -1)
        
        while max_depth <= 0 or depth <= max_depth:
            move = self.try_move(game, depth)
            if move == False:
                break
            best_move = move
            depth += 1
        return best_move
    
    
    def try_move(self, game, depth):
        """
        Performs a single depth-limited move-search attempt (either once
        within non-iterative or repeatedly within iterative-deepening.)
        """
        move = (-1, -1)
        try:
            
            if self.method == 'minimax':
                rating, move = self.minimax(game, depth)
            
            if self.method == 'alphabeta':
                rating, move = self.alphabeta(game, depth)
            
        except Timeout:
            return False
        
        return move
    
    
    def minimax(self, game, depth, maximize=True):
        """
        Implements minimax by calling alphabeta_common *without* pruning.
        """
        return self.alphabeta_common(game, depth, float("-inf"), float("inf"), maximize, False)
    
    
    def alphabeta(self, game, depth, lower_bound=float("-inf"), upper_bound=float("inf"), maximize=True):
        """
        Implements alphabeta by calling alphabeta_common *with* pruning.
        """
        return self.alphabeta_common(game, depth, lower_bound, upper_bound, maximize, True)
    
    
    def alphabeta_common(self, game, depth, lower_bound, upper_bound, maximize, prune):
        """
        Implements the alphabeta search algorithm as described in the lectures,
        with an option to ignore pruning (thus becoming equivalent to minimax.)
        
        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state
        
        depth : int
            How deep to search in the game tree before returning with a
            heuristic estimate of the move-score.
        
        lower_bound : float
            Places a lower bound of search on minimizing layers
        
        upper_bound : float
            Places an upper bound of search on maximizing layers
        
        maximize : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)
        
        Returns
        -------
        float
            The score for the current search branch
        
        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves
        """
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





