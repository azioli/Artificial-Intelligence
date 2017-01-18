size=0
depth=0
cells=[]
from collections import deque
from copy import deepcopy
import sys,time
startTime=time.time()

class gameBoard:
    def __init__(self):
        self.board=[]
        self.empty=[]
        self.player=[]
        self.enemy=[] 
board=gameBoard()

class gameNode:
    def __init__(self):
        self.depth=0
        self.children=[]
        self.isMax=True
        self.op={}
        self.score=0
    def setScore(self):
        global board,size,cells
        self.score=0
        for i in range(size):
            for j in range(size):
                self.score+=cells[i][j]*board.board[i*size+j]
                   
    
           
def doStake(node,child,i,j):
    global size,board
    child.depth=node.depth+1
    if node.isMax:#player stake
        child.isMax=False
        board.board[i*size+j]=1
    else:#enemy stake
        child.isMax=True
        board.board[i*size+j]=-1
    child.op["Stake"]=(i,j)
    node.children.append(child)
    return

def doRaid(node,child,i,j,d):#node.board[i*size+j] is ensured to be 1 or -1
    global size,board
    if d==0:
        ri=i-1
        rj=j
    elif d==1:
        ri=i+1
        rj=j
    elif d==2:
        ri=i
        rj=j-1
    elif d==3:
        ri=i
        rj=j+1 
    else: 
        return 
    if ri<0 or rj<0 or ri>=size or rj>=size:
        return 
    if board.board[ri*size+rj]!=0:#board[ri*size+rj] must be unoccupied
        return 
    if node.isMax:
        if not ((ri-1>=0 and  board.board[(ri-1)*size+rj]==-1) or (rj-1>=0 and  board.board[ri*size+rj-1]==-1) or (ri+1<size and  board.board[(ri+1)*size+rj]==-1) or (rj+1<size and  board.board[ri*size+rj+1]==-1)):
            return 
    else:
        if not ((ri-1>=0 and  board.board[(ri-1)*size+rj]==1) or (rj-1>=0 and  board.board[ri*size+rj-1]==1) or (ri+1<size and  board.board[(ri+1)*size+rj]==1) or (rj+1<size and  board.board[ri*size+rj+1]==1)):
            return 
    child=gameNode()
    child.depth=node.depth+1 
    if node.isMax:#player raid
        child.isMax=False
        board.board[ri*size+rj]=1
        if ri-1>=0 and  board.board[(ri-1)*size+rj]==-1:
            board.board[(ri-1)*size+rj]=1
        if rj-1>=0 and  board.board[ri*size+rj-1]==-1:
            board.board[ri*size+rj-1]=1
        if ri+1<size and  board.board[(ri+1)*size+rj]==-1:
            board.board[(ri+1)*size+rj]=1
        if rj+1<size and  board.board[ri*size+rj+1]==-1:
            board.board[ri*size+rj+1]=1
    else:#enemy raid
        child.isMax=True
        board.board[ri*size+rj]=-1
        if ri-1>=0 and  board.board[(ri-1)*size+rj]==1:
            board.board[(ri-1)*size+rj]=-1
        if rj-1>=0 and  board.board[ri*size+rj-1]==1:
            board.board[ri*size+rj-1]=-1
        if ri+1<size and  board.board[(ri+1)*size+rj]==1:
            board.board[(ri+1)*size+rj]=-1
        if rj+1<size and  board.board[ri*size+rj+1]==1:
            board.board[ri*size+rj+1]=-1   
    child.op["Raid"]=(ri,rj)        
    node.children.append(child)
    #TO-DO:return a set of nodes raided
    return child

def maxvalue(node):
    if not node.children: 
        return node.score
    v=-sys.maxsize
    for child in node.children:
        v=max(v,minvalue(child))
    return v    

def minvalue(node):
    if not node.children: 
        return node.score
    v=sys.maxsize
    for child in node.children:
        v=min(v,maxvalue(child))
    return v  
    
def abmax(node,alpha,beta):
    if not node.children: 
        return node.score
    v=-sys.maxsize
    for child in node.children:
        v=max(v,abmin(child,alpha,beta)) 
        if v>=beta:
            return v
        alpha=max(alpha,v)
    return v
   
def abmin(node,alpha,beta):
    if not node.children: 
        return node.score
    v=sys.maxsize
    for child in node.children:
        v=min(v,abmax(child,alpha,beta))
        if v<=alpha:
            return v
        beta=min(beta,v)
    return v

def revStake(node,i,j):
    global size,board
    board.board[i*size+j]=0

def revRaid(node,i,j,d):
    global size,board
    if d==0:
        ri=i-1
        rj=j
    elif d==1:
        ri=i+1
        rj=j
    elif d==2:
        ri=i
        rj=j-1
    elif d==3:
        ri=i
        rj=j+1 
    else: 
        return
    if node.isMax:
        board.board[ri*size+rj]=0
        if ri-1>=0 and  board.board[(ri-1)*size+rj]==1:
            board.board[(ri-1)*size+rj]=-1
        if rj-1>=0 and  board.board[ri*size+rj-1]==1:
            board.board[ri*size+rj-1]=-1
        if ri+1<size and  board.board[(ri+1)*size+rj]==1:
            board.board[(ri+1)*size+rj]=-1
        if rj+1<size and  board.board[ri*size+rj+1]==1:
            board.board[ri*size+rj+1]=-1
    else:
        board.board[ri*size+rj]=0
        if ri-1>=0 and  board.board[(ri-1)*size+rj]==-1:
            board.board[(ri-1)*size+rj]=1
        if rj-1>=0 and  board.board[ri*size+rj-1]==-1:
            board.board[ri*size+rj-1]=1
        if ri+1<size and  board.board[(ri+1)*size+rj]==-1:
            board.board[(ri+1)*size+rj]=1
        if rj+1<size and  board.board[ri*size+rj+1]==-1:
            board.board[ri*size+rj+1]=1
                        
        
def backTracking(node):
    global size,board,depth
    if node.depth==depth:
        node.setScore()
        return
    stake=[]
    for x in range(size):
        for y in range(size):
            if board.board[x*size+y]==0:
                stake.append((x,y))
    for (x,y) in stake:            
        child=gameNode()
        #print(board.board,"before")
        doStake(node,child,x,y)
        backTracking(child)
        revStake(node, x, y)
        #print(board.board,"after")
    raid=[]
    if node.isMax:    
        for x in range(size):
            for y in range(size):
                if board.board[x*size+y]==1:
                    raid.append((x,y))
        for (x,y) in raid:                                            
            child=None
            for d in range(4):
                tmp=board.board[:]
                child=doRaid(node,child,x,y,d)
                if child is not None:
                    backTracking(child)
                    board.board=tmp[:]
    else:
        for x in range(size):
            for y in range(size):
                if board.board[x*size+y]==-1:
                    raid.append((x,y))
        for (x,y) in raid:                                            
            child=None
            for d in range(4):
                tmp=board.board[:]
                child=doRaid(node,child,x,y,d)
                if child is not None:
                    backTracking(child)
                    board.board=tmp[:]
    return
                                                                                  
if __name__ == '__main__':
    fo=open("input.txt","r+")
    size=int(fo.readline().strip())
    mode=fo.readline().strip()
    youplay=fo.readline().strip()
    depth=int(fo.readline().strip())
    cells=[[0 for x in range(size)] for y in range(size)] 
    for i in range(size):
        line=fo.readline().strip().split(" ")
        for j in range(size):
            cells[i][j]=int(line[j])
    root=gameNode()
    board.board=[0 for x in range(size*size)]        
    for i in range(size):
        line=fo.readline().strip()
        for j in range(size):
            if(line[j]==youplay):
                board.board[i*size+j]=1
            elif(line[j]=="."):
                board.board[i*size+j]=0
            else:
                board.board[i*size+j]=-1
    
    backTracking(root)
                
    maxScore=-sys.maxsize
    op=""
    pos=(0,0)
    chosen=None;
    print(time.time()-startTime) 
    startTime=time.time()
    if mode=="MINIMAX":
        for child in root.children:
            tempScore=minvalue(child)
            if tempScore>maxScore:
                maxScore=tempScore
                op=list(child.op.keys())[0]
                pos=list(child.op.values())[0]
                chosen=child;
    elif mode=="ALPHABETA" or mode=="COMPETITION":       
        for child in root.children:
            tempScore=abmin(child,-sys.maxsize,sys.maxsize)
            if tempScore>maxScore:
                maxScore=tempScore
                op=list(child.op.keys())[0]
                pos=list(child.op.values())[0]
                chosen=child;
    fw=open('output.txt',"w")            
    print(chr(ord('A')+pos[1])+str(pos[0]+1),op)
    print(chr(ord('A')+pos[1])+str(pos[0]+1),op,file=fw)
    '''for i in range(size):
        line=""
        for j in range(size):
            if youplay=="X":
                if i*size+j in chosen.empty:
                    line+="."
                elif i*size+j in chosen.player:
                    line+="X"
                elif i*size+j in chosen.enemy:
                    line+="O" 
            elif youplay=="O":
                if i*size+j in chosen.empty:
                    line+="."
                elif i*size+j in chosen.player:
                    line+="O"
                elif i*size+j in chosen.enemy:
                    line+="X" 
        print(line) 
        print(line,file=fw)'''
          
print(time.time()-startTime)                                