from objects import *
from secrets import randbelow

class Level:
    def __init__(self,txt):
        file=open(txt,"r")
        self.tiles={}
        self.dots={}
        self.dotNumber=0
        self.ghosts=[]
        self.nodes=[]
        self.connections=[]
        self.distances={}
        y=0
        for line in file.readlines():
            x=0
            for char in line:
                if char=="#":
                    self.tiles[(x,y)]=Wall(x,y)
                elif char=="-":
                    self.tiles[(x,y)]=Wall(x,y,"gate")
                elif char==" ":
                    self.tiles[(x,y)]=Space(x,y)
                elif char==".":
                    self.tiles[(x,y)]=Space(x,y)
##                    self.dots[(x,y)]=Dot(x,y)
##                    self.dotNumber+=1
                elif char=="o":
                    self.tiles[(x,y)]=Space(x,y)
##                    self.dots[(x,y)]=Dot(x,y,"big")
##                    self.dotNumber+=1
                elif char=="^":
                    self.tiles[(x,y)]=Space(x,y)
                    self.ghosts.append(Ghost(x,y,"pink"))
                    self.ghosts.append(Ghost(x,y,"red"))
                elif char=="e":
                    self.tiles[(x,y)]=Space(x,y)
                    self.player=Pacman(x,y)
                elif char=="(":
                    self.tiles[(x,y)]=Loop(x,y,"left")
                elif char==")":
                    self.tiles[(x,y)]=Loop(x,y,"right")
                elif char!="\n":
                    print("error!")
                x+=1
            y+=1
        self.width=x
        self.height=y
        for tile in self.tiles.values():
            if tile.type=="space": self.checkifNode(tile.x,tile.y)
        for n in range(len(self.nodes)):
            self.checkDistance(n)
        for ghost in self.ghosts:
            ghost.nextNode=self.tiles[(ghost.x,ghost.y-2)]
##            ghost.planner.start()
            #ghost.plan_move(self)
    def checkifNode(self,x,y):
        flagV=0
        flagH=0
        connections=[0,0,0,0]
        if (x+1,y) in self.tiles and self.tiles[(x+1,y)].type=="space":
            flagH=1
            connections[0]=1
        if (x,y-1) in self.tiles and self.tiles[(x,y-1)].type=="space":
            flagV=1
            connections[1]=1
        if (x-1,y) in self.tiles and self.tiles[(x-1,y)].type=="space":
            flagH=1
            connections[2]=1
        if (x,y+1) in self.tiles and self.tiles[(x,y+1)].type=="space":
            flagV=1
            connections[3]=1
        if (x,y+1) in self.tiles and self.tiles[(x,y+1)].type=="wall" and self.tiles[(x,y+1)].gate=="yes":
            flagV=1
        if flagH+flagV==2:
            node=self.tiles[(x,y)]
            node.node="yes"
            self.nodes.append(node)
            self.connections.append([connections,[None,None,None,None]])
    def checkDistance(self,n):
        if self.connections[n][0][0]==1:
            x=self.nodes[n].x
            y=self.nodes[n].y
            while self.tiles[(x+1,y)].node!="yes":
                if self.tiles[(x+1,y)].type=="loop": x=0
                else: x+=1
                self.connections[n][0][0]+=1
            self.connections[n][1][0]=self.nodes.index(self.tiles[(x+1,y)])
        if self.connections[n][0][1]==1:
            x=self.nodes[n].x
            y=self.nodes[n].y
            while self.tiles[(x,y-1)].node!="yes":
                y-=1
                self.connections[n][0][1]+=1
            self.connections[n][1][1]=self.nodes.index(self.tiles[(x,y-1)])
        if self.connections[n][0][2]==1:
            x=self.nodes[n].x
            y=self.nodes[n].y
            while self.tiles[(x-1,y)].node!="yes":
                if self.tiles[(x-1,y)].type=="loop": x=self.width-2
                else: x-=1
                self.connections[n][0][2]+=1
            self.connections[n][1][2]=self.nodes.index(self.tiles[(x-1,y)])
        if self.connections[n][0][3]==1:
            x=self.nodes[n].x
            y=self.nodes[n].y
            while self.tiles[(x,y+1)].node!="yes":
                y+=1
                self.connections[n][0][3]+=1
            self.connections[n][1][3]=self.nodes.index(self.tiles[(x,y+1)])
    def closestNode(self,x,y):
        distances=[]
        for node in self.nodes:
            distances.append(((node.x-x)**2+(node.y-y)**2)**0.5)
        pnt=[0]
        for i in range(len(distances)):
            if distances[i]<distances[pnt[0]]: pnt=[i]
            #if distances[i]==distances[pnt[0]]: pnt.append(i)
        return self.nodes[pnt[randbelow(len(pnt))]]
