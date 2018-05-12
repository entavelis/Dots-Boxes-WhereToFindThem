#!/usr/bin/env python3
# encoding: utf-8
"""
dotsandboxescompete.py

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
from collections import defaultdict
import random
import uuid
import time

logger = logging.getLogger(__name__)

ts_won = 0
ts_lost = 0
ts_draw = 0


def start_competition(address1, address2, nb_rows, nb_cols, timelimit):
   asyncio.get_event_loop().run_until_complete(connect_agent(address1, address2, nb_rows, nb_cols, timelimit))


async def connect_agent(uri1, uri2, nb_rows, nb_cols, timelimit):
    global ts_lost, ts_won, ts_draw
    cur_game = str(uuid.uuid4())
    winner = None
    cells = []
    cur_player = 1
    points = [0, 0, 0]
    timings = [None, [], []]

    for ri in range(nb_rows + 1):
        columns = []
        for ci in range(nb_cols + 1):
            columns.append({"v":0, "h":0, "p":0})
        cells.append(columns)

    logger.info("Connecting to {}".format(uri1))
    async with websockets.connect(uri1) as websocket1:
        logger.info("Connecting to {}".format(uri2))
        async with websockets.connect(uri2) as websocket2:
            logger.info("Connected")

            # Start game
            msg = {
              "type": "start",
              "player": 1,
              "timelimit": timelimit,
              "game": cur_game,
              "grid": [nb_rows, nb_cols]
            }
            await websocket1.send(json.dumps(msg))
            msg["player"] = 2
            await websocket2.send(json.dumps(msg))

            # Run game
            while winner is None:
                ask_time = time.time()
                logger.info("Waiting for player {}".format(cur_player))
                if cur_player == 1:
                    msg = await websocket1.recv()
                else:
                    msg = await websocket2.recv()
                recv_time = time.time()
                diff_time = recv_time - ask_time
                timings[cur_player].append(diff_time)
                logger.info("Message received after (s): {}".format(diff_time))
                try:
                    msg = json.loads(msg)
                except json.decoder.JSONDecodeError as err:
                    logger.debug(err)
                    continue
                if msg["type"] != "action":
                    logger.error("Unknown message: {}".format(msg))
                    continue
                r, c = msg["location"]
                o = msg["orientation"]
                next_player = user_action(r, c, o, cur_player,
                                          cells, points,
                                          nb_rows, nb_cols)
                if points[1] + points[2] == nb_cols * nb_rows:
                    # Game over
                    winner = 1
                    if points[2] == points[1]:
                        winner = 0
                        ts_draw +=1
                    elif points[2] > points[1]:
                        winner = 2
                        ts_lost +=1
                    else:
                        ts_won += 1

                else:
                    msg = {
                        "type": "action",
                        "game": cur_game,
                        "player": cur_player,
                        "nextplayer": next_player,
                        "score": [points[1], points[2]],
                        "location": [r, c],
                        "orientation": o
                    }
                    await websocket1.send(json.dumps(msg))
                    await websocket2.send(json.dumps(msg))

                cur_player = next_player

            # End game
            logger.info("Game ended: points1={} - points2={} - winner={}".format(points[1], points[2], winner))
            msg = {
                "type": "end",
                "game": cur_game,
                "player": cur_player,
                "nextplayer": 0,
                "score": [points[1], points[2]],
                "location": [r, c],
                "orientation": o,
                "winner": winner
            }


            await websocket1.send(json.dumps(msg))
            await websocket2.send(json.dumps(msg))

    # Timings
    for i in [1, 2]:
        logger.info("Timings: player={} - avg={} - min={} - max={}"\
            .format(i,
                    sum(timings[i])/len(timings[i]),
                    min(timings[i]),
                    max(timings[i])))

    logger.info("Closed connections")


def user_action(r, c, o, cur_player, cells, points, nb_rows, nb_cols):
    logger.info("User action: player={} - r={} - c={} - o={}".format(cur_player, r, c, o))
    next_player = cur_player
    won_cell = False
    cell = cells[r][c]
    if o == "h":
        if cell["h"] != 0:
            return cur_player
        cell["h"] = cur_player
        # Above
        if r > 0:
            if cells[r - 1][c]["v"] != 0 \
                and cells[r - 1][c + 1]["v"] != 0 \
                and cells[r - 1][c]["h"] != 0 \
                and cells[r][c]["h"] != 0:
                won_cell = True
                points[cur_player] += 1
                cells[r - 1][c]["p"] = cur_player
        # Below
        if r < nb_rows:
            if cells[r][c]["v"] != 0 \
                and cells[r][c + 1]["v"] != 0 \
                and cells[r][c]["h"] != 0 \
                and cells[r + 1][c]["h"] != 0:
                won_cell = True
                points[cur_player] += 1
                cells[r][c]["p"] = cur_player

    if o == "v":
        if cell["v"] != 0:
            return cur_player
        cell["v"] = cur_player;
        # Left
        if c > 0:
            if cells[r][c - 1]["v"] != 0 \
                and cells[r][c]["v"] != 0 \
                and cells[r][c - 1]["h"] != 0 \
                and cells[r + 1][c - 1]["h"] != 0:
                won_cell = True
                points[cur_player] += 1
                cells[r][c - 1]["p"] = cur_player
        # Right
        if c < nb_cols:
            if cells[r][c]["v"] != 0 \
                and cells[r][c + 1]["v"] != 0 \
                and cells[r][c]["h"] != 0 \
                and cells[r + 1][c]["h"] != 0:
                won_cell = True
                points[cur_player] += 1
                cells[r][c]["p"] = cur_player

    if not won_cell:
        next_player = 3 - cur_player
    else:
        next_player = cur_player
        # print("Update points: player1={} - player2={}".format(points[1], points[2]))
    return next_player


def main(argv=None):
    parser = argparse.ArgumentParser(description='Start agent to play Dots and Boxes')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='Verbose output')
    parser.add_argument('--quiet', '-q', action='count', default=0, help='Quiet output')
    parser.add_argument('--cols', '-c', type=int, default=5, help='Number of columns')
    parser.add_argument('--rows', '-r', type=int, default=5, help='Number of rows')
    parser.add_argument('--timelimit', '-t', type=float, default=0.5, help='Time limit per request in seconds')
    parser.add_argument('--times', '-ts', type=int, default=50, help='Time limit per request in seconds')
    parser.add_argument('agents', nargs=2, metavar='AGENT', help='Websockets addresses for agents')
    args = parser.parse_args(argv)

    logger.setLevel(max(logging.INFO - 10 * (args.verbose - args.quiet), logging.DEBUG))
    logger.addHandler(logging.StreamHandler(sys.stdout))

    ports = {}
    ports["greedy"] = "ws://127.0.0.1:8048"
    ports["alpha_DnB"] = "ws://127.0.0.1:8046"
    ports["mcts"] = "ws://127.0.0.1:8049"
    ports["random"] = "ws://127.0.0.1:8047"

    global ts_lost, ts_won, ts_draw
    print("Rows: %d, Columns %d, Timelimit: %f" % (args.rows, args.cols, args.timelimit))

    agent_names = ["alpha_DnB", "mcts"]

    for _ in range(2):

       for dim in range(3,9):
        print("{} Vs {} \t Dimensions {}x{}".format(agent_names[0],agent_names[1],dim,dim))
        ts_won = 0
        ts_lost = 0
        ts_draw = 0
        for i in range(int(args.times/2)):
            print(i+1)
            start_competition(ports[agent_names[0]], ports[agent_names[1]], dim, dim, args.timelimit)
            print("{} Won: {}, {} Won: {}, Draws: {}".format(agent_names[0], ts_won, agent_names[1], ts_lost, ts_draw))

        print("Switching Sides")
        ts_won, ts_lost = ts_lost, ts_won
        for j in range(int(args.times/2)):
            print(i+j+2)
            start_competition(ports[agent_names[1]], ports[agent_names[0]], dim, dim, args.timelimit)
            print("{} Won: {}, {} Won: {}, Draws: {}".format(agent_names[0], ts_lost, agent_names[1], ts_won, ts_draw))

        print("Won {}%".format(100*ts_lost/(ts_won+ts_lost)))
       agent_names[1] = "random"


if __name__ == "__main__":
    sys.exit(main())

