

import random
import math


MAX_VAL = float("inf")
MIN_VAL = float("-inf")


def custom_score(game, player):
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
        return MIN_VAL
    
    oppose_rating, oppose_explored = find_accessible(game, game.get_opponent(player), 5)
    if oppose_rating == 0:
        return MAX_VAL
    
    spice = 1
    score = player_rating - oppose_rating
    
    if game.active_player == player:
        score += random.random() * spice
    
    return score


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
    possible, we fall back on the custom_score heuristic based on maximising
    your own freedom of movement and denying that of your opponent.
    
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
    max_score = wide * high
    
    if game.move_count <= 2:
        if opp_pos == None:
            return max_score if own_pos == centre else 0
        elif own_pos in game.get_legal_moves(opponent) and opp_pos == centre:
            return -max_score
    
    elif player == game.__player_1__:
        xr, yr = wide - (1 + opp_pos[0]), high - (1 + opp_pos[1])
        if own_pos == (xr, yr):
            return max_score
    
    return custom_score(game, player)


def improved_salt_score(game, player):
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
        return MIN_VAL
    
    if game.is_winner(player):
        return MAX_VAL
    
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    spice = 1
    score = own_moves - opp_moves
    
    if game.active_player == player:
        score += random.random() * spice
    
    return score



"""
Assorted directional constants used during rotations (see below.)
"""
CACHE_VERBOSE = False
NORTH  = 0
EAST   = 1
SOUTH  = 2
WEST   = 3
DIAG_1 = 4
DIAG_2 = 5
HORIZ  = 6
VERT   = 8
RECT_ROTATIONS = [NORTH, SOUTH, HORIZ, VERT]


def custom_cached_score(game, player):
    """
    Returns a game-state heuristic based on the custom_score heuristic, but
    that attempts to cache score-values based on the current board-layout
    under various symmetries.
    
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
    keys = [hash_key(game, rotation) for rotation in RECT_ROTATIONS]
    
    for key in keys:
        if key in player.score_cache:
            player.cache_hits += 1
            return player.score_cache[key]
    
    score = custom_score(game, player)
    player.cache_misses += 1
    
    if CACHE_VERBOSE and player.cache_misses % 1000 == 0:
        print("Cached keys for board were: ", keys)
    
    if len(player.score_cache) < player.MAX_CACHE_SIZE and game.move_count < player.MAX_CACHE_DEPTH:
        for key in keys:
            player.score_cache[key] = score
    
    return score


def hash_key(game, rotation):
    """
    Returns a hash-key for the give game-board under a specific rotation,
    which is applied to all occupied spaces and the players' current
    coordinates.
    
    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).
    
    rotation : { NORTH, SOUTH, EAST, WEST, DIAG_1, DIAG_2, HORIZ, VERT }
        A rotation to apply to internal x/y coordinates.

    Returns
    -------
    str
        A string-hash-key based on appending together player coordinates and
        those of any occupied spaces.
    """
    x1, y1 = game.get_player_location(game.__player_1__)
    x2, y2 = game.get_player_location(game.__player_2__)
    x1, y1 = (rotate_coord(game, x1, y1, rotation))
    x2, y2 = (rotate_coord(game, x2, y2, rotation))
    key = [x1, y1, x2, y2]
    
    for x in range(game.width):
        for y in range(game.height):
            x, y = rotate_coord(game, x, y, rotation)
            if game.__board_state__[x][y] != game.BLANK:
                key.append(x)
                key.append(y)
    
    return str(key)


def rotate_coord(game, x, y, rotation):
    """
    Rotates the given x/y coordinates within the board space.
    
    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).
    
    x : int
        The x coordinate
    
    y : int
        The y coordinate
    
    rotation : { NORTH, SOUTH, EAST, WEST, DIAG_1, DIAG_2, HORIZ, VERT }
        A rotation to apply to internal x/y coordinates.

    Returns
    -------
    (int, int)
        The given board coordinates under the appropriate rotation.
    """
    off_h = game.width  - 1
    off_v = game.height - 1
    
    if (rotation == NORTH):
        pass
    if (rotation == SOUTH):
        x, y = off_h - x, off_v - y
    if (rotation == EAST):
        x, y = y, off_h - x
    if (rotation == WEST):
        x, y = off_v - y, x
    if (rotation == HORIZ):
        x, y = off_h - x, y
    if (rotation == VERT):
        x, y = x, off_v - y
    if (rotation == DIAG_1):
        x, y = y, x
    if (rotation == DIAG_2):
        x, y = off_v - y, off_h - x
    return x, y



def centred_score(game, player):
    """
    Returns a game-state heuristic based on the number of legal moves
    available to each player, but adjusted for distance from the centre of the
    board.  In addition, the final score is divided by sum of scores for both
    players.
    
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
    own_moves = len(game.get_legal_moves(player))
    if own_moves == 0:
        return MIN_VAL
    
    opp_moves = len(game.get_legal_moves(opponent))
    if opp_moves == 0:
        return MAX_VAL
    
    own_moves *= centre_factor(game, player)
    opp_moves *= centre_factor(game, opponent)
    return own_moves / (own_moves + opp_moves)


def centre_factor(game, player):
    """
    Returns a factor based off the euclidean distance to the centre of the
    board, relative to maximum dimensions.
    """
    x, y = game.get_player_location(player)
    dx, dy = x - game.width / 2., y - game.height / 2.
    dist = math.sqrt((dx * dx) + (dy * dy))
    maxWide = max(game.width, game.height)
    return maxWide / (maxWide + dist)



class Timeout(Exception):
    """
    Subclasses Exception for code clarity.
    """
    pass


class CustomPlayer:
    
    score_cache = {}
    MAX_CACHE_DEPTH = 4
    MAX_CACHE_SIZE = 40000
    cache_hits = 0
    cache_misses = 0
    
    def __init__(self, search_depth=3, score_fn=custom_score,
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
        
        if CACHE_VERBOSE and self.cache_misses > 0:
            print("CACHE HITS/MISSES: ", self.cache_hits, "/", self.cache_misses)
        
        return best_move
    
    
    def try_move(self, game, depth):
        """
        Performs a single depth-limited move-search attempt (either once
        within non-iterative or repeatedly within iterative-deepening.)  See
        get_move, above, for details.
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
        Implements minimax by calling alphabeta_common *without* pruning.  See
        alphabeta_common below for details.
        """
        return self.alphabeta_common(game, depth, MIN_VAL, MAX_VAL, maximize, False)
    
    
    def alphabeta(self, game, depth, lower_bound=MIN_VAL, upper_bound=MAX_VAL, maximize=True):
        """
        Implements alphabeta by calling alphabeta_common *with* pruning.  See
        alphabeta_common below for details.
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
        
        prune : bool
            Flag indicating whether to prune branches that cannot contribute
            to the final outcome
        
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
        best_score = MIN_VAL if maximize else MAX_VAL
        
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





