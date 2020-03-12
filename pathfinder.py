from secrets import randbelow
import threading
from variables import *
import time

def find_path(ghost,level):
    ghost.startLock.acquire()
    startIndex=level.nodes.index(ghost.nextNode)
    ghost.startLock.release()
    ghost.endLock.acquire()
    endIndex=level.nodes.index(ghost.targetNode)
    ghost.endLock.release()
    
    pathArray=[] #tablica z drogami, które  będą wykorzystane do krzyżowania
    path=ghost.preferredPath #najlepsza droga z poprzedniej iteracji
    for i in range(4): #tworzy cztery drogi, jedna jest importowana z poprzedniej iteracji
        if path==[]:
            path.append(startIndex)
        path=create_path(level,path,endIndex) #Znajduje drogę do węzła endIndex w sposób pseudolosowy, path=tablica zawierająca początkowy węzeł(lub kilka)
        pathArray.append(path)
        path=[startIndex]
        ghost.pathLock.acquire()
        ghost.pathArray=sorted(pathArray, key= lambda x: countLength(level,x)) #zwraca tablicę dróg posortowaną według długości
        ghost.pathLock.release()
        path=[]
    while True:
        if not ghost.threadLoop:
            break
        if len(pathArray)>1:
            crossover(ghost,level,pathArray)
            ghost.pathLock.acquire()
            ghost.pathArray=sorted(pathArray, key= lambda x: countLength(level,x))
            ghost.pathLock.release()
            time.sleep(0.001)
            

def crossover(ghost,level,pathArray):
    pathOne=pathArray.pop(randbelow(len(pathArray)))
    pathTwo=pathArray[randbelow(len(pathArray))]
    pathArray.append(pathOne)
    crossPoint=(None,None,0)
    for n1 in range(len(pathOne)-1,0,-1):
        if pathOne[n1] in pathTwo:
            n2=pathTwo.index(pathOne[n1])
            potential=abs(n1-n2)
            if potential>crossPoint[2]:
                crossPoint=(n1,n2,potential)
    if crossPoint[0]!=None:
        n1=crossPoint[0]
        n2=crossPoint[1]
        crossedOne=pathOne[:n1]+pathTwo[n2:]
        crossedTwo=pathTwo[:n2]+pathOne[n1:]
        pathArray.append(crossedOne)
        pathArray.append(crossedTwo)
        pathArray.sort(key= lambda x: countLength(level,x))
        pathArray.pop(-1)
        pathArray.pop(-1)

    
def create_path(level,path,endIndex): 
    while True:
        if endIndex in level.connections[path[-1]][1]: #sprawdza czy cel jest za jednym z zakrętów
            path.append(endIndex)
            break
        else: #w przeciwnym razie skręca w losowym dostępnym kierunku, unikając zawracania o 180 stopni
            randomizerArray=[]
            for i in range(4):
                if level.connections[path[-1]][1][i]!=None:
                    if len(path)<2 or level.connections[path[-1]][1][i]!=path[-2]:
                        randomizerArray.append(level.connections[path[-1]][1][i])
            r=randbelow(len(randomizerArray))
            path.append(randomizerArray[r])
            
    return path
        
def set_targets(ghost,level): #ustala cel podróży ducha
    if ghost.color=="red": #w przypadku czerwonego ducha jest to dokładna pozycja gracza
        ghost.target=(level.player.x,level.player.y)
    elif ghost.color=="pink": #...różowy natomiast stara się być parę kroków przed.
        if level.player.dir%4==0:
            ghost.target=(level.player.x+2,level.player.y)
        elif level.player.dir%4==1:
            ghost.target=(level.player.x,level.player.y-2)
        elif level.player.dir%4==2:
            ghost.target=(level.player.x-2,level.player.y)
        elif level.player.dir%4==3:
            ghost.target=(level.player.x,level.player.y+2)
    ghost.endLock.acquire()
    ghost.targetNode=level.closestNode(ghost.target[0],ghost.target[1]) #znajduje węzeł najbliższy podanemu x i y
    ghost.endLock.release()
    
def countLength(level,path): #zlicza sumę odległści między węzłami drogi
    length=0
    for i in range(len(path)-1):
        direction=level.connections[path[i]][1].index(path[i+1])
        length+=level.connections[path[i]][0][direction]
    return length

def getMove(level,start,end,ghost): #zwraca kierunek od start do end i odległość między nimi
    direction=level.connections[start][1].index(end)
    distance=level.connections[start][0][direction]
    return (direction,distance)
        
def ghost_move(level,ghost):
    if ghost.movement>0: #movement=pozostały dystans do przebycia
        ghost.movement-=SPEED
        if ghost.dir==0:
            ghost.move_x+=SPEED
        elif ghost.dir==1:
            ghost.move_y-=SPEED
        elif ghost.dir==2:
            ghost.move_x-=SPEED
        elif ghost.dir==3:
            ghost.move_y+=SPEED
        if ghost.move_x>=16:
            ghost.x+=1
            ghost.move_x-=32
        elif ghost.move_x<-16:
            ghost.x-=1
            ghost.move_x+=32
        elif ghost.move_y>=16:
            ghost.y+=1
            ghost.move_y-=32
        elif ghost.move_y<-16:
            ghost.y-=1
            ghost.move_y+=32
    if ghost.move_x==0 and ghost.move_y==0:
        if level.tiles[(ghost.x,ghost.y)].type=="loop" and level.tiles[(ghost.x,ghost.y)].dir=="left":
            ghost.x=level.width-2
        elif level.tiles[(ghost.x,ghost.y)].type=="loop" and level.tiles[(ghost.x,ghost.y)].dir=="right":
            ghost.x=0
    if ghost.movement==0: #docieramy do kolejnego węzła
        if ghost.pathArray!=[]: #jeżeli w tablicy znajdują się drogi, wybieramy najlepszą (są już posortowane)
            ghost.pathLock.acquire()
            ghost.preferredPath=ghost.pathArray[0]
            ghost.pathLock.release()
            
        if ghost.preferredPath!=[]:
            ghost.pathLock.acquire()
            ghost.preferredPath.pop(0)
            ghost.pathLock.release()
        if ghost.preferredPath!=[]:
            ghost.startLock.acquire()
            ghost.nextNode=level.nodes[ghost.preferredPath[0]]
            ghost.startLock.release()          
        else: #w przeciwnym razie skręcamy losowo
            node=level.nodes.index(level.tiles[(ghost.x,ghost.y)])
            validDestinations=[]
            for i in range(4):
                if level.connections[node][0][i]>0:
                    validDestinations.append(level.connections[node][1][i])
            tmp=randbelow(len(validDestinations))
            ghost.startLock.acquire()
            ghost.nextNode=level.nodes[validDestinations[tmp]]
            ghost.startLock.release()

        start=level.nodes.index(level.tiles[(ghost.x,ghost.y)])
        end=level.nodes.index(ghost.nextNode)
        nextMove=getMove(level,start,end,ghost)

        
        ghost.dir=nextMove[0]
        ghost.movement=nextMove[1]*32
        if ghost.planner.is_alive() is True:
            ghost.threadLoop=False
            ghost.planner.join()
        ghost.planner=threading.Thread(target=find_path,args=(ghost,level))
        ghost.threadLoop=True
        ghost.planner.start() #rozpoczyna wątek realizujący szukanie drogi
        

