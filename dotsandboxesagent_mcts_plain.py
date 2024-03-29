#!/usr/bin/env python3
# encoding: utf-8
"""
dotsandboxesagent.py

Template for the Machine Learning Project course at KU Leuven (2017-2018)
of Hendrik Blockeel and Wannes Meert.

Copyright (c) 2018 KU Leuven. All rights reserved.
"""
import sys
import argparse
import logging
import asyncio
import websockets
import json

import numpy as np

from alpha_zero_general import MCTS
from alpha_zero_general import MCTSplain
from alpha_zero_general.dotsandboxes.DnBGame import DnBGame
from alpha_zero_general.utils import dotdict

from collections import defaultdict
import random
#
# import numpy as np
# try:
#     from alpha_zero_general.MCTS import MCTS
#     from alpha_zero_general.dotsandboxes.NNet import NNetWrapper as NNet
#     from alpha_zero_general.dotsandboxes.DnBGame import DnBGame
#     from alpha_zero_general.utils import *
# except Exception:
#     from .alpha_zero_general.dotsandboxes.DnBGame import DnBGame
#     from .alpha_zero_general.MCTS import MCTS
#     from .alpha_zero_general.dotsandboxes.NNet import NNetWrapper as NNet
#     from .alpha_zero_general.utils import *



logger = logging.getLogger(__name__)
games = {}
agentclass = None


class DotsAndBoxesAgent:
    """Example Dots and Boxes agent implementation base class.
    It returns a random next move.

    A DotsAndBoxesAgent object should implement the following methods:
    - __init__
    - add_player
    - register_action
    - next_action
    - end_game

    This class does not necessarily use the best data structures for the
    approach you want to use.
    """
    def __init__(self, player, nb_rows, nb_cols, timelimit):
        """Create Dots and Boxes agent.

        :param player: Player number, 1 or 2
        :param nb_rows: Rows in grid
        :param nb_cols: Columns in grid
        :param timelimit: Maximum time allowed to send a next action.
        """
        self.player = {player}

        self.timelimit = timelimit
        self.ended = False

        self.nb_rows = nb_rows
        self.nb_cols = nb_cols

        rows = []
        # for ri in range(nb_rows + 1):
        #     columns = []
        #     for ci in range(nb_cols + 1):
        #         columns.append({"v": 0, "h": 0})
        #     rows.append(columns)
        # self.cells = rows

        logger.info("Initializing the agent")
        # Initialize the Game
        self.swapped = nb_rows < nb_cols
        if self.swapped:
            self.game = DnBGame(nb_cols, nb_rows)
        else:
            self.game = DnBGame(nb_rows, nb_cols)
        self.game.reset_game()
        # print([self.game.legalMoves[x] for x in self.game.legalMoves])

        mcts_args = dotdict({'numMCTSSims': 30, 'cpuct':1.0, 'time_limit': timelimit}) #Impose Timelimit here?
        self.mcts = MCTSplain.MCTS(mcts_args)



    def add_player(self, player):
        """Use the same agent for multiple players."""
        self.player.add(player)

    def register_action(self, row, column, orientation, player):
        """Register action played in game.

        :param row:
        :param columns:
        :param orientation: "v" or "h"
        :param player: 1 or 2
        """
        # logger.info("Registering next move")
        # Map action to our coding for the moves

        # Swap Boards

        if self.swapped:
            row, column, orientation = swap_board(row, column, orientation)


        if orientation == 'h':
            r =  row
            c = column + 1
            o = 1
        else:
            r  = row + 1
            c =  column
            o = 0

        action = 2 * ( self.game.m * r + c) + o
        # print(action)
        # print(row, column, orientation)
        # print(r,c,o)
        # print(self.game.legalMoves[action])

        # Map players to -1, 1 convention
        player = (-1)**(player-1)
        self.game.getNextState(player, action)
        # print("Player " + str(player))
        # print("Score " + str(self.game.score))
        # print("Game Ended " + str(self.game.getGameEnded()))

    def next_action(self):
        """Return the next action this agent wants to perform.

        In this example, the function implements a random move. Replace this
        function with your own approach.

        :return: (row, column, orientation)
        """
        # logger.info("Computing next move (grid={}x{}, player={})"\
        #         .format(self.nb_rows, self.nb_cols, self.player))


        probs = self.mcts.getActionProb(self.game, 1, temp=1)
        action = np.argmax(probs)


        # self.game.getNextState(action,player)
        # self.game.getNextState(1,action)

        o = action % 2
        r = int(action/(2*self.game.n))
        c = int(action/2) % self.game.n

        # print(self.game.legalMoves[action])

        # Swap Boards
        if self.swapped:
            # print(r,c,o)
            if not o:
                return swap_board(r-1,c,"v")
            else:
                return swap_board(r,c-1,"h")

        if not o:
            return r-1, c, "v"
        else:
            return r, c-1, "h"



    def end_game(self):
        self.ended = True


## MAIN EVENT LOOP

async def handler(websocket, path):
    logger.info("Start listening")
    game = None
    # msg = await websocket.recv()
    try:
        async for msg in websocket:
            # logger.info("< {}".format(msg))
            try:
                msg = json.loads(msg)
            except json.decoder.JSONDecodeError as err:
                logger.error(err)
                return False
            game = msg["game"]
            answer = None
            if msg["type"] == "start":
                # Initialize game
                if msg["game"] in games:
                    games[msg["game"]].add_player(msg["player"])
                else:
                    nb_rows, nb_cols = msg["grid"]
                    games[msg["game"]] = agentclass(msg["player"],
                                                    nb_rows,
                                                    nb_cols,
                                                    msg["timelimit"])
                if msg["player"] == 1:
                    # Start the game
                    nm = games[game].next_action()
                    print('nm = {}'.format(nm))
                    if nm is None:
                        # Game over
                        # logger.info("Game over")
                        continue
                    r, c, o = nm
                    answer = {
                        'type': 'action',
                        'location': [r, c],
                        'orientation': o
                    }
                else:
                    # Wait for the opponent
                    answer = None

            elif msg["type"] == "action":
                # An action has been played
                r, c = msg["location"]
                o = msg["orientation"]
                games[game].register_action(r, c, o, msg["player"])
                if msg["nextplayer"] in games[game].player:
                    # Compute your move
                    nm = games[game].next_action()
                    if nm is None:
                        # Game over
                        # logger.info("Game over")
                        continue
                    nr, nc, no = nm
                    answer = {
                        'type': 'action',
                        'location': [nr, nc],
                        'orientation': no
                    }
                else:
                    answer = None

            elif msg["type"] == "end":
                # End the game
                games[msg["game"]].end_game()
                answer = None
            else:
                logger.error("Unknown message type:\n{}".format(msg))

            if answer is not None:
                # print(answer)
                await websocket.send(json.dumps(answer))
                # logger.info("> {}".format(answer))
    except websockets.exceptions.ConnectionClosed as err:
        logger.info("Connection closed")
    logger.info("Exit handler")


def start_server(port):
    server = websockets.serve(handler, 'localhost', port)
    print("Running on ws://127.0.0.1:{}".format(port))
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()


def swap_board(row,column,orientation):
    if orientation == 'h':
        return column, row, 'v'
    else:
        return column, row, 'h'

## COMMAND LINE INTERFACE

def main(argv=None):
    global agentclass
    parser = argparse.ArgumentParser(description='Start agent to play Dots and Boxes')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='Verbose output')
    parser.add_argument('--quiet', '-q', action='count', default=0, help='Quiet output')
    parser.add_argument('port', metavar='PORT', type=int, help='Port to use for server')
    args = parser.parse_args(argv)

    logger.setLevel(max(logging.INFO - 10 * (args.verbose - args.quiet), logging.DEBUG))
    logger.addHandler(logging.StreamHandler(sys.stdout))

    agentclass = DotsAndBoxesAgent
    start_server(args.port)


if __name__ == "__main__":
    sys.exit(main())

