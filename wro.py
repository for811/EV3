#!/usr/bin/python

import time
import sys
import signal
from ev3.lego import *
import os


##def signal_handler(signal, frame):
##        print('You pressed Ctrl+C!')
##        dr.run_forever(0, stop_mode=Motor.STOP_MODE.BRAKE)
##        dl.run_forever(0, stop_mode=Motor.STOP_MODE.BRAKE)
##        sys.exit(0)
##signal.signal(signal.SIGINT, signal_handler)

dl = LargeMotor('A')
dr = LargeMotor('B')
dbras = LargeMotor('C')
dpinces = LargeMotor('D')

dl.reset()
dr.reset()


LEFT = 0
CENTER = 1
RIGHT = 2

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

OPEN = -1
CLOSE = 1


#           0        1      2      3        4       5      6       7
COLORS = ['None','Black','Blue','Green','Yellow','Red','White','Brown']
sensor = [LegoSensor(1),LegoSensor(2),LegoSensor(3)]


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




class CalibratedSensor():
    def __init__(self,sensor,min,max):
        self.sensor = sensor
        self.min = min
        self.max = max
    def contrast(self):
        r = self.sensor.value0 
        d = float(((r - self.min))) / (self.max-self.min) * 100.0
        if r < self.min:
            print 'Error sensor is below minimum calibrated value ('+str(self.min)+'):',r
        if r > self.max:
            print 'Error sensor is over maximum calibrated value ('+str(self.max)+'):',r
        #return self.min,self.max,r,d
        return d


if False:
    for s in sensor:
        s.mode = 'REF-RAW'
    dl.reset()
    dr.reset()
    dl.setup_position_limited(int(15 * (1000/48.2)), int(10*7), absolute=False,stop_mode=Motor.STOP_MODE.BRAKE)
    dr.setup_position_limited(int(15 * (1000/48.2)), int(10*7), absolute=False,stop_mode=Motor.STOP_MODE.BRAKE)
    dl.start()
    dr.start()
    min = [9999,9999,9999]
    max = [0,0,0]
    n = 0
    time.sleep(0.25)

    while (dl.state == 'running') or (dr.state == 'running'):
        for i in range(3):
            d = sensor[i].value0
            if d < min[i]:
                min[i] = d
            if d > max[i]:
                max[i] = d
        n += 1

    print min
    print max
    print "Samples",n
else:
    min = [511,519,509]
    max = [641,632,625]
csensor = []
for i in range(3):
    csensor.append(CalibratedSensor(sensor[i],int(min[i] - (min[i]*0.02)),int(max[i] + (max[i]*0.02))))



def follow_line2(distance,speed=50,side=0,delay=999,break_on_color=None, break_on_line=False,break_on_arrival=True):
    sensor[CENTER].mode = 'REF-RAW'
    if break_on_color == None:
        sensor[LEFT].mode = 'REF-RAW'
        sensor[RIGHT].mode = 'REF-RAW'
    else:
        sensor[LEFT].mode = 'COL-COLOR'
        sensor[RIGHT].mode = 'COL-COLOR'

    m = [dl,dr]
    m[0].reset()
    m[1].reset()
    m[0].run_forever(int(speed))
    m[1].run_forever(int(speed))
    n = 0
    spd = 0.0
    f = 2.0
    ri = (csensor[CENTER].contrast()-50) * f
    line_detected = [0,0]
    while (m[side].position < (distance * (1000/48.2))) and (m[side^1].position < (distance * (1000/48.2))):
        if break_on_color==None:
            if (csensor[LEFT].contrast() > 25) or (csensor[RIGHT].contrast() > 25):
                if break_on_line:
                    m[0].stop()
                    m[1].stop()
                    print "Stop because line detected"
                    return
                else:
                    line_detected = [side,m[side].position]
                    if line_detected[1] < m[side^1].position:
                        line_detected = [side^1,m[side^1].position]
                    line_detected[1] += 3*(1000/48.2)
        else:
            if (sensor[LEFT].value0==BLACK) or (sensor[RIGHT].value0==BLACK):
                m[0].stop()
                m[1].stop()
                print "Stop because ",COLORS[break_on_color],"line detected"
                return
            
        r = csensor[CENTER].contrast() - 50
        ri = ((ri / f) * (f-1)) + r
        r = ri / f
        spd = (abs(r)/50.0)
        #if spd > 100:
        #    spd = 100
        #if spd < 0:
        #    spd = 0
        #print m[line_detected[0]].position,line_detected
        if m[line_detected[0]].position < line_detected[1]:
            r = 0
            print "Passing a line !!!"
        #print r,csensor[LEFT].contrast(),csensor[RIGHT].contrast()
        sp = speed - ((speed*0.6) * spd)
        if r > 0:
            #print int(speed),int(sp)
            m[side].run_forever(int(speed))         
            m[side^1].run_forever(int(sp))
        elif r < 0:
            #print int(sp),int(speed)
            m[side].run_forever(int(sp))            
            m[side^1].run_forever(int(speed))
        else:
            #print int(speed),int(speed)
            m[side].run_forever(int(speed))            
            m[side^1].run_forever(int(speed))
        n+=1
    print "Stop because distance reached"
    m[side].stop()
    m[side^1].stop()

def run_straight_to(distance,speed=50,nline=999,delay=999):
    st = time.time()
    n = 0
    osl,osr = None,None
    distance *= 1000 /48.2
    dl.reset()
    dr.reset()
    dl.setup_position_limited(int(distance), int(speed*7), absolute=False,stop_mode=Motor.STOP_MODE.BRAKE)
    dr.setup_position_limited(int(distance), int(speed*7), absolute=False,stop_mode=Motor.STOP_MODE.BRAKE)
    print dl.position, dr.position
    dl.start()
    dr.start()
    while ((time.time()-st) < delay):
        n+=1
        if (distance > 0) and ((dl.position >= distance) or (dr.position >= distance)):
            break
        if (distance < 0) and ((dl.position <= distance) or (dr.position <= distance)):
            break
    dr.run_forever(0, stop_mode=Motor.STOP_MODE.BRAKE)
    dl.run_forever(0, stop_mode=Motor.STOP_MODE.BRAKE)
    return 0

def turn(degree=0,speed=50):
    sr = (speed / 2.0)*10 
    sl = (speed / 2.0)*10
    pl = degree * 2.955
    pr = pl
    print pl,pr
    pr *= -1
    dl.setup_position_limited(int(pl*0.8), int(sl*0.8), absolute=False,stop_mode=Motor.STOP_MODE.BRAKE)
    dr.setup_position_limited(int(pr*1.2), int(sr*1.2), absolute=False,stop_mode=Motor.STOP_MODE.BRAKE)
    dl.start()
    dr.start()
    while (dl.state == 'running') or (dr.state == 'running'):
        time.sleep(0.01)
    print "Done turning",degree,'degree'
    return 0

def turn_and_search_line(degree=0,speed=50):
    sr = (speed / 2.0)*10 
    sl = (speed / 2.0)*10
    pl = degree * 2.955
    pr = pl - 100
    if degree > 0:
        pr *= -1
    else:
        pl *= -1
    dl.reset()
    dr.reset()
    f1 = 0.75
    f2 = 1.25
    dl.setup_position_limited(int(pl*f1), int(sl*f1), absolute=False,stop_mode=Motor.STOP_MODE.BRAKE)
    dr.setup_position_limited(int(pr*f2), int(sr*f2), absolute=False,stop_mode=Motor.STOP_MODE.BRAKE)
    dl.start()
    dr.start()
    while (dl.state == 'running') and (dr.state == 'running'):
        time.sleep(0.01)
    if degree > 0:
        sr *= -1
    else:
        sl *= -1
    dl.run_forever(int(sl/3*f1))
    dr.run_forever(int(sr/3*f2))
    if degree < 0:
        while csensor[CENTER].contrast() < 25:
            time.sleep(0.005)
    else:
        while csensor[CENTER].contrast() < 25:
            time.sleep(0.005)
        while csensor[CENTER].contrast() < 50:
            time.sleep(0.005)
        while csensor[CENTER].contrast() > 50:
            time.sleep(0.005)
    dl.stop()
    dr.stop()
    print "Done turning",degree,'degree'
    return 0


def find_line_ahead_and_turn(side,speed=15):
    for s in sensor:
        s.mode = 'REF-RAW'
    #while 1:
    #    for i in range(3):
    #        print csensor[i].contrast(),
    #    print
    m = [dl,dr]
    dl.reset()
    dr.reset()
    dl.run_forever(int(speed))
    dr.run_forever(int(speed))
    while (csensor[RIGHT].contrast() < 25) and (csensor[LEFT].contrast() < 25):
        #for i in range(3):
        #    print int(csensor[i].contrast()),
        #print
        time.sleep(0.01)
    print 'Line Found!'
    m[side^1].stop()
    m[side].stop()
    dl.reset()
    dr.reset()
    m[side^1].setup_position_limited(600*0.8, int(speed*10.0), absolute=False)
    m[side].setup_position_limited(186*0.8, int(speed*3), absolute=False)
    dl.start()
    dr.start()
    while (dl.state == 'running') and (dr.state == 'running'):
        time.sleep(0.01)
        #print dl.position,dr.position
    print dl.position,dr.position,'---1---'
    dl.reset()
    dr.reset()
    m[side^1].setup_position_limited(100, int(speed*10.0), absolute=False)
    m[side].setup_position_limited(100, int(speed*10.0), absolute=False)
    dl.start()
    dr.start()
    while (dl.state == 'running') and (dr.state == 'running'):
        time.sleep(0.01)
        #print dl.position,dr.position
    print dl.position,dr.position,'---2---'

    m[side^1].run_forever(int(speed*6))
    m[side  ].run_forever(int(speed*3))

    if side == 0:
        
        while csensor[CENTER].contrast() < 25:
            time.sleep(0.005)
    else:
        while csensor[CENTER].contrast() < 25:
            time.sleep(0.005)
        while csensor[CENTER].contrast() < 50:
            time.sleep(0.005)
        while csensor[CENTER].contrast() > 50:
            time.sleep(0.005)
    dl.stop()
    dr.stop()

    print dl.position,dr.position,'final'

def pinces(side=0):
    dpinces.reset()
    print "Pinces to",600*(side*-1)
    dpinces.setup_position_limited(6100*(side*-1), int(2000), absolute=False)
    dpinces.start()
    while dpinces.state=='running':
        time.sleep(0.01)
    print "Done"

def bras(side=0):
    dbras.reset()
    dbras.setup_position_limited(200*(side), int(200), absolute=False)
    dbras.start()
    while dbras.state=='running':
        time.sleep(0.01)
    print "Done"


raw_input("Press enter to start")
    
code = []

if True:
    distance = 65 * (1000/48.2)
    sensor[CENTER].mode = 'COL-COLOR'
    dl.reset()
    dr.reset()
    dl.setup_position_limited(int(distance), int(15*7), absolute=False,stop_mode=Motor.STOP_MODE.BRAKE)
    dr.setup_position_limited(int(distance), int(15*7), absolute=False,stop_mode=Motor.STOP_MODE.BRAKE)
    dl.start()
    dr.start()

    ac = [0,0,0,0,0,0,0,0]
    cl = None
    while (dl.state == 'running') or (dr.state == 'running'):
        c = sensor[CENTER].value0
        ac[c] += 1
        if cl <> c:
            print ac,
            for n,i in enumerate(ac):
                if i > 10:
                    print COLORS[n]+'['+str(i)+']',
                    if n <> 6:
                        code.append(n)
            print
            ac = [0,0,0,0,0,0,0,0]
        cl = c
        time.sleep(0.01)
    dl.stop()
    dr.stop()
else:
    code = [
        RED,BLUE,YELLOW,GREEN,
        GREEN,GREEN,RED,BLUE,
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
    [00,07,32,66],
    [07,00,00,32],
    [32,00,00,07],
    [66,32,07,00],
    ]
def goto(x,y):
    # if destination is on the same latitude, then we turn around and move to the other side.
    global xpos,ypos
    print "Goto("+str(x)+","+str(y)+") from ("+str(xpos)+","+str(ypos)+")"
    if (y == ypos) and (x == xpos): 
        print "Nothing to do."
        return
    if y == ypos:
        side_for_180_turn = [ [1,1,-1,-1], [-1,-1,1,1] ]
        print "Turn",180*side_for_180_turn[xpos][ypos],' degres'
        turn_and_search_line(180*side_for_180_turn[xpos][ypos])
    elif y < ypos: #on Descend
        if xpos==0:
            print "1-Turn Left 90 degres"
            turn(-90)
        else:
            print "2-Turn Right 90 degres"
            turn(90)
        print "Move",ydistance[ypos][y],'cm ahead'
        run_straight_to(ydistance[ypos][y])
        if ((x==xpos) and (xpos==0)) or (x < xpos):
            print "Find line and turn RIGHT 90 degres"
            find_line_ahead_and_turn(1,20)
        elif ((x==xpos) and (xpos==1)) or (x > xpos):
            print "Find line and turn LEFT 90 degres"
            find_line_ahead_and_turn(0,20)
        else:
            print "BIG TROUBLE IF WE CAME TO THIS CONDITON !!!!"
    elif y > ypos: #On monte
        if xpos==0:
            print "3-Turn Right 90 degres"
            turn(90)
        else:
            print "4-Turn Left 90 degres"
            turn(-90)
        print "Move",ydistance[ypos][y],'cm ahead'
        run_straight_to(ydistance[ypos][y])
        if ((x==xpos) and (xpos==0)) or (x < xpos):
            print "Find line and turn LEFT 90 degres"
            find_line_ahead_and_turn(0,20)
        elif ((x==xpos) and (xpos==1)) or (x > xpos):
            print "Find line and turn RIGHT 90 degres"
            find_line_ahead_and_turn(1,20)
        else:
            print "BIG TROUBLE IF WE CAME TO THIS CONDITON !!!!"
    if (x <> xpos):
        print "Move ahead 90 cm (move to the other side)"
        follow_line2(60,40)
    print "Done Goto"
    xpos,ypos = x,y

find_line_ahead_and_turn(1,20)
#follow_line2(50,40,side=0,break_on_line=True)
#run_straight_to(-30,40)
goto(0,pos[0][0][0]==MOUNTAIN)
follow_line2(25,20,delay=3,break_on_color=BLACK)
run_straight_to(-2,30)
block_color = pos[0][pos[0][0][0]==MOUNTAIN][1]
print 'Grab',COLORS[block_color],'block'
pinces(CLOSE)
time.sleep(1)
pos[0][pos[0][0][0]==MOUNTAIN][1] = BLACK #Mark block as gone.
run_straight_to(-25,40)

while True:
    #Find where this block is going:
    tx,ty = None,None
    for x in range(2):
        for y in range(4):
            if (pos[x][y][0]==MOUNTAIN) and (pos[x][y][1]==block_color):
                tx,ty = x,y
    print COLORS[block_color],'is going to be places at',tx,ty
    goto(tx,ty)
    follow_line2(15,35,delay=2,break_on_line=True)
    print "Place Block at pos ",xpos,ypos
    bras(OPEN)
    pinces(OPEN)
    time.sleep(0.5)
    bras(CLOSE)
    run_straight_to(-16,50)

    floor_print()
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
    follow_line2(25,20,delay=3,break_on_color=BLACK)
    run_straight_to(-2,30)
    block_color = pos[xpos][ypos][1]
    print 'Grab',COLORS[block_color],'block'
    pinces(CLOSE)
    time.sleep(0.5)
    pos[xpos][ypos][1] = BLACK #Mark block as gone.
    run_straight_to(-25,40)
