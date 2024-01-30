
from PIL import Image, ImageDraw, ImageFont

def drawLayers(grlayers, col, row, circDict):
       
    w = 35*col
    h = 35*row
    
    
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
   
     
    fnt = ImageFont.truetype('arial.ttf', 20)
    
    colorcount = 0
    color = ['green', 'red', 'yellow', 'blue']
    fixedLayers = ['RX', 'POLY', 'CA', 'M1']
    modd = [[0,0,30,30],[5,-10,25,40], [0,0,30,30], [0,0,30,30]]
    
    
    
    for gr in grlayers:    
        for i in range(len(fixedLayers)):
            if gr.layer == fixedLayers[i]:
                drawMod = i
        for idx_x in range(col):
            for idx_y in range(row):
                if gr.grid[idx_x][idx_y] != 0:
                    
                    shape = [((30*idx_x)+modd[drawMod][0], (30*idx_y)+modd[drawMod][1]), ((30*idx_x)+modd[drawMod][2], (30*idx_y)+modd[drawMod][3])]
                    
                    if(fixedLayers[drawMod] == 'M1'):
                        draw.rectangle(shape, outline='blue')
                        draw.text(((30*idx_x)+modd[drawMod][0], (30*idx_y)+modd[drawMod][1]), text = str(gr.grid[idx_x][idx_y]), font=fnt, fill = 'white')
                        
                    else:
                        draw.rectangle(shape, fill = color[colorcount])
                    
                    if(fixedLayers[drawMod] == 'CA'):
                        draw.text(((30*idx_x)+modd[drawMod][0], (30*idx_y)+modd[drawMod][1]), text = list(circDict.keys())[list(circDict.values()).index(gr.grid[idx_x][idx_y])], font=fnt, fill = 'blue')

                    # if(fixedLayers[drawMod] == 'M1'):
                    #     draw.text(((30*idx_x)+modd[drawMod][0], (30*idx_y)+modd[drawMod][1]), text = str(gr.grid[idx_x][idx_y]), font=fnt, fill = 'white')

        colorcount = colorcount + 1
        
    
    # creating new Image object
    
    
    # create rectangle image 
    img.show()
    
   