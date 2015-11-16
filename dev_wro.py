#           0        1      2      3        4       5      6       7
COLORS = ['None','Black','Blue','Green','Yellow','Red','White','Brown']
MOUNTAIN = 1
CUBE = 0

NONE = 0
BLACK = 1
BLUE = 2
GREEN = 3
YELLOW = 4
RED = 5
WHITE = 6
BROWN = 7


pos = [ 
        [ [1,3],[0,3],[0,4],[1,4] ], 
        [ [1,2],[0,2],[0,5],[1,5] ], 
      ]

def floor_print():
    txt = []
    
    for i in range(4):
        for c in [' ','-','-',' ']:
            txt.append(c*6)

    if pos[0][1][0]==MOUNTAIN:
        txt[8]  = COLORS[pos[0][1][1]].center(6,' ')
        txt[13] = COLORS[pos[0][0][1]].center(6,'-')
    else:    
        txt[9]  = COLORS[pos[0][1][1]].center(6,'-')
        txt[12] = COLORS[pos[0][0][1]].center(6,' ')

    if pos[0][2][0]==MOUNTAIN:
        txt[4]  = COLORS[pos[0][2][1]].center(6,' ')
        txt[1]  = COLORS[pos[0][3][1]].center(6,'-')
    else:    
        txt[0]  = COLORS[pos[0][3][1]].center(6,' ')
        txt[5]  = COLORS[pos[0][2][1]].center(6,'-')

    if pos[1][1][0]==MOUNTAIN:
        txt[11] = COLORS[pos[1][1][1]].center(6,' ')
        txt[14] = COLORS[pos[1][0][1]].center(6,'-')
    else:    
        txt[15] = COLORS[pos[1][0][1]].center(6,' ')
        txt[10] = COLORS[pos[1][1][1]].center(6,'-')

    if pos[1][2][0]==MOUNTAIN:
        txt[7]  = COLORS[pos[1][2][1]].center(6,' ')
        txt[2]  = COLORS[pos[1][3][1]].center(6,'-')
    else:    
        txt[3]  = COLORS[pos[1][3][1]].center(6,' ')
        txt[6]  = COLORS[pos[1][2][1]].center(6,'-')
        

    print '''+-------------+                          +-------------+
|             |                          |             |
|   '''+txt[00]+'''    |-'''+txt[01]+'''------------'''+txt[02]+'''-|   '''+txt[03]+'''    |
|             |                          |             |
|   '''+txt[04]+'''    |-'''+txt[05]+'''------------'''+txt[06]+'''-|   '''+txt[07]+'''    |
|             |                          |             |
+-------------+                          +-------------+
|             |                          |             |
|   '''+txt[ 8]+'''    |-'''+txt[ 9]+'''------------'''+txt[10]+'''-|   '''+txt[11]+'''    |
|             |                          |             |
|   '''+txt[12]+'''    |-'''+txt[13]+'''------------'''+txt[14]+'''-|   '''+txt[15]+'''    |
|             |                          |             |
+-------------+                          +-------------+'''


#           0        1      2      3        4       5      6       7
#COLORS = ['None','Black','Blue','Green','Yellow','Red','White','Brown']

code = [
    RED,BLUE,GREEN,YELLOW,
    YELLOW,GREEN,BLUE,RED,
    ]

print "Code:",
for color in code:
    print COLORS[color],
print

#place mountain color everywhere first
pos[0][0][1] = GREEN
pos[0][1][1] = GREEN
pos[0][2][1] = YELLOW
pos[0][3][1] = YELLOW
pos[1][0][1] = BLUE
pos[1][1][1] = BLUE
pos[1][2][1] = RED
pos[1][3][1] = RED

#mark everything as a cube position
for x in range(2):
    for y in range(4):
        pos[x][y][0] = CUBE

#mark mountain and then cube color
#Yellow Mountain
pos[0][2+(code[4]==YELLOW)][0] = MOUNTAIN
pos[0][3-(code[4]==YELLOW)][1] = code[0]
#Green Mountain
pos[0][1-(code[5]==GREEN)][0] = MOUNTAIN
pos[0][0+(code[5]==GREEN)][1] = code[1]
#Blue Mountain
pos[1][1-(code[6]==BLUE)][0] = MOUNTAIN
pos[1][0+(code[6]==BLUE)][1] = code[2]
#Red Mountain
pos[1][2+(code[7]==RED)][0] = MOUNTAIN
pos[1][3-(code[7]==RED)][1] = code[3]
print pos[0]
print pos[1]
floor_print()

xpos,ypos = 0,0
ydistance = [
    [00,20,40,60],
    [20,00,20,40],
    [40,20,00,20],
    [60,40,20,00],
    ]
def goto(x,y):
    # if destination is on the same latitude, then we turn around and move to the other side.
    global xpos,ypos
    if (y == ypos) and (x == xpos): 
        print "Nothing to do."
        return
    if y == ypos:
        side_for_180_turn = [ [1,1,-1,-1], [-1,-1,1,1] ]
        print "Turn",180*side_for_180_turn[xpos][ypos],' degres'
    elif y < ypos: #on Descend
        print "Turn Left 90 degres"
        print "Move",ydistance[ypos][y],'cm ahead'
        if ((x==xpos) and (xpos==0)) or (x < xpos):
            print "Find line and turn RIGHT 90 degres"
        elif ((x==xpos) and (xpos==1)) or (x > xpos):
            print "Find line and turn LEFT 90 degres"
        else:
            print "BIG TROUBLE IF WE CAME TO THIS CONDITON !!!!"
    elif y > ypos: #On monte
        print "Turn Right 90 degres"
        print "Move",ydistance[ypos][y],'cm ahead'
        if ((x==xpos) and (xpos==0)) or (x < xpos):
            print "Find line and turn LEFT 90 degres"
        elif ((x==xpos) and (xpos==1)) or (x > xpos):
            print "Find line and turn RIGHT 90 degres"
        else:
            print "BIG TROUBLE IF WE CAME TO THIS CONDITON !!!!"
    if (x <> xpos):
        print "Move ahead 90 cm (move to the other side)"
                
    xpos,ypos = x,y

goto(0,pos[0][0][0]==MOUNTAIN)
block_color = pos[0][pos[0][0][0]==MOUNTAIN][1]
print 'Grab',COLORS[block_color],'block'
pos[0][pos[0][0][0]==MOUNTAIN][1] = BLACK #Mark block as gone.

while True:
    #Find where this block is going:
    tx,ty = None,None
    for x in range(2):
        for y in range(4):
            if (pos[x][y][0]==MOUNTAIN) and (pos[x][y][1]==block_color):
                tx,ty = x,y
    print COLORS[block_color],'is going to be places at',tx,ty
    goto(tx,ty)
    print "Place Block at pos ",xpos,ypos
    #floor_print()
    print
    #find if there is a block beside us:
    tx,ty = xpos,ypos
    ty += [+1,-1,+1,-1][ty]
    print "check",tx,ty
    if pos[tx][ty][1] <> BLACK:
        goto(tx,ty)
    else:
        #Nope, so we search for the next remaining block
        tx,ty = None,None
        for x in range(2):
            for y in range(4):
                if (pos[x][y][0]==CUBE) and (pos[x][y][1] <> BLACK):
                    tx,ty = x,y
                    print "Found a cube at",xpos,ypos
        if tx == None:
            print "All done !"
            break
        goto(tx,ty)
    block_color = pos[xpos][ypos][1]
    print 'Grab',COLORS[block_color],'block'
    pos[xpos][ypos][1] = BLACK #Mark block as gone.
