import math
import numpy as np
import copy
import time

EPS = 1e-8

class MCTS():
    """
    This class handles the MCTS tree.
    """

    # def __init__(self, game, args):
    def __init__(self, args):
        # self.game = game
        self.args = args
        self.Qsa = {}       # stores Q values for s,a (as defined in the paper)
        self.Nsa = {}       # stores #times edge s,a was visited
        self.Ns = {}        # stores #times board s was visited
        self.Ps = {}        # stores initial policy (returned by neural net)
        # self.Es = {}        # stores game.getGameEnded ended for board s
        self.Vs = {}        # stores game.getValidMoves for board s

        # self.depth = 0
        # self.moves = []

    def getActionProb(self, game, currPlayer, temp=1):
        """
        This function performs numMCTSSims simulations of MCTS starting from
        canonicalBoard.

        Returns:
            probs: a policy vector where the probability of the ith action is
                   proportional to Nsa[(s,a)]**(1./temp)
        """

        no_sims = self.args.numMCTSSims
        # no_sims = 2*game.numberLegalMoves() + 1

        if self.args.time_limit:
            timeleft = self.args.time_limit - 0.01
            tmptime = 0
            while timeleft>tmptime:
                tmptime = time.time();
                game_instance = copy.deepcopy(game)
                self.depth=0
                self.search(game_instance, currPlayer)

                tmptime = time.time() - tmptime;
                timeleft -= tmptime

        else:
            for i in range(no_sims):
                # print("NEW SIMULATION STARTED",flush=True)
                # print(i,flush=True)
                game_instance = copy.deepcopy(game)
                # self.depth=0
                # self.moves=[]
                self.search(game_instance, 1)
                # print(self.moves)
                assert not (game_instance is game), "Copy Not Deep Enough"


                # print("SIMULATION ENDED",flush=True)

        s = game.stringRepresentation()

        # In case Nsa empty
        # if not self.Nsa:
        #     probs = [0]*game.getActionSize()
        #
        #     n = game.numberLegalMoves()
        #     for a in game.getLegalKeys():
        #         probs[a] = 1/n
        #
        #     return probs

        counts = [self.Nsa[(s,a)] if (s,a) in self.Nsa else 0 for a in range(game.getActionSize())]


        # counts = [0]*game.getActionSize()
        # for a in game.getLegalKeys():
        #     if (s,a) in self.Nsa:
        #         counts[a] = self.Nsa[(s,a)]


        if temp==0:
            bestA = np.argmax(counts)
            probs = [0]*len(counts)
            probs[bestA]=1
            return probs


        assert sum(counts), str(game.boxes) + str(self.Nsa.items())

        # counts = [x**(1./temp) for x in counts]
        probs = [x/float(sum(counts)) for x in counts]
        return probs


    def search(self, game, player):


        s = game.stringRepresentation()
        # s = str(list(valids))

        # print(str([">>"]*self.depth) + "\n")
        # self.depth +=1

        if game.getGameEnded():
            # terminal node
            return player*game.getGameEnded()

        valids = game.getLegalKeys()


        if s not in self.Ps:
            # leaf node

            v = (np.random.rand()-1)/5

            # Improve Performance

            # masking invalid moves
            # valids = game.getValidMoves()
            # self.Ps[s] = self.Ps[s]*valids

            # temp = np.zeros(game.getActionSize())
            temp = {}
            sum_Ps_s = 0
            for a in valids:
                temp[a] = 1
                sum_Ps_s += 1
            self.Ps[s] = temp

            # sum_Ps_s = np.sum(self.Ps[s])
            if sum_Ps_s > 0:
                # self.Ps[s] /= sum_Ps_s    # renormalize
                for k in self.Ps[s].keys():
                    self.Ps[s][k] /= sum_Ps_s

            # self.Vs[s] = valids
            self.Ns[s] = 0

            return v
        else:
            strv = str(list(valids))
            strP = str(list(self.Ps[s].keys()))
            assert strv == strP, "New: " + strP + "\nOld: " + strv

        cur_best = -float('inf')
        best_act = -1
        # pick the action with the highest upper confidence bound
        for a in valids:
                # strv = str(list(valids).sort())
                # strP = str(list(self.Ps[s].keys()).sort())
                # assert strv == strP, "\nNew: " + strP + "\nOld: " + strv
                assert a in self.Ps[s], str(a) + "\nNew: " + str(valids) + "\nOld: " + str(self.Ps[s].keys()) + str(game.boxes)


                if (s,a) in self.Qsa:
                    u = self.Qsa[(s,a)] + self.args.cpuct*self.Ps[s][a]*math.sqrt(self.Ns[s])/(1+self.Nsa[(s,a)])
                else:
                    u = self.args.cpuct*self.Ps[s][a]*math.sqrt(self.Ns[s] + EPS)     # Q = 0 ?

                if u > cur_best:
                    cur_best = u
                    best_act = a

        # print(len(game.getValidMoves()))
        a = best_act
        next_player = game.getNextState(player, a)

        sign = 1 if next_player == player else -1

        # if the next player is the same then the value is positive
        v = self.search(game, next_player)*sign
        #
        # print("\n")
        # print("Depth: " + str(self.depth))
        # print("Next Player: " + str(next_player))
        # print("Value: " + str(v))
        # self.moves.append((next_player, str(v)))


        if (s,a) in self.Qsa:
            # assert np.sign(v) == np.sign(self.Qsa[(s,a)]), "Value sign mismatch"
            self.Qsa[(s,a)] = (self.Nsa[(s,a)]*self.Qsa[(s,a)] + v)/(self.Nsa[(s,a)]+1)
            self.Nsa[(s,a)] += 1

        else:
            self.Qsa[(s,a)] = v
            self.Nsa[(s,a)] = 1

        self.Ns[s] += 1
        return v
    #
    # def oldsearch(self, game):
    #     """
    #     This function performs one iteration of MCTS. It is recursively called
    #     till a leaf node is found. The action chosen at each node is one that
    #     has the maximum upper confidence bound as in the paper.
    #
    #     Once a leaf node is found, the neural network is called to return an
    #     initial policy P and a value v for the state. This value is propagated
    #     up the search path. In case the leaf node is a terminal state, the
    #     outcome is propagated up the search path. The values of Ns, Nsa, Qsa are
    #     updated.
    #
    #     NOTE: the return values are the negative of the value of the current
    #     state. This is done since v is in [-1,1] and if v is the value of a
    #     state for the current player, then its value is -v for the other player.
    #
    #     Returns:
    #         v: the negative of the value of the current canonicalBoard
    #     """
    #
    #     # results=[]
    #
    #     s = game.stringRepresentation()
    #
    #     if game.getGameEnded():
    #         # terminal node
    #         return game.getGameEnded()
    #
    #     if s not in self.Ps:
    #         # leaf node
    #         self.Ps[s], v = self.nnet.predict(game.boxes)
    #
    #         # Improve Performance
    #         valids = game.getLegalKeys()
    #
    #         # masking invalid moves
    #         # valids = game.getValidMoves()
    #         # self.Ps[s] = self.Ps[s]*valids
    #
    #         temp = np.zeros(game.getActionSize())
    #         for val in valids:
    #             temp[val] = self.Ps[s][val]
    #         self.Ps[s] = temp
    #
    #         sum_Ps_s = np.sum(self.Ps[s])
    #         if sum_Ps_s > 0:
    #             self.Ps[s] /= sum_Ps_s    # renormalize
    #         else:
    #             # if all valid moves were masked make all valid moves equally probable
    #
    #             # NB! All valid moves may be masked if either your NNet architecture is insufficient or you've get overfitting or something else.
    #             # If you have got dozens or hundreds of these messages you should pay attention to your NNet and/or training process.
    #             print("All valid moves were masked, do workaround.")
    #             # self.Ps[s] = self.Ps[s] + valids
    #             for val in valids:
    #                 self.Ps[s][val] += 1
    #
    #             self.Ps[s] /= np.sum(self.Ps[s])
    #
    #         # self.Vs[s] = valids
    #         self.Ns[s] = 0
    #         return v
    #
    #
    #     # valids = self.Vs[s]
    #     valids = game.getLegalKeys()
    #
    #     # if len(valids)!=len(game.getLegalKeys()):
    #     #     print("Valids Diff: ")
    #     #     print(valids)
    #     #     print(game.getLegalKeys())
    #     cur_best = -float('inf')
    #     best_act = -1
    #
    #     # pick the action with the highest upper confidence bound
    #     # for a in range(game.getActionSize()):
    #     #     if valids[a]:
    #     # print(len(valids),flush=True)
    #     for a in valids:
    #             if (s,a) in self.Qsa:
    #                 u = self.Qsa[(s,a)] + self.args.cpuct*self.Ps[s][a]*math.sqrt(self.Ns[s])/(1+self.Nsa[(s,a)])
    #             else:
    #                 u = self.args.cpuct*self.Ps[s][a]*math.sqrt(self.Ns[s] + EPS)     # Q = 0 ?
    #
    #             if u > cur_best:
    #                 cur_best = u
    #                 best_act = a
    #
    #     # print(len(game.getValidMoves()))
    #     a = best_act
    #     next_player = game.getNextState(1, a)
    #
    #
    #     # if the next player is the same then the
    #     v = self.search(game)*next_player
    #
    #     # results.append((s,a,v))
    #
    #     if (s,a) in self.Qsa:
    #         # assert np.sign(v) == np.sign(self.Qsa[(s,a)]), "Value sign mismatch"
    #         self.Qsa[(s,a)] = (self.Nsa[(s,a)]*self.Qsa[(s,a)] + v)/(self.Nsa[(s,a)]+1)
    #         self.Nsa[(s,a)] += 1
    #
    #     else:
    #         self.Qsa[(s,a)] = v
    #         self.Nsa[(s,a)] = 1
    #
    #     self.Ns[s] += 1
    #     return v
