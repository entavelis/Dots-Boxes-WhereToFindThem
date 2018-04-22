from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
from .DnBLogic import Board
import numpy as np


class DnBGame(Game):
    def __init__(self, n, m):
        self.n = n

    def getInitBoard(self):
        # return initial board (numpy board)
        b = Board(self.n, self.m)
        return np.array(b.boxes)

    def getBoardSize(self):
        # (a,b) tuple
        return (self.n, self.m)

    def getActionSize(self):
        # return number of actions
        return 2*self.n*self.m + self.m + self.n

    def getNextState(self, board, action, player):
        # if player takes action on board, return next (board,player)
        # action must be a valid move

        b = Board(self.n)
        b.boxes = np.copy(board)
        move = (int(action/self.n), action%self.n)

        # checks if the box is filled
        plays_again = b.execute_move(move)

        return b.boxes, (player if plays_again else -player)

    def getValidMoves(self, board):
        # return a fixed size binary vector
        valids = [0]*self.getActionSize()
        b = Board(self.n, self.m)
        b.boxes = np.copy(board)
        legalMoves = b.get_legal_moves()

        # if len(legalMoves)==0:
        #     valids[-1]=1
        #     return np.array(valids)

        # D is for direction
        for x, y, d in legalMoves:
            valids[(self.n*x+y)*2 + d] = 1
        return np.array(valids)

    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1
        b = Board(self.n)
        b.boxes = np.copy(board)
        if b.has_legal_moves(player):
            return 0
        if b.has_legal_moves(-player):
            return 0
        if b.countDiff(player) > 0:
            return 1
        return -1

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        return board

    def getSymmetries(self, board, pi):
        # mirror, rotational
        assert(len(pi) == self.n*self.m+1)  # 1 for pass
        pi_board = np.reshape(pi[:-1], (self.m, self.n))
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

    def stringRepresentation(self, board):
        # 8x8 numpy array (canonical board)
        return board.tostring()

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
