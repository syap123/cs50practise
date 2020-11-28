"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    # count how many X or Os. Fewer Os means it is O's turn and vice-versa. Same Xs and Os means it is X turn since X starts first.
    """
    x_count = 0
    o_count = 0
    for row in board:
        for cell in row:
            if cell == X:
                x_count = x_count + 1
            if cell == O:
                o_count = o_count + 1                
    if x_count <= o_count:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions_set = set()
    i = 0
    for row in board:
        j = 0
        for cell in row:
            if cell is EMPTY:
                actions_set.add((i,j))
            j = j + 1
        i = i + 1
    return actions_set


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    #print(action)
    if board[action[0]][action[1]] is not EMPTY:
        raise Exception('Invalid move')
    else: 
        result_board = copy.deepcopy(board)
        result_board[action[0]][action[1]] = player(board)
    return result_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # for every cell in the board, check if the next 2 consecutive cells are moves from the same player. We only have to check to the right, down, down-left and down-right directions. 
    i = 0
    for row in board:
        j = 0
        for cell in row:
            potential_winner = cell
            # right direction
            if j == 0 and board[i][j + 1] == potential_winner and board[i][j + 2] == potential_winner:
                return potential_winner
            # down direction
            if i == 0 and board[i + 1][j] == potential_winner and board[i + 2][j] == potential_winner:
                return potential_winner                    
            # down-left
            if i == 0 and j == 2 and board[i + 1][j - 1] == potential_winner and board[i + 2][j - 2] == potential_winner:
                return potential_winner                                      
            # down-right
            if i == 0 and j == 0 and board[i + 1][j + 1] == potential_winner and board[i + 2][j + 2] == potential_winner:
                return potential_winner
            j = j + 1
        i = i + 1
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    elif len(actions(board)) == 0:
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0

def max_value(board,current_best_val):
    #global iteration
    #iteration = iteration + 1
    if terminal(board):
        return utility(board)
    best_utility_score_now = -999
    for action in actions(board):
        best_utility_score_now = max(best_utility_score_now, min_value(result(board,action),current_best_val))
        # the line below is an "early termination clause". Since the result of this function will always only be used to find a lower "current_best_val", I don't need to keep digging deeper under this action to find out how much higher the output will be
        if best_utility_score_now > current_best_val:
            return best_utility_score_now        
    return best_utility_score_now

def min_value(board,current_best_val):
    #global iteration
    #iteration = iteration + 1    
    if terminal(board):
        return utility(board)
    best_utility_score_now = 999
    for action in actions(board):
        best_utility_score_now = min(best_utility_score_now, max_value(result(board,action),current_best_val))
        # the line below is an "early termination clause". Since the result of this function will always only be used to find a higher "current_best_val", I don't need to keep digging deeper under this action to find out how much lower the output will be
        if best_utility_score_now < current_best_val:
            return best_utility_score_now
    return best_utility_score_now     

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    #global iteration
    #iteration = 0
    if player(board) == X:
        best_utility_score = -999
        best_action = None
        for action in actions(board):
            min_v = min_value(result(board,action),best_utility_score)
            if best_utility_score < min_v:
                best_utility_score = min_v
                best_action = action

    if player(board) == O:
        best_utility_score = 999
        best_action = None
        for action in actions(board):
            max_v = max_value(result(board,action),best_utility_score)
            if best_utility_score > max_v:
                best_utility_score = max_v
                best_action = action 
    #print(iteration)               
    #print(best_action)
    return best_action


