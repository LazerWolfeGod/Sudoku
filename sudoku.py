import pygame,math,random,copy,time
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

def checksolveable(grid,pmap=-1):
    if pmap == -1: pmap = possible_map(grid)
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

def strip(grid,count):
    size = len(grid)
    ngrid = copy.deepcopy(grid)
    for a in range(count):
        x = random.randint(0,size-1)
        y = random.randint(0,size-1)
        while ngrid[y][x] == 0:
            x = random.randint(0,size-1)
            y = random.randint(0,size-1)
        ngrid[y][x] = 0
    return ngrid

def makesudoku(size=9,diff=50):
    grid = makegrid(size)
    stripped = 10
    grid = strip(grid,stripped)
    cut = 4
    attempts = 0
    while 1:
        refreshpyui(grid)
        past = copy.deepcopy(grid)
        grid = strip(grid,cut)
        f = solve(copy.deepcopy(grid),singlesolution=False,update=False)
        if len(f) == 1:
            stripped+=cut
            cut = max(int(cut*0.8),1)
            attempts = 0
        elif stripped>diff or attempts>4:
            return past
        else:
            grid = past
            attempts+=1
    

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
    start = time.time()
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

def solve(grid,solutions=-1,singlesolution=True,depth=0,update=True):
    if solutions == -1:
        solutions = []
    if update: refreshpyui(grid)
    grid,found = fill(grid)
    if checksolved(grid):
        solutions.append(grid)
        if update: refreshpyui(grid)
        return solutions
    pmap = possible_map(grid)
    if not checksolveable(grid,pmap):
        return solutions
    else:
        for n in range(1,len(grid)+1):       
            for y,a in enumerate(pmap):
                for x,b in enumerate(a):
                    if grid[y][x] == 0 and n in pmap[y][x]:
                        if update: print(depth,len(solutions),'cords:',x,y,n)
                        grid[y][x] = n
                        if checksolveable(grid):
                            solutions = solve(copy.deepcopy(grid),solutions,singlesolution,depth+1,update)
                        if singlesolution and len(solutions)>0:
                            return solutions
                        grid[y][x] = 0
        return solutions

                
            
            
    
def objectify(grid):
    trueg = grid
    grid = possible_map(grid)
    mini = int(len(grid)**0.5)
    textgrid = []
    for j,y in enumerate(grid):
        textgrid.append([])
        for i,x in enumerate(y):
            st = ''
            for a in x: st+=str(a)
            st = textcolfilter(st)
            backingcol = (16, 163, 127)
            if ((j//mini)*mini+i//mini)%2 == 0: backingcol = (16,193,127) 
            if len(x) == 1 and trueg[j][i]!=0:
                textgrid[-1].append(ui.maketext(0,0,st,60,textcenter=True,backingcol=backingcol))
            else:
                textgrid[-1].append(ui.maketext(0,0,st,15,maxwidth=40,backingcol=backingcol))
    return textgrid

def refreshpyui(grid):
    trueg = grid
    grid = possible_map(grid)
    mini = int(len(grid)**0.5)
    for j,y in enumerate(grid):
        for i,x in enumerate(y):
            st = ''
            for a in x: st+=str(a)
            st = textcolfilter(st)
            prev = [ui.IDs['grid'].data[j][i].text,ui.IDs['grid'].data[j][i].textcenter]
            ui.IDs['grid'].data[j][i].text = st
            if len(x) == 1 and trueg[j][i]!=0:
                ui.IDs['grid'].data[j][i].textcenter = True
                ui.IDs['grid'].data[j][i].textsize = 60
            else:
                ui.IDs['grid'].data[j][i].textcenter = False
                ui.IDs['grid'].data[j][i].textsize = 15
            if prev!=[ui.IDs['grid'].data[j][i].text,ui.IDs['grid'].data[j][i].textcenter]:
                ui.IDs['grid'].data[j][i].refresh(ui)
    gameloop()                
            
            
        

    

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


ui.maketable(40,40,objectify(grid),ID='grid',boxwidth=50,boxheight=50)

data = []
for b in range(10):
    start = time.time()
    sudoku = makesudoku(diff=40)
    print('time:',time.time()-start)
    refreshpyui(sudoku)
    data.append(sudoku)
print('done',data)

##print(solve(grid,singlesolution=False))
##print(makegrid())

while not done:
    gameloop()                                             
pygame.quit() 
