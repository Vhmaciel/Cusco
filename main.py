from z3 import *
import placement as pl
import toolutils as ut
import routing as rt
import drawing as dr
import numpy as np

#nets = ["netlist.txt", "sccg.txt", "nor.txt", 'a.txt']
#nets = ['somador.txt']
nets = ['netlist.txt']
layers = ['M1', 'CA', 'RX', 'POLY']

for item in nets:
    circuit, circDict, pc, nc, ppos, npos = [], [], [], [], [], []
    circuit, circDict = ut.read_netlist(item)
    netlist = []
    pc, nc, ppos, npos = pl.placement(circuit)
    
    
    for pitem in pc:
        print(pitem)        
    for nitem in nc:
        print(nitem)
        
    col, row = rt.estimateGrid(pc,nc)
        
    print(col, row)
    
    grRX, grCA, grPoly = rt.createGridTransistors(['RX', 'CA', 'POLY'], col, row, pc, nc, ppos, npos)
    netlist, pinlist = rt.defineNets(grCA)
    
    npGridCA = np.matrix(grCA.grid)
    print(npGridCA)
    print("FOI")


    grM1 = rt.routeHoldingHandsMST(['M1', 'M2', 'M3'], netlist, pinlist, col, row)

    #grM1 = rt.route(['M1', 'M2', 'M3'], netlist, pinlist, col, row)
    
    dr.drawLayers([grRX, grPoly, grCA, grM1], col, row, circDict)
    
    print('-----------------------------------------------')






        
    

       
    

