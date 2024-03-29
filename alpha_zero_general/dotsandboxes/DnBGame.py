from __future__ import print_function
import sys
sys.path.append('..')
import numpy as np


class DnBGame():
    def __init__(self, n, m, maxboard = 10):
        "Set up initial board configuration."

        # We have a maximum board size as fixed and then we fix smaller boards at its center and pad
        # self.maxboard = maxboard

        self.n = n + 2;
        self.m = m + 2;
        # self.legalMoves=[]

        self.innerN = n
        self.innerM = m





    def reset_game(self):
        # Reset Score to 0
        self.score = 0

        self.moves_played = []

        # Create the empty board array.
        self.boxes = [None]*self.n

        # Create the empty board array.
        # self.mask = [None]*self.n

        for i in range(self.n):
            self.boxes[i] = [-5]*self.m
            # self.boxes[i] = [0]*self.m

        # ATTENTION: Do I even need to store the tuple or just the hash? Check Implementation as Java's BitSet or just have the
        self.legalMoves = dict()

        # Last Verticals
        # for j in range((self.n - self.innerM)/2,(self.m - self.innerM)/2):
        for j in range(1,self.m-1):
            # self.add_legal_move((self.n + self.innerN)/2,j,1)
            self.add_legal_move(0,j,1)

        # Set up the legalMoves.
        # Centers the Inner Dimensions in the center and pads
        # for i in range((self.n - self.innerN)/2,(self.n + self.innerN)/2):
        for i in range(1,self.n-1):
            # self.add_legal_move(i,(self.m - self.innerM)/2,0)
            self.add_legal_move(i,0,0)

        #     for j in range((self.n - self.innerM)/2,(self.m - self.innerM)/2):
            for j in range(1,self.m-1):
                # self.mask[i][j] = 1
                self.boxes[i][j]=0
                # Horizontal (left) Move -> 0
                self.add_legal_move(i,j,0)

                # Vertical (down) Move -> 1
                self.add_legal_move(i,j,1)


            # Last Horizontal

        # TOCHECK turn to np.arrays
        self.boxes = np.array(self.boxes)
        # self.mask = np.array(self.mask)

        # self.print_legal_moves()

    # add [][] indexer syntax to the Board
    def __getitem__(self, index):
        return self.boxes[index]

    def add_legal_move(self, x, y, d):
        # Check legal moves sizes.legalMoves
        # self.legalMoves[(self.innerN*x+y)*2 + d] = (x,y,d)
        self.legalMoves[(self.m*x+y)*2 + d] = (x,y,d)

    def numberLegalMoves(self):
        return len(self.legalMoves)

    def getLegalMoves(self):
        return self.legalMoves

    def getLegalKeys(self):
        return self.legalMoves.keys()

    def isValidMove(self,action):
        return action in self.legalMoves

    def hasLegalMoves(self):
        return len(self.legalMoves)>0;

    def executeMove(self, move, player):
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
        # self.boxes[move[0]][move[1]]+=0.25
        plays_again += self.boxes[move[0]][move[1]] == 4
        # plays_again += int(self.boxes[move[0]][move[1]])

        if move[2]:
            self.boxes[move[0]+1][move[1]] += 1
            # self.boxes[move[0]+1][move[1]] += 0.25
            plays_again += self.boxes[move[0]+1][move[1]] == 4
            # plays_again += int(self.boxes[move[0]+1][move[1]])
        else:
            self.boxes[move[0]][move[1]+1] += 1
            # self.boxes[move[0]][move[1]+1] += 0.25
            plays_again += self.boxes[move[0]][move[1]+1] == 4
            # plays_again += int(self.boxes[move[0]][move[1]+1])



    # Remove Move from Legal Moves O(1)
        # self.remove_legal_move(move)

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

    def getNextState(self, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move

        # Gets and removes the action out of the legal moves

        tlen = len(self.legalMoves)

        assert self.hasLegalMoves(), "Doesn't have legal moves"
        assert self.isValidMove(action), "Isn't a valid move"
        move = self.legalMoves.pop(action)

        assert (tlen == len(self.legalMoves)+1), "No Move was deleted"


        self.moves_played.append(action)
        if move==None:
            print("\nMove Tried\n")

            print(action)
            print(self.moves_played)
            print("\nMoves Left\n")
            print(len(self.legalMoves))
            print("\nBoard State\n")
            print(self.boxes)
            self.printLegalMoves()
            assert (move!=None), "Move was None"


        # checks if the box is filled
        plays_again = self.executeMove(move, player)

        return (player if plays_again else -player)

    def getValidMoves(self):
        # return a fixed size binary vector
        valids = [0]*self.getActionSize()

        # Our key is a action to mapping Dictionary
        for key in self.legalMoves.keys():
            valids[key] = 1
        return np.array(valids)

    # change implementation to for draw
    def getGameEnded(self):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1
        if self.hasLegalMoves():
            return 0

        # Checks for draw
        if not self.score:
            # draw has a very little value
            return 1e-4

        return np.sign(self.score)*1.


    # Maybe we should set this to turn boards so n>m
    def getCanonicalForm(self):
        # return state if player==1, else return -state if player==-1
        return self.boxes

    def getSymmetries(self,  pi):

        board = np.copy(self.boxes)
        # mirror, rotational
        assert(len(pi) == 2*self.n*self.m)  # 1 for pass

        pi_down=[]
        pi_left=[]
        for i in range(0,len(pi),2):
            pi_left.append(pi[i])
            pi_down.append(pi[i+1])

        # pi_board = np.reshape(pi[:-1], (self.m, self.n, 2)) # Check this: We have 2 moves for each box -> how to?
        pi_down_board = np.reshape(pi_down, (self.n, self.m))
        pi_left_board = np.reshape(pi_left, (self.n, self.m))

        l = []

        # check if we want to store 4 or 8 symmetrical boards
        square = (self.n == self.m)

        # Original version
        temp_board = board
        temp_pi_down = pi_down_board
        temp_pi_left = pi_left_board
        l.append((board, list(pi)))
        # print("\nBoard " + str(i))
        # print(temp_pi_left)
        # Flipped
        b, pid, pil = _get_flipped(temp_board, temp_pi_down, temp_pi_left)
        # print("\nFlipped Board " + str(i))
        # print(pil)
        l.append((b, _merge(pil,pid)))

        for i in range(1,4):
            # 90*i degrees
            temp_board, temp_pi_down, temp_pi_left = _get_rotated(temp_board, temp_pi_down, temp_pi_left)

            if square or i==2:
                # print("\nBoard " + str(i))
                # print(temp_pi_left)
                l.append((temp_board,_merge(temp_pi_left,temp_pi_down)))

                # flipped
                b, pid, pil = _get_flipped(temp_board, temp_pi_down, temp_pi_left)
                # print("\nFlipped Board " + str(i))
                # print(pil)
                l.append((b, _merge(pil,pid)))

        #
        #
        # for i in range(1, 5):
        #     for j in [True, False]:
        #         newB = np.rot90(board, i)
        #         newPi = np.rot90(pi_board, i)
        #         if j:
        #             newB = np.fliplr(newB)
        #             newPi = np.fliplr(newPi)
        #         l += [(newB, list(newPi.ravel()) )]
        # print(l)
        return l

    def stringRepresentation(self):
        # 8x8 numpy array (canonical board)
        # return self.boxes.tostring()
        return str(self.legalMoves.keys())

    def printLegalMoves(self):

        temp = np.zeros((self.n,self.m))
        for x,move in self.legalMoves.items():
            x,y,d = move
            if d:
                temp[x,y] += 10
            else:
                temp[x,y] += 1

        print(temp)

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
    return temp_board, temp_down, temp_left


def _get_flipped(board, down, left):
    '''
    Flips Board and Pi boards according to conventions and returns the right result
    :param board:
    :param down:
    :param left:
    :return:
    '''
    temp_board = np.fliplr(board)
    temp_down = np.fliplr(down)
    temp_left = _pi_fliplr(left)
    return temp_board, temp_down, temp_left


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
    return np.roll(np.flipup(board),-1,0)

def _merge(x,y):
    '''
    Merges the two pi boards into a list
    :param x: the leftwards pis
    :param y: the downwards pis
    :return: the list of pis
    '''
    result = []
    for x_i,y_i in zip(x.ravel(),y.ravel()):
        result += [x_i,y_i]

    return result


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
            if piece == 4: print("X ",end="")
            elif piece < 4: print(piece+ " ",end="")
            else:
                if x==n:
                    print("-",end="")
                else:
                    print("- ",end="")
        print("|")

    print("   -----------------------")
