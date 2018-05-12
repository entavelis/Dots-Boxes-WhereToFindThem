import sys
import argparse
import logging
import asyncio
import websockets
import json

import numpy as np

from alpha_zero_general import MCTS
from alpha_zero_general.dotsandboxes.DnBGame import DnBGame
from alpha_zero_general.utils import dotdict
from alpha_zero_general.dotsandboxes.pytorch.NNet import NNetWrapper as nn

# Initialize the Game
nb_cols=3
nb_rows=3
game = DnBGame(nb_rows, nb_cols)
game.reset_game()
# print([self.game.legalMoves[x] for x in self.game.legalMoves])

# Initialize the Network
nn = nn(game)
modelpath = "./alpha_zero_general/models/dim" + str(max(nb_rows,nb_cols)) + \
            "x" + str(min(nb_rows,nb_cols)) + str("/")
print("Searching for path " + str(modelpath))
nn.load_checkpoint(modelpath, "best.pth.tar")

# Initialize the MCTS and first its arguments
mcts_args = dotdict({'numMCTSSims': 20, 'cpuct':1.0, 'time_limit':0}) #Impose Timelimit here?
mcts1 = MCTS.MCTS(nn, mcts_args)
mcts2 = MCTS.MCTS(nn, mcts_args)
count=0

# while(sum(mcts.Es.values())==0):
#     count+=1
#     mcts.getActionProb(game)
# print("mcts.Qsa" )
# print(mcts.Qsa )
# print("mcts.Nsa")
# print(mcts.Nsa )
# print("mcts.Ns ")
# print(mcts.Ns )
# print("mcts.Ps ")
# print(mcts.Ps )
#     print("mcts.Es ")
    # print(list(map(lambda x: np.reshape(np.fromstring(x,dtype=int),(2+nb_rows,2+nb_cols)),mcts.Es.keys())))
    # print(mcts.Es.values())
    # print(count)
    # print(len(mcts.Es))
    # input('')
# print("mcts.Vs ")
# print(mcts.Vs )
if True:
    while game.getGameEnded()==0:
        it+=1
        if verbose:
            assert(display)
            print("Turn ", str(it), "Player ", str(curPlayer))
            display(game.getCanonicalForm)

        # CHECK: change this to adjust nnet input?
        # +1 is to get -1 to 0 and 1 to 2 for indices
        probs = players[curPlayer+1](game)
        print(probs)
        action = np.argmax(probs)

        # valids = game.getValidMoves()

        assert game.isValidMove(action),(str(action) + " not in " + str(game.getLegalMoves()))

        curPlayer = game.getNextState(curPlayer, action)

