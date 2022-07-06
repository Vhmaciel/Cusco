from z3 import *


class Grid:
    def __init__(self, layer, x, y):
        self.layer = layer
        grid = []
        self.x_size = x
        self.y_size = y

        for _ in range(x):
            bandwith = []
            for _ in range(y):
                bandwith.append(False)
            grid.append(bandwith)
        
        self.grid = grid
        
    def increase_x(self, increase_in):
        
        for _ in range(increase_in):
            bandwith = []
            for _ in range(self.y_size):
                bandwith.append(False) 
            self.grid.append(bandwith)
    
   
    def occupy_point(self, x, y):
        
        self.grid[x][y] = True
        


    def print(self):
        print('Layer:', self.layer)
        for idx in range(self.y_size):
            for row in self.grid:
                print(int(row[idx]) , end=', ')
            print()
        
        return



def estimateGrid(listPCirc, listNCirc):
    
    return




