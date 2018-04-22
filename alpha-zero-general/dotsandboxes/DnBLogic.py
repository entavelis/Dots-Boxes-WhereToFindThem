'''
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

    # list of all 8 directions on the board, as (x,y) offsets
    __directions = [(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1)]


    def __init__(self, n, m):
        "Set up initial board configuration."

        # We have a maximum board size as fixed and then we fix smaller boards at its center and pad
        self.maxboard = 10

        self.n = self.maxboard + 2;
        self.m = self.maxboard + 2;
        self.legalMoves=[]

        self.innerN = n
        self.innerM = m



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
                self.legalMoves.append((i,j-1,0))

                # Vertical Move
                self.legalMoves.append((i-1,j,1))


            # Last Horizontal
            self.legalMoves.append((i,m+1,0))

        # Last Verticals
        for j in range(7 - m/2, 2+m):
            self.legalMoves.append((1+n,j,1))










    # add [][] indexer syntax to the Board
    def __getitem__(self, index): 
        return self.boxes[index]

    def countDiff(self, color):
        """Counts the # pieces of the given color
        (1 for white, -1 for black, 0 for empty spaces)"""
        count = 0
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y]==color:
                    count += 1
                if self[x][y]==-color:
                    count -= 1
        return count

    def get_legal_moves(self):
        return self.legalMoves


    def has_legal_moves(
        return len(self.legalMoves)>0;

    def get_moves_for_square(self, square):
        """Returns all the legal moves that use the given square as a base.
        That is, if the given square is (3,4) and it contains a black piece,
        and (3,5) and (3,6) contain white pieces, and (3,7) is empty, one
        of the returned moves is (3,7) because everything from there to (3,4)
        is flipped.
        """
        (x,y) = square

        # determine the color of the piece.
        color = self[x][y]

        # skip empty source squares.
        if color==0:
            return None

        # search all possible directions.
        moves = []
        for direction in self.__directions:
            move = self._discover_move(square, direction)
            if move:
                # print(square,move,direction)
                moves.append(move)

        # return the generated move list
        return moves

    def execute_move(self, move):
        """Perform the given move on the board; flips pieces as necessary.
        color gives the color pf the piece to play (1=white,-1=black)
        """

        # Change board state
        self.boxes[move[0]][move[1]]+=1
        if move[2]:
            self.boxes[move[0]+1][move[1]]+=1
        else:
            self.boxes[move[0]][move[1]+1]+=1


        # Remove Move from Legal Moves O(n)
        # TOCHECK
        # Improve Implementation -> Maybe HashMap?
        self.legalMoves.remove(move)





    @staticmethod
    def _increment_move(move, direction, n):
        # print(move)
        """ Generator expression for incrementing moves """
        move = list(map(sum, zip(move, direction)))
        #move = (move[0]+direction[0], move[1]+direction[1])
        while all(map(lambda x: 0 <= x < n, move)): 
        #while 0<=move[0] and move[0]<n and 0<=move[1] and move[1]<n:
            yield move
            move=list(map(sum,zip(move,direction)))
            #move = (move[0]+direction[0],move[1]+direction[1])

