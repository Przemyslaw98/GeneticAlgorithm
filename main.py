import arcade
from level import *
from objects import *
import threading
from pathfinder import *
from variables import *




class Game(arcade.Window):
    def setup(self):
        arcade.set_background_color([0,0,0])
        self.level=Level("level2.txt")
        #planners=[]
        #for ghost in self.level.ghosts:
            #planner=threading.Thread(target=plan_move,args=(self.level,ghost))
            #planners.append(planner)
    def on_draw(self):
        
        arcade.start_render()
        if DRAW_NODES==1:
            for ghost in self.level.ghosts:
                nodes=[]
                for i in ghost.preferredPath:
                    nodes.append(self.level.nodes[i])
                for node in nodes:
                    node.draw(ghost.nodeSprite)
        for tile in self.level.tiles:
            if self.level.tiles[tile].type!="space" and self.level.tiles[tile].type!="loop":
                self.level.tiles[tile].draw()
        for dot in self.level.dots:
            self.level.dots[dot].draw()
        for ghost in self.level.ghosts:
            ghost.draw()
        self.level.player.draw()
    def on_update(self,delta_time):
        self.level.player.draw()
        pacman_move(self.level,self.level.player)
        
        for ghost in self.level.ghosts:
            ghost_move(self.level,ghost)
            set_targets(ghost,self.level)
    def on_key_press(self,symbol,modifiers):
        if symbol==arcade.key.RIGHT:
            if self.level.player.dir==2:
                self.level.player.dir=0
            else: self.level.player.next=0
        elif symbol==arcade.key.UP:
            if self.level.player.dir==3:
                self.level.player.dir=1
            else: self.level.player.next=1
        elif symbol==arcade.key.LEFT:
            if self.level.player.dir==0:
                self.level.player.dir=2
            else: self.level.player.next=2
        elif symbol==arcade.key.DOWN:
            if self.level.player.dir==1:
                self.level.player.dir=3
            else: self.level.player.next=3

def main():
    game=Game(SCREEN_WIDTH,SCREEN_HEIGHT,SCREEN_TITLE)
    game.setup()
    arcade.run()

main()
