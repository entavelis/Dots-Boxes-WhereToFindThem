'''
Not used anymore

Author: Evan Ntavelis (Based on work by Eric P. Nichols)
Date: Feb 8, 2008.
Board class.
Board data:
  1=white, -1=black, 0=empty
  first dim is column , 2nd is row:
     pieces[1][7] is the square in column 2,
     at the opposite end of the board in row 8.
Squares are stored and manipulated as (x,y) tuples.
x is the column, y is the row.
'''
class Board():


    def __init__(self, n, m, maxboard = 10):
        "Set up initial board configuration."

        # We have a maximum board size as fixed and then we fix smaller boards at its center and pad
        self.maxboard = maxboard

        self.n = self.maxboard + 2;
        self.m = self.maxboard + 2;
        self.legalMoves=[]

        self.innerN = n
        self.innerM = m

        self.score = 0


        # Create the empty board array.
        self.boxes = [None]*self.n

        # Create the empty board array.
        self.mask = [None]*self.n

        for i in range(self.n):
            self.boxes[i] = [0]*self.m
            self.mask[i] = [0]*self.m


        # Set up the legalMoves.
        # Centers the Inner Dimensions in the center and pads
        for i in range((self.n - self.innerN)/2,(self.n + self.innerN)/2):
            for j in range((self.n - self.innerM)/2,(self.m - self.innerM)/2):
                self.mask[i][j] = 1
                # Horizontal Move
                self.addMove(i,j-1,0)

                # Vertical Move
                self.legalMoves.append((i-1,j,1))


            # Last Horizontal
            self.legalMoves.append((i,(self.m - self.innerM)/2,0))

        # Last Verticals
        for j in range((self.n - self.innerM)/2,(self.m - self.innerM)/2):
            self.legalMoves.append(((self.n + self.innerN)/2,j,1))


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
        """Perform the given move on the board; flips pieces as necessary.
        color gives the color pf the piece to play (1=white,-1=black)
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


        # Remove Move from Legal Moves O(n)
        # TOCHECK
        # Improve Implementation -> Maybe HashMap?
        self.remove_lega_move(move)

        self.score += player * plays_again

        return plays_again







