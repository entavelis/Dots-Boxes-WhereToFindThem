from collections import deque

import numpy as np
import time, os, sys
from pickle import Pickler, Unpickler
from random import shuffle
import copy
try:
    from .pytorch_classification.utils import Bar, AverageMeter
    from .Arena import Arena
    from .MCTS import MCTS
except Exception:
    from pytorch_classification.utils import Bar, AverageMeter
    from Arena import Arena
    from MCTS import MCTS

class Coach():
    """
    This class executes the self-play + learning. It uses the functions defined
    in Game and NeuralNet. args are specified in main.py.
    """
    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.pnet = self.nnet.__class__(self.game)  # the competitor network
        self.args = args
        # self.mcts = MCTS(self.game, self.nnet, self.args)
        self.mcts = MCTS(self.nnet, self.args)
        self.trainExamplesHistory = []    # history of examples from args.numItersForTrainExamplesHistory latest iterations
        self.skipFirstSelfPlay = False # can be overriden in loadTrainExamples()
        self.arenaEnabled = args.arena == "true"

    def executeEpisode(self):
        """
        This function executes one episode of self-play, starting with player 1.
        As the game is played, each turn is added as a training example to
        trainExamples. The game is played till the game ends. After the game
        ends, the outcome of the game is used to assign values to each example
        in trainExamples.

        It uses a temp=1 if episodeStep < tempThreshold, and thereafter
        uses temp=0.

        Returns:
            trainExamples: a list of examples of the form (canonicalBoard,pi,v)
                           pi is the MCTS informed policy vector, v is +1 if
                           the player eventually won the game, else -1.
        """
        trainExamples = []
        self.game.reset_game()
        self.curPlayer = 1
        episodeStep = 0

        players = []
        while True:
            players.append(self.curPlayer)
            episodeStep += 1
            # canonicalBoard = self.game.getCanonicalForm()
            temp = int(episodeStep < self.args.tempThreshold)

            pi = self.mcts.getActionProb(self.game, self.curPlayer, temp=temp)
            sym = self.game.getSymmetries(pi)

            for b,p in sym:
                trainExamples.append([b, self.curPlayer, p])
            #
            # trainExamples.append([self.game.boxes, self.curPlayer, pi, None])

            # Random Choice Based on the pi array as weights
            action = np.random.choice(len(pi), p=pi)
            self.curPlayer = self.game.getNextState(self.curPlayer, action)


            r = self.game.getGameEnded()

            if r!=0:
            #     print(r)
            #     print(self.curPlayer)
            #     for _,p,_ in trainExamples[::-8]:
                    # print("Last Player: {} Winner:: {} Score: {} Player Example {} \t Value {}".format(self.curPlayer, r, self.game.score, p,r*p))
                # return [(x[0],x[2],r*((-1)**(x[1]!=self.curPlayer))) for x in trainExamples]
                return [(x[0],x[2],r*x[1]) for x in trainExamples]

    def learn(self):
        """
        Performs numIters iterations with numEps episodes of self-play in each
        iteration. After every iteration, it retrains neural network with
        examples in trainExamples (which has a maximium length of maxlenofQueue).
        It then pits the new neural network against the old one and accepts it
        only if it wins >= updateThreshold fraction of games.
        """

        for i in range(1, self.args.numIters+1):
            # bookkeeping
            print('------ITER ' + str(i) + '------')
            print(str(self.game.innerN) + "x" + str(self.game.innerM))
            # examples of the iteration
            if not self.skipFirstSelfPlay or i > 1:
                iterationTrainExamples = deque([], maxlen=self.args.maxlenOfQueue)

                eps_time = AverageMeter()
                bar = Bar('Self Play', max=self.args.numEps)
                end = time.time()
    
                for eps in range(self.args.numEps):
                    # self.mcts = MCTS(self.game, self.nnet, self.args)   # reset search tree
                    self.mcts = MCTS(self.nnet, self.args)   # reset search tree
                    iterationTrainExamples += self.executeEpisode()

    
                    # bookkeeping + plot progress
                    eps_time.update(time.time() - end)
                    end = time.time()
                    bar.suffix  = '({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:}'.format(eps=eps+1, maxeps=self.args.numEps, et=eps_time.avg,
                                                                                                               total=bar.elapsed_td, eta=bar.eta_td)
                    bar.next()
                bar.finish()

                # save the iteration examples to the history 
                self.trainExamplesHistory.append(iterationTrainExamples)
                
            if len(self.trainExamplesHistory) > self.args.numItersForTrainExamplesHistory:
                print("len(trainExamplesHistory) =", len(self.trainExamplesHistory), " => remove the oldest trainExamples")
                self.trainExamplesHistory.pop(0)
            # backup history to a file
            # NB! the examples were collected using the model from the previous iteration, so (i-1)  
            self.saveTrainExamples(i-1)
            
            # shuffle examlpes before training
            trainExamples = []
            for e in self.trainExamplesHistory:
                trainExamples.extend(e)
            shuffle(trainExamples)

            tempfile =  'temp.pth.tar'
            bestfile =  'best.pth.tar'

            # training new network, keeping a copy of the old one
            self.nnet.save_checkpoint(folder=self.args.checkpoint, filename=tempfile)
            self.nnet.train(trainExamples)

            if self.arenaEnabled:
                self.pnet.load_checkpoint(folder=self.args.checkpoint, filename=tempfile)

                pmcts = MCTS(self.pnet, self.args)
                nmcts = MCTS(self.nnet, self.args)

                print('PITTING AGAINST PREVIOUS VERSION')
                # arena = Arena(lambda x: np.argmax(pmcts.getActionProb(x, temp=0)),
                #               lambda x: np.argmax(nmcts.getActionProb(x, temp=0)), self.game)
                arena = Arena(lambda x, y: pmcts.getActionProb(x, y, temp=0),
                           lambda x, y: nmcts.getActionProb(x, y, temp=0), self.game)
                pwins, nwins, draws = arena.playGames(self.args.arenaCompare)

                print('NEW/PREV WINS : %d / %d ; DRAWS : %d' % (nwins, pwins, draws))
                if pwins+nwins > 0 and float(nwins)/(pwins+nwins) < self.args.updateThreshold:
                    print('REJECTING NEW MODEL')
                    self.nnet.load_checkpoint(folder=self.args.checkpoint, filename=tempfile)
                else:
                    print('ACCEPTING NEW MODEL')
                    self.nnet.save_checkpoint(folder=self.args.checkpoint, filename=self.getCheckpointFile(i))
                    self.nnet.save_checkpoint(folder=self.args.checkpoint, filename=bestfile)
                # self.nnet.save_checkpoint(folder=self.args.checkpoint, filename=self.getCheckpointFile(i))
                # self.nnet.save_checkpoint(folder=self.args.checkpoint, filename=bestfile)

    def getCheckpointFile(self, iteration):
        return 'checkpoint_' + str(iteration) + '.pth.tar'

    def saveTrainExamples(self, iteration):
        folder = self.args.checkpoint
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.getCheckpointFile(iteration)+".examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.trainExamplesHistory)
        f.closed

    def loadTrainExamples(self):
        modelFile = os.path.join(self.args.load_folder, self.args.load_file)
        examplesFile = modelFile+".examples"
        if not os.path.isfile(examplesFile):
            print(examplesFile)
            r = input("File with trainExamples not found. Continue? [y|n]")
            if r != "y":
                sys.exit()
        else:
            print("File with trainExamples found. Read it.")
            with open(examplesFile, "rb") as f:
                self.trainExamplesHistory = Unpickler(f).load()
            f.closed
            # examples based on the model were already collected (loaded)
            self.skipFirstSelfPlay = True
