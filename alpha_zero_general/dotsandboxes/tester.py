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
        # Reset Score to 0



score = 0
n=6
m=6

# Create the empty board array.
boxes = [None]*n

# Create the empty board array.
# mask = [None]*n

for i in range(n):
    boxes[i] = [0]*m
    # mask[i] = [0]*m

legalMoves = dict()

temp = np.zeros((n,m))
print(temp)

# Set up the legalMoves.
# Centers the Inner Dimensions in the center and pads
# for i in range((n - innerN)/2,(n + innerN)/2):
for i in range(1,n-1):
    #     for j in range((n - innerM)/2,(m - innerM)/2):
    for j in range(1,m-1):
        # mask[i][j] = 1
        # Horizontal Move
        temp[i][j-1] += 1

        # Vertical Move
        temp[i-1][j] += 10


    # Last Horizontal
    # add_legal_move(i,(m - innerM)/2,0)
    temp[i][m - 2] += 1

# Last Verticals
# for j in range((n - innerM)/2,(m - innerM)/2):
for j in range(1,m-1):
    # add_legal_move((n + innerN)/2,j,1)
    temp[n-2][j] += 10

print(temp)
# TOCHECK turn to np.arrays
boxes = np.array(boxes)
# mask = np.array(mask)
#
# x2 = np.reshape(x,(4,4))
# pi_down_board = np.rot90(x2,3)
# pi_left_board = x2 * -1
#
# # Original version
# print("\nOriginal:\n")
# temp_pi_down = pi_down_board
# temp_pi_left = pi_left_board
#
# # Flipped
# print("\nRotated:\n")
# _get_rotated(board,temp_pi_down, temp_pi_left)




