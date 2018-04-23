from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
from .DnBLogic import Board
import numpy as np


class DnBGame(Game):
    def __init__(self, n, m, maxboard = 10):
        "Set up initial board configuration."

        # We have a maximum board size as fixed and then we fix smaller boards at its center and pad
        self.maxboard = maxboard

        self.n = self.maxboard + 2;
        self.m = self.maxboard + 2;
        self.legalMoves=[]

        self.innerN = n
        self.innerM = m



    def reset_game(self):
        # Reset Score to 0
        self.score = 0

        # Create the empty board array.
        self.boxes = [None]*self.n

        # Create the empty board array.
        self.mask = [None]*self.n

        for i in range(self.n):
            self.boxes[i] = [0]*self.m
            self.mask[i] = [0]*self.m

        self.legalMoves = dict()

        # Set up the legalMoves.
        # Centers the Inner Dimensions in the center and pads
        for i in range((self.n - self.innerN)/2,(self.n + self.innerN)/2):
            for j in range((self.n - self.innerM)/2,(self.m - self.innerM)/2):
                self.mask[i][j] = 1
                # Horizontal Move
                self.add_legal_move(i,j-1,0)

                # Vertical Move
                self.add_legal_move(i-1,j,1)


            # Last Horizontal
            self.add_legal_move(i,(self.m - self.innerM)/2,0)

        # Last Verticals
        for j in range((self.n - self.innerM)/2,(self.m - self.innerM)/2):
            self.add_legal_move((self.n + self.innerN)/2,j,1)

        # TOCHECK turn to np.arrays
        self.boxes = np.array(self.boxes)
        self.mask = np.array(self.mask)

    # add [][] indexer syntax to the Board
    def __getitem__(self, index):
        return self.boxes[index]

    def add_legal_move(self, x, y, d):
        self.legalMoves[(self.innerN*x+y)*2 + d] = (x,y,d)

    def pop_legal_move(self, move):
        x = move[0]
        y = move[1]
        d = move[2]

        return self.legalMoves.pop((self.innerN*x+y)*2 + d, None)


    def get_legal_moves(self):
        return self.legalMoves


    def has_legal_moves(self):
        return len(self.legalMoves)>0;

    def execute_move(self, move, player):
        """
        Executes the move, removes it from the legal moves and adjusts the score
        :param move: the tuple x,y,direction
        :param player: 1 for player 1 and -1 for player 2
        :return: return if the player has to play again
        """


        # Count to see if we have any boxes filled this game
        plays_again = 0

        # Change board state
        self.boxes[move[0]][move[1]]+=1
        plays_again += self.boxes[move[0]][move[1]] == 4

        if move[2]:
            self.boxes[move[0]+1][move[1]] += 1
            plays_again += self.boxes[move[0]+1][move[1]] == 4
        else:
            self.boxes[move[0]][move[1]+1] += 1
            plays_again += self.boxes[move[0]][move[1]+1] == 4


        # Remove Move from Legal Moves O(1)
        self.remove_legal_move(move)

        # Adjust Score
        self.score += player * plays_again

        return plays_again

    # Returns the augmented game board with padding
    def getBoardSize(self):
        # (a,b) tuple
        return (self.n, self.m)

    # Returns the actions size with padded actions
    def getActionSize(self):
        # return number of actions
        # we put some extra invalid actions in
        return 2*(self.n)*(self.m)

    def getNextState(self, action, player):
        # if player takes action on board, return next (board,player)
        # action must be a valid move

        # Gets and removes the action out of the legal moves
        move = self.pop_legal_move(action)

        # checks if the box is filled
        plays_again = b.execute_move(move)

        return (player if plays_again else -player)

    def getValidMoves(self, board):
        # return a fixed size binary vector
        valids = [0]*self.getActionSize()

        # Our key is a action to mapping Dictionary
        for key in self.legalMoves.keys:
            valids[key] = 1
        return np.array(valids)

    # change implementation to for draw
    def getGameEnded(self):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1
        if self.has_legal_moves():
            return 0

        # Checks for draw
        if not b.score:
            # draw has a very little value
            return 1e-4

        return np.sign(b.score)


    # Maybe we should set this to turn boards so n>m
    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        return board

    def getSymmetries(self,  pi):

        board = copy(self.boxes)
        # mirror, rotational
        assert(len(pi) == 2*self.n*self.m)  # 1 for pass
        pi_board = np.reshape(pi[:-1], (self.m, self.n, 2)) # Check this: We have 2 moves for each box -> how to?
        l = []

        for i in range(1, 5):
            for j in [True, False]:
                newB = np.rot90(board, i)
                newPi = np.rot90(pi_board, i)
                if j:
                    newB = np.fliplr(newB)
                    newPi = np.fliplr(newPi)
                l += [(newB, list(newPi.ravel()) + [pi[-1]])]
        return l

    def stringRepresentation(self):
        # 8x8 numpy array (canonical board)
        return boxes.tostring()

def display(board):
    n = board.shape[0]

    for y in range(n):
        print (y,"|",end="")
    print("")
    print(" -----------------------")
    for y in range(n):
        print(y, "|",end="")    # print the row #
        for x in range(n):
            piece = board[y][x]    # get the piece to print
            if piece == -1: print("b ",end="")
            elif piece == 1: print("W ",end="")
            else:
                if x==n:
                    print("-",end="")
                else:
                    print("- ",end="")
        print("|")

    print("   -----------------------")
