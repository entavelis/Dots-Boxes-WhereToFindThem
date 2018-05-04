import numpy as np

def _get_flipped(board, down, left):
    temp_board = np.fliplr(board)
    temp_down = np.fliplr(down)
    temp_left = _pi_fliplr(left)

    print(board)
    print(temp_board)

    print(down)
    print(temp_down)

    print(left)
    print(temp_left)

def _get_rotated(board, down, left):
    '''
    Rotated the Board and Pi boards by 90 according to conventions and returns the right result
    :param board:
    :param down:
    :param left:
    :return:
    '''
    temp_board = np.rot90(board)
    temp_down = np.roll(np.rot90(left),-1,0)
    temp_left = np.rot90(down)

    print(board)
    print(temp_board)

    print(down)
    print(temp_down)

    print(left)
    print(temp_left)

def _pi_fliplr(board):
    '''
    Flips the pi boards left to right according to our conventions
    :return: the flipped board
    '''
    return np.roll(np.fliplr(board),-1,1)

def _pi_flipud(board):
    '''
    Flips the pi boards up to down according to our conventions
    :return: the flipped board
    '''
    return np.roll(np.flipud(board),0,0)

board = np.reshape([0]*5 + [10,20] + [0,0] + [30,40] + [0]*5,(4,4))
x = [0]*4 + [1,2,3] + [0] + [4,5,6] + [0]*5


x2 = np.reshape(x,(4,4))
pi_down_board = np.rot90(x2,3)
pi_left_board = x2 * -1

# Original version
print("\nOriginal:\n")
temp_pi_down = pi_down_board
temp_pi_left = pi_left_board

# Flipped
print("\nRotated:\n")
_get_rotated(board,temp_pi_down, temp_pi_left)




