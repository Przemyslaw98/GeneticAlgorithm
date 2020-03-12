import arcade
import threading
from secrets import randbelow
from pathfinder import *

class Pacman:
    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.move_x=0
        self.move_y=0
        self.dir=4
        self.next=4
        self.sprites=[]
        self.spriteNumber=0
        self.sprites.append(arcade.Sprite("graphics/p2.png",1))
        self.sprites.append(arcade.Sprite("graphics/p1.png",1))
        self.sprites.append(arcade.Sprite("graphics/p0.png",1))
        self.sprites.append(arcade.Sprite("graphics/p1.png",1))
        self.sprites.append(arcade.Sprite("graphics/p2.png",1))
        self.sprites.append(arcade.Sprite("graphics/p3.png",1))
        self.sprites.append(arcade.Sprite("graphics/p4.png",1))
        self.sprites.append(arcade.Sprite("graphics/p3.png",1))
    def draw(self):
        if self.spriteNumber>7:
            self.spriteNumber=0
        self.sprites[self.spriteNumber].angle=self.dir*90
        self.sprites[self.spriteNumber].center_x=self.x*32+16+self.move_x
        self.sprites[self.spriteNumber].center_y=768-(self.y*32+16+self.move_y)
        self.sprites[self.spriteNumber].draw()
        
class Ghost:
    def __init__(self,x,y,color):
        self.x=x
        self.y=y
        self.color=color
        self.dir=1
        self.movement=64
        self.move_x=0
        self.move_y=0
        self.sprites=[]
        self.nextNode=None
        self.nextMove=None
        self.target=None
        self.targetNode=None
        self.planner=threading.Thread()
        self.threadLoop=True
        self.pathArray=[]
        self.preferredPath=[]
        self.pathLock=threading.Lock()
        self.startLock=threading.Lock()
        self.endLock=threading.Lock()
        if self.color=="red":
            self.sprites.append(arcade.Sprite("graphics/grr.png",1))
            self.sprites.append(arcade.Sprite("graphics/gru.png",1))
            self.sprites.append(arcade.Sprite("graphics/grl.png",1))
            self.sprites.append(arcade.Sprite("graphics/grd.png",1))
            self.nodeSprite=arcade.Sprite("graphics/grn.png",1)
            self.targetSprite=arcade.Sprite("graphics/grt.png",1)
        elif self.color=="pink":
            self.sprites.append(arcade.Sprite("graphics/gpr.png",1))
            self.sprites.append(arcade.Sprite("graphics/gpu.png",1))
            self.sprites.append(arcade.Sprite("graphics/gpl.png",1))
            self.sprites.append(arcade.Sprite("graphics/gpd.png",1))
            self.nodeSprite=arcade.Sprite("graphics/gpn.png",1)
            self.targetSprite=arcade.Sprite("graphics/gpt.png",1)
    def draw(self):
        self.sprites[self.dir].center_x=self.x*32+16+self.move_x
        self.sprites[self.dir].center_y=768-(self.y*32+16+self.move_y)
        self.sprites[self.dir].draw()
    def drawNode(self):
        self.nodeSprite.center_x=self.nextNode.x*32+16
        self.nodeSprite.center_y=768-(self.nextNode.y*32+16)
        self.nodeSprite.draw()
        self.targetSprite.center_x=self.targetNode.x*32+16
        self.targetSprite.center_y=768-(self.targetNode.y*32+16)
        self.targetSprite.draw()
##    def plan_move(self,level):
##        while(True):
##            validDirections=[]
##            for i in range(4):
##                if level.connections[self.nextNode][i]>0:
##                    validDirections.append(i)
##            tmp=randbelow(len(validDirections))
##            with self.lock:
##                self.nextMove=(validDirections[tmp],level.connections[self.nextNode][validDirections[tmp]])
##                self.target=(level.player.x,level.player.y)
##                self.targetNode=level.tiles[(self.target[0],self.target[1])]
class Terrain:
    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.type=None
    def draw(self):
        self.sprite.center_x=self.x*32+16
        self.sprite.center_y=768-(self.y*32+16)
        #print(self.type)
        self.sprite.draw()
class Space(Terrain):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.type="space"
        self.node="no"
        sprite=arcade.Sprite("graphics/node.png",1)
    def draw(self,sprite):
        sprite.center_x=self.x*32+16
        sprite.center_y=768-(self.y*32+16)
        sprite.draw()
class Wall(Terrain):
    def __init__(self,x,y,gate="no"):
        super().__init__(x,y)
        self.type="wall"
        self.gate="no"
        if gate=="gate":
            self.sprite=arcade.Sprite("graphics/gate.png",1)
            self.gate="yes"
        else: self.sprite=arcade.Sprite("graphics/wall.png",1)
class Dot(Terrain):
    def __init__(self,x,y,size="small"):
        super().__init__(x,y)
        self.size=size
        self.type="dot"
        if size=="big":
            self.sprite=arcade.Sprite("graphics/db.png",1)
        else: self.sprite=arcade.Sprite("graphics/ds.png",1)
class Loop(Space):
    def __init__(self,x,y,direction):
        super().__init__(x,y)
        self.dir=direction
        self.type="loop"
def pacman_move(level,pacman):
    if pacman.move_x==0 and pacman.move_y==0:
        if pacman.next<4:
            if pacman.next==0:
                if level.tiles[(pacman.x+1,pacman.y)].type!="wall":
                    pacman.dir=pacman.next
                else: pacman.dir=pacman.next+4
            elif pacman.next==1:
                if level.tiles[(pacman.x,pacman.y-1)].type!="wall":
                    pacman.dir=pacman.next
                else: pacman.dir=pacman.next+4
            elif pacman.next==2:
                if level.tiles[(pacman.x-1,pacman.y)].type!="wall":
                    pacman.dir=pacman.next
                else: pacman.dir=pacman.next+4
            elif pacman.next==3:
                if level.tiles[(pacman.x,pacman.y+1)].type!="wall":
                    pacman.dir=pacman.next
                else: pacman.dir=pacman.next+4
            pacman.next=4
        else:
            if level.tiles[(pacman.x,pacman.y)].type=="loop" and level.tiles[(pacman.x,pacman.y)].dir=="left":
                pacman.x=level.width-2
            elif level.tiles[(pacman.x,pacman.y)].type=="loop" and level.tiles[(pacman.x,pacman.y)].dir=="right":
                pacman.x=0
            if pacman.dir==0 and level.tiles[(pacman.x+1,pacman.y)].type=="wall":
                pacman.dir+=4
            elif pacman.dir==1 and level.tiles[(pacman.x,pacman.y-1)].type=="wall":
                pacman.dir+=4
            elif pacman.dir==2 and level.tiles[(pacman.x-1,pacman.y)].type=="wall":
                pacman.dir+=4
            elif pacman.dir==3 and level.tiles[(pacman.x,pacman.y+1)].type=="wall":
                pacman.dir+=4
    if pacman.dir==0:
        pacman.move_x+=SPEED
        pacman.spriteNumber+=1
    elif pacman.dir==1:
        pacman.move_y-=SPEED
        pacman.spriteNumber+=1
    elif pacman.dir==2:
        pacman.move_x-=SPEED
        pacman.spriteNumber+=1
    elif pacman.dir==3:
        pacman.move_y+=SPEED
        pacman.spriteNumber+=1
    if pacman.move_x>=16:
        pacman.x+=1
        pacman.move_x-=32
    elif pacman.move_x<-16:
        pacman.x-=1
        pacman.move_x+=32
    elif pacman.move_y>=16:
        pacman.y+=1
        pacman.move_y-=32
    elif pacman.move_y<-16:
        pacman.y-=1
        pacman.move_y+=32
    if pacman.move_x in range(-8,8) and pacman.move_y in range(-8,8) and(pacman.x,pacman.y) in level.dots:
        del level.dots[(pacman.x,pacman.y)]
        level.dotNumber-=1    

        
