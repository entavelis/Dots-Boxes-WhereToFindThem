import numpy as np
from alpha_zero_general.dotsandboxes.DnBGame import DnBGame

def hashsym(sym):
    return hash(str(sorted(sym,key= lambda  x : str(x[0]))))

g = DnBGame(3,3)
g.reset_game()
g.getNextState(1,37)

print(g.boxes)
#
# sym = g.getSymmetries(range(50))
# print(len(sym))
# hs = hashsym(sym)
# for b,p in sym:
#     tmp = DnBGame(3,3)
#     tmp.reset_game()
#     tmp.boxes = b
#     print(hashsym(tmp.getSymmetries(p)) == hs)
