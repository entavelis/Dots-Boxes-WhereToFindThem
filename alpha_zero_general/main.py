# Colorful Traceback
import argparse

try:
    import colored_traceback.auto
except ImportError:
    pass

try :
    from .Coach import Coach
    from .dotsandboxes.DnBGame import DnBGame as Game
    from .dotsandboxes.pytorch.NNet import NNetWrapper as nn
    from .utils import *
except Exception:
    from Coach import Coach
    from dotsandboxes.DnBGame import DnBGame as Game
    from dotsandboxes.pytorch.NNet import NNetWrapper as nn
    from utils import *

import numpy as np

parser = argparse.ArgumentParser()

parser.add_argument('--numIters',type= int, default=1000)
parser.add_argument('--numEps',type= int, default=101)
parser.add_argument('--tempThreshold',type= int, default=20)
parser.add_argument('--updateThreshold',type= float, default=0.55)
parser.add_argument('--maxlenOfQueue',type= int, default=200000)
parser.add_argument('--numMCTSSims',type= int, default=25)
parser.add_argument('--arenaCompare',type= int, default=40)
parser.add_argument('--cpuct',type= int, default=1)
parser.add_argument('--checkpoint',type= str, default='./models/')
parser.add_argument('--load_model',type= str, default="false")
parser.add_argument('--load_folder',type= str, default='./models/')
parser.add_argument('--load_file',type= str, default='best.pth.tar')
parser.add_argument('--numItersForTrainExamplesHistory',type= int, default=  20)
parser.add_argument('--max_board',type= int, default=10)
parser.add_argument('--time_limit',type= float, default=0)
parser.add_argument('--rows',type= int, default=3)
parser.add_argument('--columns',type=int, default=3)
parser.add_argument('--arena',type=str, default= "true")
parser.add_argument('--arch',type=str, default="DnBNet")
parser.add_argument('--blocks',type=int, default= 5)

def main():
    # args.rows = np.random.randint(2,6)
    # args.columns = np.random.rand]int(2,args.rows)
    args = parser.parse_args()


    print("Rows: " + str(args.rows))
    print("Columns: " + str(args.columns))

    g = Game(args.rows,args.columns)
    nnet = nn(g,args)



    args.checkpoint += "dim" + str(args.rows) + 'x' + str(args.columns) + "/"
    args.load_folder += "dim" + str(args.rows) + 'x' + str(args.columns) + "/"


    if args.load_model == "true":
        nnet.load_checkpoint(args.load_folder, args.load_file)

    c = Coach(g, nnet, args)
    if args.load_model == "true":
        print("Load trainExamples from file")
        c.loadTrainExamples()
    c.learn()

if __name__=="__main__":
    main()
#
# args = dotdict({
#     'numiters': 50, # changed from 1000
#     'numeps': 20, # changed from 100
#     'tempthreshold': 50, # changed from 15
#     'updatethreshold': 0.50, # changed from 0.6
#     'maxlenofqueue': 200000,
#     'nummctssims': 15, # changed from 25
#     'arenacompare': 21, # changed from 40
#     'cpuct': 1,
#
#     'checkpoint': './models/',
#     'load_model': false,
#     'load_folder_file': ('/dev/models/8x100x50','best.pth.tar'),
#     'numitersfortrainexampleshistory': 20,
#
#     # our parameters
#     'sequential_training': true, #starting from smaller boards and going upwards,
#     'max_board': 10,
#     'time_limit': 0, # zero means no time limit
#     'rows': 3,
#     'columns': 3,
#     'arena': true
# })

