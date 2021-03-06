from tkinter import W
from PIL import Image, ImageDraw

def drawLayers(grlayers, col, row):
       
    w = 40*col
    h = 40*row
    
   
       
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img) 
    
    colorcount = 0
    color = ['green', 'red', 'yellow', 'blue']
    fixedLayers = ['RX', 'POLY', 'CA']
    modd = [[0,0,30,30],[10,-10,20,40], [5,5,25,25]]
    
    for gr in grlayers:    
        for i in range(len(fixedLayers)):
            if gr.layer == fixedLayers[i]:
                drawMod = i
        for idx_x in range(col):
            for idx_y in range(row):
                if gr.grid[idx_x][idx_y] != 0:
                    shape = [((30*idx_x)+modd[drawMod][0], (30*idx_y)+modd[drawMod][1]), ((30*idx_x)+modd[drawMod][2], (30*idx_y)+modd[drawMod][3])]
                    draw.rectangle(shape, fill = color[colorcount])
        
        colorcount = colorcount + 1
        
    
    # creating new Image object
    
    
    # create rectangle image 
    img.show()
    
   