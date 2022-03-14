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
    """
    if terminal(board):
        return None
    else:
        x_count = 0
        o_count = 0
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == X:
                    x_count += 1
                elif board[i][j] == O:
                    o_count += 1
                else:
                    pass
        # in the initial game state, X gets the first move hence including the equal sign.
        if x_count <= o_count:
            return X
        else:
            return O

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    if terminal(board):
        return None
    else:
        possible_actions = set()
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] not in [X, O]:
                # != X and board[i][j] != O:
                    possible_actions.add((i, j))
        return possible_actions

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # put this if action is possible meaning the board is empty on the action part.
    if board[action[0]][action[1]] in [X, O]:
        raise Exception("The action is not vaild for the board.")
    else:
        new_board = copy.deepcopy(board)
        new_board[action[0]][action[1]] = player(board)
    return new_board

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    winner_sym = None
    primary_diag_flag = False
    secondary_diag_flag = False
    
    # primary diagonal check
    if all(element == board[0][0] for element in [board[i][i] for i in range(len(board))]) and board[0][0] is not None:
        primary_diag_flag = True
        winner_sym = board[0][0]
        
    # seceondary diagonal check
    if all(element == board[0][len(board)-1] for element in [board[i][len(board)-1-i] for i in range(len(board))]) and board[0][len(board)-1] is not None:
        secondary_diag_flag = True
        winner_sym = board[0][len(board)-1]

    if not (primary_diag_flag or secondary_diag_flag):
        for i in range(len(board)):
            #row checking
            if all(element == board[i][0] for element in board[i]) and board[i][0] is not None:
                # row_flag = True
                winner_sym = board[i][0]
                break
            #col checking
            if all(element == board[0][i] for element in [col[i] for col in board]) and board[0][i] is not None:
                # col_flag = True
                winner_sym = board[0][i]
                break
    return winner_sym # Not finished

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None or tie(board):
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

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    else:
        possible_actions = actions(board)
        if player(board) == X: # maximizing
            temp_dict = {action: min_value(result(board, action)) for action in possible_actions}
            return max(temp_dict, key=temp_dict.get)
        else: #minimizing
            temp_dict = {action: max_value(result(board, action)) for action in possible_actions}
            return min(temp_dict, key=temp_dict.get)

############################################### my functions below
def tie(board):
    draw_count = 0
    filled_count = 0
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] in [X, O]:
                filled_count += 1
    if filled_count == 9:
        return True
    else:
        return False

def max_value(board):
    # new_board = result(board, action)
    if terminal(board):
        return utility(board)
    else:
        v = -math.inf 
        for action in actions(board):
            v = max(v, min_value(result(board, action)))
        return v

def min_value(board):
    # new_board = result(board, action)
    if terminal(board):
        return utility(board)
    else:
        v = math.inf 
        for action in actions(board):
            v = min(v, max_value(result(board, action)))
        return v