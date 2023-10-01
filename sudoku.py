import pygame,math,random,copy
import PyUI as pyui
pygame.init()
screen = pygame.display.set_mode((600, 600),pygame.RESIZABLE)
pygame.scrap.init()
ui = pyui.UI()
done = False
clock = pygame.time.Clock()

ui.styleload_soundium()

def gameloop():
    pygameeventget = ui.loadtickdata()
    for event in pygameeventget:
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
    screen.fill(pyui.Style.wallpapercol)

     
    ui.rendergui(screen)
    pygame.display.flip()
    clock.tick(60)

def textcolfilter(st):
    out = ''
    dic = {'1':'(255,0,0)','2':'(0,255,0)','3':'(0,0,255)','4':'(255,255,0)','5':'(255,255,255)','6':'(0,100,160)','7':'(0,0,150)','8':'(0,140,0)','9':'(255,0,180)'}
    for a in st:
        out+='{"'+a+'" col='+dic[a]+'}'
    return out



def checkdupe(lis):
    lis = lis[:]
    while 0 in lis:
        lis.remove(0)
    for a in lis:
        if len([b for b in lis if b==a])>1:
            return True
    return False

def inverse(grid):
    return [[grid[b][a] for b in range(len(grid[a]))] for a in range(len(grid))]

def valid(bgrid):
    grid = copy.deepcopy(bgrid)
    for y in grid:
        if checkdupe(y):
            return False
    
    for x in inverse(grid):
        if checkdupe(x):
            return False
    for m in segmentgrid(grid):
        if checkdupe(m):
            return False
    return True

def segmentgrid(grid):
    ngrid = [[] for b in range(len(grid))]
    mini = int(len(grid)**0.5)
    for y,a in enumerate(grid):
        for x,b in enumerate(a):
            pos = (y//mini)*mini+x//mini
##            print(x,y,pos)
            ngrid[pos].append(b)
    
    return ngrid

def checksolved(grid):
    completed = True
    for a in grid:
        for b in a:
            if b == 0:
                completed = False
    return completed

def checksolveable(grid):
    pmap = possible_map(grid)
    mini = int(len(grid)**0.5)
    for y,a in enumerate(pmap):
        for x,b in enumerate(a):
            if len(a) == 0:
                return False
            if grid[y][x] == 0:
                checker = [[],[],[]]
                for c in a:
                    checker[0]+=c
                for c in [pmap[i][x] for i in range(len(pmap))]:
                    checker[1]+=c
                for c in segmentgrid(pmap)[(y//mini)*mini+x//mini]:
                    checker[2]+=c
                for c in checker:
                    for n in range(1,len(grid)):
                        if not (n in c):
                            return False
    return True

def makegrid(size=9):
    items = [a+1 for b in range(size) for a in range(size)]
    grid = [[0 for a in range(size)] for b in range(size)]
    while len(items)>(size**2-17):
        item = items.pop(random.randint(0,len(items)-1))
        x = random.randint(0,size-1)
        y = random.randint(0,size-1)
        if grid[y][x] == 0:
            grid[y][x] = item
            if not valid(grid):
                items.append(item)
                grid[y][x] = 0
                
        else:
            items.append(item)
    solutions = solve(grid)
    return solutions[0]

def possible_map(grid):
    pmap = [[[] for a in range(len(grid[0]))] for b in range(len(grid))]
    for y,a in enumerate(grid):
        for x,b in enumerate(a):
            if grid[y][x] == 0:
                for n in range(1,len(grid)+1):
                    grid[y][x] = n
                    if valid(grid):
                        pmap[y][x].append(n)
                grid[y][x] = 0
            else:
                pmap[y][x].append(grid[y][x])
    return pmap

            
def fill(grid):
    if checksolved(grid):
        return grid,1
    pmap = possible_map(grid)
    ngrid = copy.deepcopy(grid)
    mini = int(len(grid)**0.5)
    edit = []
    for y,a in enumerate(pmap):
        for x,b in enumerate(a):    
            if ngrid[y][x] == 0:
                for p in b:
                    checker = [[],[],[]]
                    for c in a:
                        checker[0]+=c
                    for c in [pmap[i][x] for i in range(len(pmap))]:
                        checker[1]+=c
                    for c in segmentgrid(pmap)[(y//mini)*mini+x//mini]:
                        checker[2]+=c
                    valid = True
                    for c in checker:
                        if len([i for i in c if i==p]) == 1:
                            edit.append([y,x,p])
    if len(edit) == 0:
        return ngrid,0
    for a in edit:
        ngrid[a[0]][a[1]] = a[2]                        
    ngrid,found = fill(ngrid)
    return ngrid,found

def solve(grid,solutions=[],singlesolution=True,depth=0):
    refreshpyui(grid)
    gameloop()
    grid,found = fill(grid)
    if checksolved(grid):
        solutions.append(grid)
        refreshpyui(grid)
        gameloop()
        return solutions
    if not checksolveable(grid):
        return solutions
    else:
        refreshpyui(grid)
        gameloop()
        pmap = possible_map(grid)
        for n in range(1,len(grid)+1):       
            for y,a in enumerate(pmap):
                for x,b in enumerate(a):
                    if grid[y][x] == 0 and n in pmap[y][x]:
                        print(depth,len(solutions),'cords:',x,y,n)
                        grid[y][x] = n
                        solutions = solve(copy.deepcopy(grid),solutions,singlesolution,depth+1)
                        if singlesolution and len(solutions)>0:
                            return solutions
                        grid[y][x] = 0
        return solutions

                
            
            
    
                        

def refreshpyui(grid):
    trueg = grid
    grid = possible_map(grid)
    if 'grid' in ui.IDs:
        ui.IDs['grid'].wipe(ui,True)
    mini = int(len(grid)**0.5)
    textgrid = []
    for j,y in enumerate(grid):
        textgrid.append([])
        for i,x in enumerate(y):
            st = ''
            for a in x: st+=str(a)
            backingcol = (16, 163, 127)
            if ((j//mini)*mini+i//mini)%2 == 0: backingcol = (16,193,127) 
            if len(x) == 1 and trueg[j][i]!=0:
                textgrid[-1].append(ui.maketext(0,0,textcolfilter(st),60,textcenter=True,backingcol=backingcol))
            else:
                textgrid[-1].append(ui.maketext(0,0,textcolfilter(st),15,maxwidth=40,backingcol=backingcol))

    ui.IDs['grid'].data = textgrid
    ui.IDs['grid'].refresh(ui)
                    
                
            
            
        

    

grid =  [[0,0,0,0,0,0,0,0,0],
         [0,0,0,0,0,3,0,8,5],
         [0,0,1,0,2,0,0,0,0],
         [0,0,0,5,0,7,0,0,0],
         [0,0,4,0,0,0,1,0,0],
         [0,9,0,0,0,0,0,0,0],
         [5,0,0,0,0,0,0,7,3],
         [0,0,2,0,1,0,0,0,0],
         [0,0,0,0,4,0,0,0,9]]


##grid = [[0,0,0,2,0,6,5,4,0],
##        [5,9,0,0,0,0,6,0,0],
##        [0,6,2,5,8,0,0,0,0],
##        [6,0,5,0,1,3,7,0,0],
##        [0,1,0,6,4,0,0,9,0],
##        [0,0,0,8,0,0,1,0,0],
##        [0,0,1,0,0,0,0,0,0],
##        [2,4,6,1,7,9,0,0,0],
##        [0,0,9,0,0,0,0,1,7]]


ui.maketable(40,40,grid,ID='grid',boxwidth=50,boxheight=50)


print(makegrid())

while not done:
    gameloop()                                             
pygame.quit() 
