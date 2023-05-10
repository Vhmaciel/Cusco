import numpy as np
from z3 import *
from math import floor, sqrt

N_REGION = 3
P_REGION = 3
MID_REGION = 10
GND_REGION = 4
VDD_REGION = 4


class Pin:
    def __init__(self, x: int, y: int, con_num = None, net = None):
        self.con_num = con_num
        self.net = net
        self.x = x
        self.y = y

    def __str__(self):
        return (f"({self.x}, {self.y})")

class Connection:
    def __init__(self, number: int, pin1: Pin, pin2: Pin):
        self.number = number
        self.pin1 = pin1
        self.pin2 = pin2

    def __str__(self):
        return (f"Con: {self.number} | Start Pin: {self.pin1} End Pin: {self.pin2}")


class Net:
    def __init__(self, net_number: int, connections: list, pinslist: list):
        self.net_number = net_number
        self.connections = connections
        self.pinslist = pinslist
    
    def __str__(self):
        txt = "Net {}\n".format(self.net_number)
        for con in self.connections:
            txt += f"\t {con}\n"

        return txt
    
    def getNumOfConnections(self):
        return len(self.connections)
            
    def getPins(self):
        listOfPins = []
        
        for c in self.connections:
            if c.pin1 not in listOfPins:
                listOfPins.append(c.pin1)
            if c.pin2 not in listOfPins:
                listOfPins.append(c.pin2)
        
        return listOfPins
            
            

class Grid:
    def __init__(self, layer, x: int, y: int):
        self.layer = layer
        grid = []
        self.x_size = x
        self.y_size = y

        for _ in range(x):
            bandwith = []
            for _ in range(y):
                bandwith.append(0)
            grid.append(bandwith)
        
        self.grid = grid
        
    def increase_x(self, increase_in):
        
        for _ in range(increase_in):
            bandwith = []
            for _ in range(self.y_size):
                bandwith.append(0) 
            self.grid.append(bandwith)
    
   
    def occupy_points(self, listOfPoints, value=1):
        for point in listOfPoints:
            self.occupy_one_point(point[0],point[1], value)
   
    def occupy_one_point(self, x, y, value=1):
        
        self.grid[x][y] = value

    def fill_grid(self, list_of_lists):
        for x, ar in enumerate(list_of_lists):
            for y, val in enumerate(ar):
                self.occupy_one_point(y, x, int(val))
  
        
    def print(self):
        print('Layer:', self.layer)
        for idx in range(self.y_size):
            for row in self.grid:
                print(row[idx] , end=', ')
            print()
        
        return


def estimateGrid(listPCirc, listNCirc):

    max_p_w = 3
    max_n_w = 3
    mid_region = 12
    gnd_y, vdd_y = 2, 2
    
    min_bandwidth = N_REGION + P_REGION + MID_REGION + VDD_REGION + GND_REGION          #constante
    bandw = max_p_w + max_n_w + mid_region + gnd_y + vdd_y                              #variável
    

    if len(listPCirc)!=len(listNCirc):
        print('Erro estranho kkk')
        return

    count_col = (len(listPCirc)*4) + 5
    count_row = bandw if bandw >= min_bandwidth else min_bandwidth
    
    
    return count_col, count_row

def POLYfill(grPOLY, pcirc, ncirc, grCA):
    #if len(pcirc)!=len(ncirc):
    #    print('Erro estranho kkk')
    #    return
    
    for idx in range(len(ncirc)):
        points = []
        if ncirc[idx].gate == pcirc[idx].gate and ncirc[idx].gate != 0 and pcirc[idx].gate != 0:
            for y in range(P_REGION+N_REGION+MID_REGION):
                points.append([(ncirc[idx].position*4)+4, y+VDD_REGION])
            grPOLY.occupy_points(points, ncirc[idx].gate) 
            grCA.occupy_one_point((ncirc[idx].position*4)+4, floor((P_REGION+N_REGION+MID_REGION+VDD_REGION)/2)+1, ncirc[idx].gate)
        else:
            if ncirc[idx].gate != 0:
                for y in range(N_REGION+2):
                    points.append([(ncirc[idx].position*4)+4, y+VDD_REGION+P_REGION+MID_REGION-2])
                grPOLY.occupy_points(points, ncirc[idx].gate)
                grCA.occupy_one_point((ncirc[idx].position*4)+4, VDD_REGION+P_REGION+MID_REGION-2, ncirc[idx].gate)
                points = []
            if pcirc[idx].gate != 0:
                for y in range(P_REGION+2):
                    points.append([(pcirc[idx].position*4)+4, y+VDD_REGION])
                grPOLY.occupy_points(points, pcirc[idx].gate)
                grCA.occupy_one_point((pcirc[idx].position*4)+4, VDD_REGION+P_REGION+1, pcirc[idx].gate)
        
                 
    grPOLY.print()
  

def RXfill(grRX, pcirc, ncirc):
    
    #if len(pcirc)!=len(ncirc):
    #    print('Erro estranho kkk')
    #    return

    idx_p_max = 0
    idx_n_max = 0
    
    for idx in range(len(pcirc)):
        points = []  
        
        idx_p_max = len(pcirc)-1
        idx_n_max = len(pcirc)-1
        
        if pcirc[idx].source != 0 and pcirc[idx].drain != 0:
            #ocupa 2*idx+1 e 2*idx+2 para toda p_region
            for x in range(1,5):
                for y in range(P_REGION):
                    points.append([(pcirc[idx].position*4)+x, y+VDD_REGION])
            grRX.occupy_points(points)
        else:
            if grRX.grid[pcirc[idx].position*4][VDD_REGION] != 0:
                for x in range(1,4):
                    for y in range(P_REGION):
                        points.append([(pcirc[idx].position*4)+x, y+VDD_REGION])
                    grRX.occupy_points(points)
            
             
        if ncirc[idx].source != 0 and ncirc[idx].drain != 0:
            #ocupa 2*idx+1 e 2*idx+2 para toda n_region
            for x in range(1,5):
                for y in range(N_REGION):
                    points.append([(ncirc[idx].position*4)+x, y+MID_REGION+P_REGION+VDD_REGION])
            grRX.occupy_points(points)
        else:
            if grRX.grid[ncirc[idx].position*4][MID_REGION+P_REGION+VDD_REGION] != 0:
                for x in range(1,4):
                    for y in range(N_REGION):
                        points.append([(ncirc[idx].position*4)+x, y+MID_REGION+P_REGION+VDD_REGION])
                    grRX.occupy_points(points)
    
   
    
    if pcirc[idx_p_max].source != 0 and pcirc[idx_p_max].drain != 0:
        points = []
        for x in range(5,8):
            for y in range(P_REGION):
                points.append([(pcirc[idx_p_max].position*4)+x, y+VDD_REGION])
            grRX.occupy_points(points)
             
    if ncirc[idx_n_max].source != 0 and ncirc[idx_n_max].drain != 0:
        points = []
        for x in range(5,8):    
            for y in range(N_REGION):
                points.append([(ncirc[idx_n_max].position*4)+x, y+MID_REGION+P_REGION+VDD_REGION])
            grRX.occupy_points(points)
        
    grRX.print()
    
def CAfill(grCA, ppos, npos):
    
    yp = floor(P_REGION/2)
    yn = floor(N_REGION/2)
    
    for idp, pmos in enumerate(ppos):
        if pmos != 0:
            grCA.occupy_one_point((idp*4)+2, yp+VDD_REGION, pmos)
            
    for idn, nmos in enumerate(npos):
        if nmos != 0:
            grCA.occupy_one_point((idn*4)+2, yn+MID_REGION+P_REGION+VDD_REGION, nmos)
            
    # for idx in range(math.ceil(grCA.x_size/2)-1):
    #     grCA.occupy_one_point((idx*2)+1, 0, 2)
    #     grCA.occupy_one_point((idx*2)+1, N_REGION + P_REGION + MID_REGION + VDD_REGION + GND_REGION-1, 1)
        
    grCA.occupy_one_point(floor(grCA.x_size/2), 1, 2)
    grCA.occupy_one_point(floor(grCA.x_size/2), N_REGION + P_REGION + MID_REGION + VDD_REGION + GND_REGION-2, 1)
    
    grCA.print()

def createGridTransistors(layers, col, row, pcirc, ncirc, ppos, npos):
    
    grRX = Grid(layers[0], col, row)
    grCA = Grid(layers[1], col, row)
    grPoly = Grid(layers[2], col, row)
     
    RXfill(grRX, pcirc, ncirc)
    POLYfill(grPoly, pcirc, ncirc, grCA)
    CAfill(grCA, ppos, npos)
    
    
    
    return grRX, grCA, grPoly


def defineNets(grCA):
    pinlist = {}
    netlist = []
    
    for idx_x in range(grCA.x_size):
        for idx_y in range(grCA.y_size):
            if grCA.grid[idx_x][idx_y] != 0:
                if grCA.grid[idx_x][idx_y] in pinlist.keys():
                    pinlist[grCA.grid[idx_x][idx_y]].append([idx_x, idx_y])
                else:
                    pinlist[grCA.grid[idx_x][idx_y]] = [[idx_x, idx_y]]

    netsToBeRemoved = []

    for key in pinlist.keys():
        if len(pinlist[key]) < 2:
            if pinlist[key][0][1] > MID_REGION+P_REGION+VDD_REGION or pinlist[key][0][1] < P_REGION+VDD_REGION:
                print(key)
                grCA.grid[pinlist[key][0][0]][pinlist[key][0][1]] = 0
                netsToBeRemoved.append(key)

    for rm in netsToBeRemoved:
        pinlist.pop(rm)

    aux_cons = []
    uniquepins = []
    con_count = 0

    for n in pinlist:
        if len(pinlist[n])==2:    
            for idx, ps in enumerate(pinlist[n]):
                for i in range(idx+1, len(pinlist[n])):
                    aux_cons.append(Connection(con_count, Pin(ps[0], ps[1], con_count, n), Pin(pinlist[n][i][0], pinlist[n][i][1], con_count, n)))
                    con_count = con_count + 1
                uniquepins.append(Pin(ps[0], ps[1], con_count, n))

            con_count = 0
            netlist.append(Net(n, aux_cons, uniquepins))
            aux_cons = []
            uniquepins = []
            
        if len(pinlist[n])>2: 
            print(pinlist[n])

            netlist.append(MST(pinlist[n], n))
            
            print("TOP")

    for n in netlist:
        print(n)
    
    print(pinlist)
    return netlist, pinlist

def MST(pts, n):

    # Create the graph
    graph = {}
    for i in range(len(pts)):
        for j in range(i+1, len(pts)):
            # Calculate the manhattan distance between the two pts
            dist = abs(pts[j][0]-pts[i][0]) + abs(pts[j][1]-pts[i][1])
            
            # Add the edge to the graph
            if i not in graph:
                graph[i] = {}
            if j not in graph:
                graph[j] = {}
            graph[i][j] = dist
            graph[j][i] = dist


    mst = kruskal(graph)
    print(mst)
    unique_connections = set()
    list_of_connections = []
    uniquepins = []

    for node in mst:
        for neighbor in mst[node]:
            connection = tuple(sorted([node, neighbor]))
            unique_connections.add(connection)

    unique_connections = [list(connection) for connection in unique_connections]

    for i, con in enumerate(unique_connections):
        list_of_connections.append(Connection(i, Pin(pts[con[0]][0], pts[con[0]][1], i, n), Pin(pts[con[1]][0], pts[con[1]][1], i, n)))
        pass
    
    for ps in pts:
        uniquepins.append(Pin(ps[0], ps[1], len(unique_connections), n))

    resulting_net = Net(n, list_of_connections, uniquepins)
    
    return resulting_net
    
def createRules(opt, matrix, list_of_pins, grid_x, grid_y):
            opt.add(matrix[list_of_pins[0].y, list_of_pins[0].x] == True)
            opt.add(matrix[list_of_pins[1].y, list_of_pins[1].x] == True)
            pass

            for idx in range(2):
                north = And(matrix[list_of_pins[idx].y+1, list_of_pins[0].x])
                south = And(matrix[list_of_pins[idx].y-1, list_of_pins[idx].x])
                east = And(matrix[list_of_pins[idx].y, list_of_pins[idx].x+1])
                weast = And(matrix[list_of_pins[idx].y, list_of_pins[idx].x-1])

                not_north = Not(north)
                not_south = Not(south)
                not_east = Not(east)
                not_weast = Not(weast)

                opt.add(Implies(matrix[list_of_pins[1].y, list_of_pins[1].x] == True, 
                                Or(And(not_north, not_south, east, not_weast),
                                    And(not_north, not_south, not_east, weast),
                                    And(north, not_south, not_east, not_weast),
                                    And(not_north, south, not_east, not_weast)
                    )))

            for y in range(1, grid_y-1):    
                for x in range(1, grid_x-1):
                    if((x==list_of_pins[0].x and y==list_of_pins[0].y) or (x==list_of_pins[1].x and y==list_of_pins[1].y)):
                        continue

                    north = And(matrix[y+1, x])
                    south = And(matrix[y-1, x])
                    east = And(matrix[y, x+1])
                    weast = And(matrix[y, x-1])

                    not_north = Not(north)
                    not_south = Not(south)
                    not_east = Not(east)
                    not_weast = Not(weast)

                    opt.add(Implies(matrix[y, x]==True,
                                    Or(And(north, south, not_east, not_weast),
                                        And(north, not_south, east, not_weast),
                                        And(north, not_south, not_east, weast),
                                        And(not_north, south, east, not_weast),
                                        And(not_north, south, not_east, weast),
                                        And(not_north, not_south, east, weast))))


def routeHoldingHandsMST(metalLayers, nets, pins, grid_x, grid_y):

    opt = Optimize()
    matrixDict = {}
    multiPinDict = {}
    f_test = 0

    for n in nets:
        matrixDict[n] = np.matrix([[Bool("net%i_%i_%i" % (n.net_number,j,i)) for j in range (grid_x)] for i in range(grid_y)])
        for x in range(grid_x):
            opt.add(matrixDict[n][0, x] == False)
            opt.add(matrixDict[n][-1, x] == False)
        for y in range(grid_y):
            opt.add(matrixDict[n][y, 0] == False)
            opt.add(matrixDict[n][y, -1] == False)
        
        print('NET NUMBER -> ', n.net_number)
        t_nets = []


        if(n.getNumOfConnections()==1):
            
            t_nets.append(n)
            list_of_pins = n.getPins()
            
            createRules(opt, matrixDict[n], list_of_pins, grid_x, grid_y)


        if(n.getNumOfConnections()>1):
            matrixDict[n] = np.matrix([[Bool("net%i_%i_%i" % (n.net_number,j,i)) for j in range (grid_x)] for i in range(grid_y)])
            multiPinDict[n] = {}
            if f_test == 0:
                nc = n
                f_test = 1
            for con in n.connections:
                if f_test == 1:
                    cc = con
                    f_test = 2
                print("entrou na CON ->", con.number)
                listOfPins = [con.pin1, con.pin2]
                auxMatrix = np.matrix([[Bool("net%i_con_%i_%i_%i" % (n.net_number, con.number,j,i)) for j in range (grid_x)] for i in range(grid_y)])
                multiPinDict[n][con] = auxMatrix
                for x in range(grid_x):
                    opt.add(multiPinDict[n][con][0, x] == False)
                    opt.add(multiPinDict[n][con][-1, x] == False)
                for y in range(grid_y):
                    opt.add(multiPinDict[n][con][y, 0] == False)
                    opt.add(multiPinDict[n][con][y, -1] == False)
                print(multiPinDict[n][con])
                createRules(opt, multiPinDict[n][con], listOfPins, grid_x, grid_y)
            
            for y in range(1, grid_y-1):    
                for x in range(1, grid_x-1):
                    opt.add(matrixDict[n][y, x] == False)
                
            

    final_mx = np.matrix([[Int('SM_%i_%i' % (j,i)) for j in range (grid_x)] for i in range(grid_y)])
    for y in range(0, grid_y):    
        for x in range(0, grid_x):
            opt.add(And(Or(final_mx[y, x]==1, final_mx[y, x]== 0), final_mx[y, x] == Sum([matrixDict[n][y, x] for n in nets])))
            pass

    for n in nets:
        if n.getNumOfConnections()==1:
            cost = Sum([Sum([matrixDict[n][y, x] for x in range(1,grid_x-1)]) for y in range(1,grid_y-1)])
            opt.minimize(cost)

    opt.set('timeout', 60000)
    if opt.check()==sat:
        m = opt.model()
        met1Grid = Grid('M1', grid_x, grid_y)
        dict_nets_matrix = {}


        for n in nets:
            dict_nets_matrix[n.net_number] = matrix_conversion(matrixDict[n], grid_x, grid_y, m)
            

        rm = result_matrix(dict_nets_matrix, grid_x, grid_y)
        print(rm.tolist())
        met1Grid.fill_grid(rm)
        return met1Grid

       
    else:
        print("UNSAT")

    return

def matrix_conversion(matrix, grid_x, grid_y, model):
    new_m = []
    for j in range(grid_y):
        new_array = []
        for i in range(grid_x):
            new_array.append(int(bool(BoolVal(model.eval(matrix[j, i]))))) if type(matrix[j, i]) is z3.z3.BoolRef else new_array.append(0)
        new_m.append(new_array)

    return new_m

def result_matrix(dict_nets_matrix, grid_x, grid_y):
    res_m = np.zeros((grid_y,grid_x))
    
    for label, matrix in dict_nets_matrix.items():
        for y in range(1, grid_y-1):
            for x in range(1, grid_x-1):
                if matrix[y][x] == 1:
                    res_m[y,x] = label

    return res_m

# Kruskal's algorithm
def kruskal(graph):
    # Create a set for each vertex
    sets = [{i} for i in graph]
    
    # Sort the edges by weight
    edges = []
    for u in graph:
        for v in graph[u]:
            edges.append((u, v, graph[u][v]))
    edges.sort(key=lambda e: e[2])
    
    # Iterate through the edges and add them to the tree if they connect different sets
    tree = {}
    for u, v, w in edges:
        set_u = next((s for s in sets if u in s))
        set_v = next((s for s in sets if v in s))
        if set_u != set_v:
            # Add the edge to the tree
            if u not in tree:
                tree[u] = {}
            if v not in tree:
                tree[v] = {}
            tree[u][v] = w
            tree[v][u] = w
            
            # Merge the sets
            sets.remove(set_u)
            sets.remove(set_v)
            sets.append(set_u.union(set_v))
            
    return tree

def route(metalLayers, nets, pins, grid_x, grid_y):
    
    first_route = True

    s = Solver()
    
    num_metal = len(metalLayers)
    metal_grid_3d = [[[Int("s_%i_%i_%i" % (j,i,k)) for j in range (grid_x)] for i in range(grid_y)] for k in range(num_metal)]
        

    nets_set = set([n.net_number for n in nets])
    net_number = []
    
    for idx, n in enumerate(nets_set):
        net_number.append(Int("net_%i" % (n)))
        s.add(net_number[idx] == n)
    
    
    print(nets_set)
    print(net_number)
    
    
    cons_number = sum(int(n.getNumOfConnections()) for n in nets) 
    
    is_pin = [[False for i in range (grid_x)] for j in range (grid_y)]
    
    for z in range(num_metal):
        for x in range(grid_x):
            s.add(metal_grid_3d[z][0][x] == 0)
            s.add(metal_grid_3d[z][grid_y-1][x] == 0)
        for y in range(grid_y):
            s.add(metal_grid_3d[z][y][0] == 0)
            s.add(metal_grid_3d[z][y][grid_x-1] == 0)


    
    print(cons_number)   
    
    for n in net_number:
        print(n)     

   
    print(pins)

    for p in pins:
        if p not in nets_set:
            print(p)
            s.add(And(metal_grid_3d[0][pins[p][0][1]+1][pins[p][0][0]+1] == 0,
                    metal_grid_3d[0][pins[p][0][1]-1][pins[p][0][0]+1] == 0,
                    metal_grid_3d[0][pins[p][0][1]+1][pins[p][0][0]-1] == 0,
                    metal_grid_3d[0][pins[p][0][1]-1][pins[p][0][0]-1] == 0,
                    metal_grid_3d[0][pins[p][0][1]][pins[p][0][0]] == 0,
                    metal_grid_3d[0][pins[p][0][1]+1][pins[p][0][0]] == 0,
                    metal_grid_3d[0][pins[p][0][1]-1][pins[p][0][0]] == 0,
                    metal_grid_3d[0][pins[p][0][1]][pins[p][0][0]+1] == 0,
                    metal_grid_3d[0][pins[p][0][1]][pins[p][0][0]-1] == 0
    
                )
            )

    
    for n in nets:
        if len(n.pinslist) > 2:
            print(str(len(n.pinslist)) + '- tamanho')
                #for ps in n.pinslist:
                            


    for n in nets:
        if len(n.pinslist) > 2:
            mst_net = True
            print(n.net_number)
        else:
            mst_net = False

        for idx, ps in enumerate(n.pinslist):
                
                s.add(metal_grid_3d[0][ps.y][ps.x] == n.net_number)
                is_pin[ps.y][ps.x] = True

                s.add(Or(metal_grid_3d[0][ps.y+1][ps.x+1] == n.net_number, metal_grid_3d[0][ps.y+1][ps.x+1] == 0))
                s.add(Or(metal_grid_3d[0][ps.y-1][ps.x+1] == n.net_number, metal_grid_3d[0][ps.y-1][ps.x+1] == 0))
                s.add(Or(metal_grid_3d[0][ps.y+1][ps.x-1] == n.net_number, metal_grid_3d[0][ps.y+1][ps.x-1] == 0))
                s.add(Or(metal_grid_3d[0][ps.y-1][ps.x-1] == n.net_number, metal_grid_3d[0][ps.y-1][ps.x-1] == 0))

                ap = And(metal_grid_3d[0][ps.y+1][ps.x] == 0, metal_grid_3d[0][ps.y-1][ps.x] == 0, metal_grid_3d[0][ps.y][ps.x+1] == 0, metal_grid_3d[0][ps.y][ps.x-1] == metal_grid_3d[0][ps.y][ps.x])
                bp = And(metal_grid_3d[0][ps.y+1][ps.x] == 0, metal_grid_3d[0][ps.y-1][ps.x] == 0, metal_grid_3d[0][ps.y][ps.x+1] == metal_grid_3d[0][ps.y][ps.x], metal_grid_3d[0][ps.y][ps.x-1] == 0)
                cp = And(metal_grid_3d[0][ps.y+1][ps.x] == 0, metal_grid_3d[0][ps.y-1][ps.x] == metal_grid_3d[0][ps.y][ps.x], metal_grid_3d[0][ps.y][ps.x+1] == 0, metal_grid_3d[0][ps.y][ps.x-1] == 0)                  
                dp = And(metal_grid_3d[0][ps.y+1][ps.x] == metal_grid_3d[0][ps.y][ps.x], metal_grid_3d[0][ps.y-1][ps.x] == 0, metal_grid_3d[0][ps.y][ps.x+1] == 0, metal_grid_3d[0][ps.y][ps.x-1] == 0)

                if mst_net:
                    if idx == 0 or idx == len(n.pinslist)-1:
                        s.add(Or(
                        And(ap, Not(bp), Not(cp), Not(dp)),
                        And(Not(ap), bp, Not(cp), Not(dp)),
                        And(Not(ap), Not(bp), cp, Not(dp)),
                        And(Not(ap), Not(bp), Not(cp), dp)
                        )
                        )
                    else:
                        s.add(Or(metal_grid_3d[0][ps.y+1][ps.x] == n.net_number,
                                metal_grid_3d[0][ps.y][ps.x+1] == n.net_number,
                                metal_grid_3d[0][ps.y-1][ps.x] == n.net_number,
                                metal_grid_3d[0][ps.y][ps.x-1] == n.net_number))
                else:
                    s.add(Or(
                        And(ap, Not(bp), Not(cp), Not(dp)),
                        And(Not(ap), bp, Not(cp), Not(dp)),
                        And(Not(ap), Not(bp), cp, Not(dp)),
                        And(Not(ap), Not(bp), Not(cp), dp)
                        ))
          
    
    for y in range(1, grid_y-1):    
        for x in range(1, grid_x-1):
            #if z == 0:
            if not is_pin[y][x]:       
                
                a = And(metal_grid_3d[0][y+1][x] == metal_grid_3d[0][y][x], metal_grid_3d[0][y][x+1] == metal_grid_3d[0][y][x], metal_grid_3d[0][y-1][x] == 0, metal_grid_3d[0][y][x-1] == 0)
                b = And(metal_grid_3d[0][y+1][x] == metal_grid_3d[0][y][x], metal_grid_3d[0][y][x+1] == 0, metal_grid_3d[0][y-1][x] == metal_grid_3d[0][y][x], metal_grid_3d[0][y][x-1] == 0)
                c = And(metal_grid_3d[0][y+1][x] == 0, metal_grid_3d[0][y][x+1] == metal_grid_3d[0][y][x], metal_grid_3d[0][y-1][x] == metal_grid_3d[0][y][x], metal_grid_3d[0][y][x-1] == 0)
                d = And(metal_grid_3d[0][y+1][x] == metal_grid_3d[0][y][x], metal_grid_3d[0][y][x+1] == 0, metal_grid_3d[0][y-1][x] == 0, metal_grid_3d[0][y][x-1] == metal_grid_3d[0][y][x])
                e = And(metal_grid_3d[0][y+1][x] == 0, metal_grid_3d[0][y][x+1] == metal_grid_3d[0][y][x], metal_grid_3d[0][y-1][x] == 0, metal_grid_3d[0][y][x-1] == metal_grid_3d[0][y][x])
                f = And(metal_grid_3d[0][y+1][x] == 0, metal_grid_3d[0][y][x+1] == 0, metal_grid_3d[0][y-1][x] == metal_grid_3d[0][y][x], metal_grid_3d[0][y][x-1] == metal_grid_3d[0][y][x])
         
                s.add(Implies(metal_grid_3d[0][y][x] != 0,
                    Or(metal_grid_3d[0][y+1][x+1] == metal_grid_3d[0][y][x], metal_grid_3d[0][y+1][x+1] == 0)
                ))

                s.add(Implies(metal_grid_3d[0][y][x] != 0,
                    Or(metal_grid_3d[0][y-1][x+1] == metal_grid_3d[0][y][x], metal_grid_3d[0][y-1][x+1] == 0)
                ))

                s.add(Implies(metal_grid_3d[0][y][x] != 0,
                    Or(metal_grid_3d[0][y+1][x-1] == metal_grid_3d[0][y][x], metal_grid_3d[0][y+1][x-1] == 0)
                ))

                s.add(Implies(metal_grid_3d[0][y][x] != 0,
                    Or(metal_grid_3d[0][y-1][x-1] == metal_grid_3d[0][y][x], metal_grid_3d[0][y-1][x-1] == 0)
                ))

                any_val_n = Or(metal_grid_3d[0][y+1][x] == 0, Or([metal_grid_3d[0][y+1][x] == n for n in nets_set]))
                any_val_e = Or(metal_grid_3d[0][y][x+1] == 0, Or([metal_grid_3d[0][y][x+1] == n for n in nets_set]))
                any_val_s = Or(metal_grid_3d[0][y-1][x] == 0, Or([metal_grid_3d[0][y-1][x] == n for n in nets_set]))
                any_val_w = Or(metal_grid_3d[0][y][x-1] == 0, Or([metal_grid_3d[0][y][x-1] == n for n in nets_set]))
                

                za = And(any_val_n, any_val_e, any_val_s, any_val_w)

                s.add(Implies(And(metal_grid_3d[0][y][x] == metal_grid_3d[0][y+1][x+1], metal_grid_3d[0][y][x] != 0) , 
                        Or(
                            And(
                                metal_grid_3d[0][y][x] != metal_grid_3d[0][y][x+1],
                                metal_grid_3d[0][y][x] == metal_grid_3d[0][y+1][x]
                            ),
                            And(
                                metal_grid_3d[0][y][x] == metal_grid_3d[0][y][x+1],
                                metal_grid_3d[0][y][x] != metal_grid_3d[0][y+1][x]
                            )         
                        )
                    )   
                )

                s.add(Implies(And(metal_grid_3d[0][y][x] == metal_grid_3d[0][y-1][x-1], metal_grid_3d[0][y][x] != 0) , 
                        Or(
                            And(
                                metal_grid_3d[0][y][x] != metal_grid_3d[0][y][x-1],
                                metal_grid_3d[0][y][x] == metal_grid_3d[0][y-1][x]
                            ),
                            And(
                                metal_grid_3d[0][y][x] == metal_grid_3d[0][y][x-1],
                                metal_grid_3d[0][y][x] != metal_grid_3d[0][y-1][x]
                            )         
                        )
                    )   
                )
                s.add(Implies(And(metal_grid_3d[0][y][x] == metal_grid_3d[0][y-1][x+1], metal_grid_3d[0][y][x] != 0) , 
                        Or(
                            And(
                                metal_grid_3d[0][y][x] != metal_grid_3d[0][y][x+1],
                                metal_grid_3d[0][y][x] == metal_grid_3d[0][y-1][x]
                            ),
                            And(
                                metal_grid_3d[0][y][x] == metal_grid_3d[0][y][x+1],
                                metal_grid_3d[0][y][x] != metal_grid_3d[0][y-1][x]
                            )         
                        )
                    )   
                )
                s.add(Implies(And(metal_grid_3d[0][y][x] == metal_grid_3d[0][y+1][x-1], metal_grid_3d[0][y][x] != 0) , 
                        Or(
                            And(
                                metal_grid_3d[0][y][x] != metal_grid_3d[0][y][x-1],
                                metal_grid_3d[0][y][x] == metal_grid_3d[0][y+1][x]
                            ),
                            And(
                                metal_grid_3d[0][y][x] == metal_grid_3d[0][y][x-1],
                                metal_grid_3d[0][y][x] != metal_grid_3d[0][y+1][x]
                            )         
                        )
                    )   
                )

                s.add(Implies(metal_grid_3d[0][y][x] == 0, za))

                s.add(Implies(metal_grid_3d[0][y][x] != 0,
                            Or(
                                And(a,Not(b),Not(c),Not(d),Not(e),Not(f)),
                                And(Not(a),b,Not(c),Not(d),Not(e),Not(f)),
                                And(Not(a),Not(b),c,Not(d),Not(e),Not(f)),
                                And(Not(a),Not(b),Not(c),d,Not(e),Not(f)),
                                And(Not(a),Not(b),Not(c),Not(d),e,Not(f)),
                                And(Not(a),Not(b),Not(c),Not(d),Not(e),f)
                            )
                    )
                )
                
    
############################################################################################################################################
    #alpha = 0
    #sum_of_zeros = (Sum([Sum([If(metal_grid_3d[0][y][x] == 0, 1, 0) for x in range(1,grid_x-1)]) for y in range(1,grid_y-1)]))   
    #zeros_optimization =  (grid_x*grid_y*alpha) - 2*(grid_x+grid_y)
    #s.add(sum_of_zeros > zeros_optimization)
############################################################################################################################################   






    # for n in nets_set:                 
    #     for y in range(1, grid_y-1):    
    #         for x in range(1, grid_x-1):
    #             if not is_pin[y][x]:
    #                 s.add(
    #                     And(Or(metal_grid_3d[0][y][x]== n,Or(metal_grid_3d[0][y][x+1] == n,Or(metal_grid_3d[0][y+1][x] == n,metal_grid_3d[0][y-1][x] == n))),
    #                     And(Or(metal_grid_3d[0][y][x]== n,Or(metal_grid_3d[0][y][x-1] == n,Or(metal_grid_3d[0][y+1][x] == n,metal_grid_3d[0][y-1][x] == n))),
    #                     And(Or(metal_grid_3d[0][y][x]== n,Or(metal_grid_3d[0][y][x+1] == n,Or(metal_grid_3d[0][y][x-1] == n,metal_grid_3d[0][y-1][x] == n))),
    #                     And(Or(metal_grid_3d[0][y][x]== n,Or(metal_grid_3d[0][y][x+1] == n,Or(metal_grid_3d[0][y][x-1] == n,metal_grid_3d[0][y+1][x] == n))),
    #                     And(Or(metal_grid_3d[0][y][x]== n,Or(metal_grid_3d[0][y][x+1] != n,Or(metal_grid_3d[0][y+1][x] != n,metal_grid_3d[0][y-1][x] != n))),
    #                     And(Or(metal_grid_3d[0][y][x]== n,Or(metal_grid_3d[0][y][x-1] != n,Or(metal_grid_3d[0][y+1][x] != n,metal_grid_3d[0][y-1][x] != n))),
    #                     And(Or(metal_grid_3d[0][y][x]== n,Or(metal_grid_3d[0][y][x+1] != n,Or(metal_grid_3d[0][y][x-1] != n,metal_grid_3d[0][y-1][x] != n))),
    #                         Or(metal_grid_3d[0][y][x]== n,Or(metal_grid_3d[0][y][x+1] != n,Or(metal_grid_3d[0][y][x-1] != n,metal_grid_3d[0][y+1][x] != n))))))))))
    #                 )

    # for y in range(1, grid_y-1):    
    #     for x in range(1, grid_x-1):
    #         s.add(Or(metal_grid_3d[0][y][x] == 0, Or([metal_grid_3d[0][y][x] == n for n in nets_set])))


    # for y in range(1, grid_y-1):    
    #     for x in range(1, grid_x-1):
    #         if not is_pin[y][x]:
    #             s.add(
    #                     Or(And(metal_grid_3d[0][y+1][x] == metal_grid_3d[0][y][x], And(metal_grid_3d[0][y-1][x] == metal_grid_3d[0][y][x], And(metal_grid_3d[0][y][x+1] != metal_grid_3d[0][y][x], metal_grid_3d[0][y][x-1] != metal_grid_3d[0][y][x]))),
    #                             Or(And(metal_grid_3d[0][y+1][x] == metal_grid_3d[0][y][x], And(metal_grid_3d[0][y-1][x] != metal_grid_3d[0][y][x], And(metal_grid_3d[0][y][x+1] == metal_grid_3d[0][y][x], metal_grid_3d[0][y][x-1] != metal_grid_3d[0][y][x]))),
    #                             Or(And(metal_grid_3d[0][y+1][x] == metal_grid_3d[0][y][x], And(metal_grid_3d[0][y-1][x] != metal_grid_3d[0][y][x], And(metal_grid_3d[0][y][x+1] != metal_grid_3d[0][y][x], metal_grid_3d[0][y][x-1] == metal_grid_3d[0][y][x]))),
    #                             Or(And(metal_grid_3d[0][y+1][x] != metal_grid_3d[0][y][x], And(metal_grid_3d[0][y-1][x] == metal_grid_3d[0][y][x], And(metal_grid_3d[0][y][x+1] == metal_grid_3d[0][y][x], metal_grid_3d[0][y][x-1] != metal_grid_3d[0][y][x]))),
    #                             Or(And(metal_grid_3d[0][y+1][x] != metal_grid_3d[0][y][x], And(metal_grid_3d[0][y-1][x] == metal_grid_3d[0][y][x], And(metal_grid_3d[0][y][x+1] != metal_grid_3d[0][y][x], metal_grid_3d[0][y][x-1] == metal_grid_3d[0][y][x]))),
    #                             Or(And(metal_grid_3d[0][y+1][x] != metal_grid_3d[0][y][x], And(metal_grid_3d[0][y-1][x] != metal_grid_3d[0][y][x], And(metal_grid_3d[0][y][x+1] == metal_grid_3d[0][y][x], metal_grid_3d[0][y][x-1] == metal_grid_3d[0][y][x])))))))))
                                   
    #             )
                                            
    intlist = []   
    is_pin_int = []         
    for y in is_pin:
        intmap = map(int, y) 
        intlist = list(intmap)
        is_pin_int.append(intlist) 
        
    for p in is_pin_int:
        print(p)
        
       
    if first_route:        
        met1Grid = Grid('m1', grid_x, grid_y)
                
    if s.check()==sat:
        m = s.model()
        print('OK')
        
        met1Grid = Grid('M1', grid_x, grid_y)

        for j in range(grid_y):
            l = []
            for i in range(grid_x):
                l.append(int(str(m.eval(metal_grid_3d[0][j][i])))) if type(m.eval(metal_grid_3d[0][j][i])) is z3.z3.IntNumRef else l.append(0)
                met1Grid.occupy_one_point(i,j,int(str(m.eval(metal_grid_3d[0][j][i]))) if type(m.eval(metal_grid_3d[0][j][i])) is z3.z3.IntNumRef else 0)
            print(l)
            
        
        print(type(m.eval(metal_grid_3d[0][1][1])))
        
        print(s.statistics())

        first_route = False
        return met1Grid

    else:
        print('UNSAT')
        return met1Grid
    
""" nt = {5: [[1, 3], [11, 3]], 4: [[2, 6], [6, 10]], 2: [[3, 3], [6, 0]], 15: [[3, 13], [11, 13]], 7: [[4, 8]], 8: [[5, 3], [7, 3]], 11: [[5, 13], [9, 3]], 1: [[6, 16], [9, 13]], 13: [[8, 8]], 10: [[10, 8]]}
route(['m1', 'm2', 'm3'], nt, 25, 20) """