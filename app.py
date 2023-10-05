import pygame,math,random,time,copy,os
import PyUI as pyui
import json
pygame.init()
screenw = 1200
screenh = 800
screen = pygame.display.set_mode((screenw,screenh),pygame.RESIZABLE)
pygame.scrap.init()
ui = pyui.UI()
done = False
clock = pygame.time.Clock()
##ui.addinbuiltimage('sudoku',pygame.image.load('sukoku.png'))
ui.escapeback = False

ui.styleload_lightblue()


def textcolfilter(st):
    out = ''
    dic = {'1':'(255,0,0)','2':'(0,255,0)','3':'(0,0,255)','4':'(255,255,0)','5':'(255,255,255)','6':'(0,100,160)','7':'(0,0,150)','8':'(255,100,0)','9':'(205,0,180)'}
    for a in st:
        out+='{"'+a+'" col='+dic[a]+'}'
    return out

class Sudoku:
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
            if Sudoku.checkdupe(y):
                return False
        
        for x in Sudoku.inverse(grid):
            if Sudoku.checkdupe(x):
                return False
        for m in Sudoku.segmentgrid(grid):
            if Sudoku.checkdupe(m):
                return False
        return True

    def segmentgrid(grid):
        ngrid = [[] for b in range(len(grid))]
        mini = int(len(grid)**0.5)
        for y,a in enumerate(grid):
            for x,b in enumerate(a):
                pos = (y//mini)*mini+x//mini
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
        if pmap == -1: pmap = Sudoku.possible_map(grid)
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
                    for c in Sudoku.segmentgrid(pmap)[(y//mini)*mini+x//mini]:
                        checker[2]+=c
                    for c in checker:
                        for n in range(1,len(grid)):
                            if not (n in c):
                                return False
        return True
    def checksolveamount(grid,base):
        bempty = 0
        for a in base:
            for b in a:
                if b == 0:
                    bempty+=1
        gempty = 0
        for a in grid:
            for b in a:
                if b == 0:
                    gempty+=1
        return 100-int(gempty/bempty*100)

    def makegrid(size=9):
        items = [a+1 for b in range(size) for a in range(size)]
        grid = [[0 for a in range(size)] for b in range(size)]
        while len(items)>(size**2-17):
            item = items.pop(random.randint(0,len(items)-1))
            x = random.randint(0,size-1)
            y = random.randint(0,size-1)
            if grid[y][x] == 0:
                grid[y][x] = item
                if not Sudoku.valid(grid):
                    items.append(item)
                    grid[y][x] = 0
                    
            else:
                items.append(item)
        solutions = Sudoku.solve(grid)
        if len(solutions) == 0:
            solutions = [Sudoku.makegrid(size)]
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
        grid = Sudoku.makegrid(size)
        stripped = 10
        grid = Sudoku.strip(grid,stripped)
        cut = 4
        attempts = 0
        while 1:
            past = copy.deepcopy(grid)
            grid = Sudoku.strip(grid,cut)
            f = Sudoku.solve(copy.deepcopy(grid),singlesolution=False,cutafterone=True)
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
                        if Sudoku.valid(grid):
                            pmap[y][x].append(n)
                    grid[y][x] = 0
                else:
                    pmap[y][x].append(grid[y][x])
        return pmap

                
    def fill(grid):
        if Sudoku.checksolved(grid):
            return grid,1
        pmap = Sudoku.possible_map(grid)
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
                        for c in Sudoku.segmentgrid(pmap)[(y//mini)*mini+x//mini]:
                            checker[2]+=c
                        valid = True
                        for c in checker:
                            if len([i for i in c if i==p]) == 1:
                                edit.append([y,x,p])
        if len(edit) == 0:
            return ngrid,0
        for a in edit:
            ngrid[a[0]][a[1]] = a[2]
        ngrid,found = Sudoku.fill(ngrid)
        return ngrid,found
    def clue(grid):
        if Sudoku.checksolved(grid):
            return []
        pmap = Sudoku.possible_map(grid)
        cordmap = [[(x,y) for x in range(len(grid[y]))] for y in range(len(grid))]
        mini = int(len(grid)**0.5)
        edit = []
        for y,a in enumerate(pmap):
            for x,b in enumerate(a):    
                if grid[y][x] == 0:
                    for p in b:
                        checker = [[],[],[]]
                        hlkey = [[],[],[]]
                        for c in range(len(a)):
                            checker[0]+=a[c]
                            hlkey[0].append(cordmap[y][c])
                        for c in [pmap[i][x] for i in range(len(pmap))]:
                            checker[1]+=c
                        for c in [cordmap[i][x] for i in range(len(pmap))]:
                            hlkey[1].append(c)
                        for c in Sudoku.segmentgrid(pmap)[(y//mini)*mini+x//mini]:
                            checker[2]+=c
                        for c in Sudoku.segmentgrid(cordmap)[(y//mini)*mini+x//mini]:
                            hlkey[2].append(c)
                        valid = True
                        for k,c in enumerate(checker):
                            if len([i for i in c if i==p]) == 1:
                                edit.append([y,x,p,k,hlkey[k]])
        if len(edit) == 0:
            return []
        return edit

    def solve(grid,solutions=-1,singlesolution=True,depth=0,cutafterone=False):
        if solutions == -1:
            solutions = []
        grid,found = Sudoku.fill(grid)
        if Sudoku.checksolved(grid):
            solutions.append(grid)
            return solutions
        pmap = Sudoku.possible_map(grid)
        if not Sudoku.checksolveable(grid,pmap):
            return solutions
        else:
            for n in range(1,len(grid)+1):       
                for y,a in enumerate(pmap):
                    for x,b in enumerate(a):
                        if grid[y][x] == 0 and n in pmap[y][x]:
                            grid[y][x] = n
                            if Sudoku.checksolveable(grid):
                                solutions = Sudoku.solve(copy.deepcopy(grid),solutions,singlesolution,depth+1,cutafterone)
                            if (singlesolution and len(solutions)>0) or (cutafterone and len(solutions)>1):
                                return solutions
                            grid[y][x] = 0
            return solutions 

class funcersl:
    def __init__(self,main,level):
        self.func = lambda: main.opensudoku(level)
class funcerus:
    def __init__(self,main,i,j):
        self.func = lambda: main.updatesudoku(i,j)

class Main:
    def __init__(self):

        self.levels = [[[[0, 2, 3, 4, 7, 6, 8, 9, 5], [6, 8, 9, 5, 2, 3, 4, 7, 1], [5, 4, 7, 9, 1, 8, 2, 6, 3], [4, 1, 2, 3, 8, 9, 7, 5, 6], [7, 6, 8, 1, 5, 2, 3, 4, 9], [9, 3, 5, 6, 4, 7, 1, 2, 8], [2, 7, 6, 8, 3, 5, 9, 1, 4], [8, 9, 1, 7, 6, 4, 5, 3, 2], [3, 5, 4, 2, 9, 1, 6, 8, 7]], [[1, 2, 3, 4, 7, 6, 8, 9, 5], [6, 8, 9, 5, 2, 3, 4, 7, 1], [5, 4, 7, 9, 1, 8, 2, 6, 3], [4, 1, 2, 3, 8, 9, 7, 5, 6], [7, 6, 8, 1, 5, 2, 3, 4, 9], [9, 3, 5, 6, 4, 7, 1, 2, 8], [2, 7, 6, 8, 3, 5, 9, 1, 4], [8, 9, 1, 7, 6, 4, 5, 3, 2], [3, 5, 4, 2, 9, 1, 6, 8, 7]]], [[[0, 0, 0, 0, 0, 6, 8, 0, 0], [6, 0, 0, 0, 2, 3, 4, 0, 0], [0, 0, 0, 9, 1, 0, 2, 0, 3], [0, 0, 2, 3, 0, 9, 7, 5, 6], [0, 0, 8, 0, 5, 0, 0, 0, 9], [0, 3, 0, 6, 0, 0, 0, 2, 8], [2, 0, 6, 8, 0, 5, 0, 1, 4], [8, 9, 0, 0, 0, 4, 0, 3, 0], [0, 0, 4, 2, 0, 1, 0, 0, 0]], [[1, 2, 3, 4, 7, 6, 8, 9, 5], [6, 8, 9, 5, 2, 3, 4, 7, 1], [5, 4, 7, 9, 1, 8, 2, 6, 3], [4, 1, 2, 3, 8, 9, 7, 5, 6], [7, 6, 8, 1, 5, 2, 3, 4, 9], [9, 3, 5, 6, 4, 7, 1, 2, 8], [2, 7, 6, 8, 3, 5, 9, 1, 4], [8, 9, 1, 7, 6, 4, 5, 3, 2], [3, 5, 4, 2, 9, 1, 6, 8, 7]]], [[[2, 0, 3, 0, 0, 0, 7, 0, 0], [0, 0, 0, 0, 0, 9, 0, 0, 0], [6, 9, 8, 0, 5, 0, 0, 0, 0], [1, 0, 4, 0, 0, 0, 0, 9, 0], [3, 2, 9, 0, 8, 1, 0, 0, 0], [0, 0, 0, 0, 3, 0, 0, 2, 0], [9, 1, 0, 0, 4, 0, 0, 6, 2], [4, 0, 0, 0, 0, 6, 0, 8, 5], [0, 5, 0, 0, 0, 3, 9, 4, 7]], [[2, 4, 3, 1, 6, 8, 7, 5, 9], [5, 7, 1, 4, 2, 9, 6, 3, 8], [6, 9, 8, 3, 5, 7, 2, 1, 4], [1, 8, 4, 6, 7, 2, 5, 9, 3], [3, 2, 9, 5, 8, 1, 4, 7, 6], [7, 6, 5, 9, 3, 4, 8, 2, 1], [9, 1, 7, 8, 4, 5, 3, 6, 2], [4, 3, 2, 7, 9, 6, 1, 8, 5], [8, 5, 6, 2, 1, 3, 9, 4, 7]]], [[[0, 1, 3, 4, 9, 5, 7, 6, 8], [0, 8, 0, 1, 2, 0, 9, 4, 5], [4, 0, 0, 7, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0, 2, 6], [0, 2, 0, 3, 4, 0, 0, 0, 7], [0, 7, 0, 5, 0, 2, 3, 0, 0], [1, 0, 0, 0, 0, 0, 6, 0, 3], [0, 0, 9, 0, 0, 0, 5, 8, 0], [0, 5, 8, 0, 0, 9, 0, 0, 4]], [[2, 1, 3, 4, 9, 5, 7, 6, 8], [6, 8, 7, 1, 2, 3, 9, 4, 5], [4, 9, 5, 7, 8, 6, 1, 3, 2], [5, 3, 1, 9, 7, 8, 4, 2, 6], [9, 2, 6, 3, 4, 1, 8, 5, 7], [8, 7, 4, 5, 6, 2, 3, 1, 9], [1, 4, 2, 8, 5, 7, 6, 9, 3], [7, 6, 9, 2, 3, 4, 5, 8, 1], [3, 5, 8, 6, 1, 9, 2, 7, 4]]], [[[1, 2, 0, 0, 8, 0, 0, 3, 7], [0, 0, 8, 0, 1, 7, 0, 0, 9], [0, 6, 0, 0, 9, 2, 0, 0, 0], [2, 0, 0, 0, 5, 4, 8, 9, 0], [4, 9, 6, 0, 2, 8, 0, 0, 0], [8, 7, 5, 0, 0, 0, 0, 2, 1], [0, 4, 2, 0, 7, 1, 0, 0, 3], [6, 1, 7, 0, 4, 0, 0, 8, 0], [0, 0, 0, 2, 0, 0, 0, 0, 4]], [[1, 2, 9, 4, 8, 5, 6, 3, 7], [3, 5, 8, 6, 1, 7, 2, 4, 9], [7, 6, 4, 3, 9, 2, 1, 5, 8], [2, 3, 1, 7, 5, 4, 8, 9, 6], [4, 9, 6, 1, 2, 8, 3, 7, 5], [8, 7, 5, 9, 3, 6, 4, 2, 1], [9, 4, 2, 8, 7, 1, 5, 6, 3], [6, 1, 7, 5, 4, 3, 9, 8, 2], [5, 8, 3, 2, 6, 9, 7, 1, 4]]], [[[0, 2, 7, 4, 0, 6, 0, 5, 8], [8, 4, 9, 0, 0, 0, 6, 0, 2], [0, 3, 6, 0, 0, 0, 1, 0, 0], [2, 0, 4, 0, 0, 9, 0, 0, 7], [0, 0, 5, 7, 0, 0, 2, 0, 0], [0, 6, 0, 2, 4, 0, 0, 1, 5], [0, 5, 0, 3, 0, 8, 0, 0, 9], [6, 7, 2, 0, 0, 4, 5, 0, 3], [0, 0, 3, 6, 5, 0, 0, 0, 0]], [[1, 2, 7, 4, 9, 6, 3, 5, 8], [8, 4, 9, 1, 3, 5, 6, 7, 2], [5, 3, 6, 8, 7, 2, 1, 9, 4], [2, 1, 4, 5, 6, 9, 8, 3, 7], [3, 9, 5, 7, 8, 1, 2, 4, 6], [7, 6, 8, 2, 4, 3, 9, 1, 5], [4, 5, 1, 3, 2, 8, 7, 6, 9], [6, 7, 2, 9, 1, 4, 5, 8, 3], [9, 8, 3, 6, 5, 7, 4, 2, 1]]], [[[0, 5, 0, 0, 0, 6, 0, 0, 0], [0, 0, 0, 3, 0, 8, 0, 9, 0], [1, 0, 0, 0, 0, 0, 4, 3, 0], [0, 0, 0, 2, 0, 0, 7, 5, 0], [0, 3, 0, 4, 8, 1, 0, 2, 9], [0, 8, 2, 0, 0, 0, 0, 1, 0], [0, 0, 5, 6, 0, 4, 9, 7, 0], [4, 2, 0, 0, 0, 5, 8, 6, 1], [7, 0, 0, 8, 1, 9, 0, 0, 0]], [[3, 5, 4, 1, 9, 6, 2, 8, 7], [2, 7, 6, 3, 4, 8, 1, 9, 5], [1, 9, 8, 5, 7, 2, 4, 3, 6], [9, 4, 1, 2, 6, 3, 7, 5, 8], [5, 3, 7, 4, 8, 1, 6, 2, 9], [6, 8, 2, 9, 5, 7, 3, 1, 4], [8, 1, 5, 6, 2, 4, 9, 7, 3], [4, 2, 9, 7, 3, 5, 8, 6, 1], [7, 6, 3, 8, 1, 9, 5, 4, 2]]], [[[0, 0, 0, 0, 8, 7, 0, 0, 9], [0, 0, 0, 1, 5, 2, 3, 0, 7], [5, 0, 0, 0, 0, 9, 0, 0, 4], [7, 0, 1, 6, 2, 4, 9, 0, 0], [9, 0, 0, 7, 1, 0, 0, 0, 0], [4, 0, 2, 5, 9, 8, 0, 0, 3], [0, 0, 0, 0, 3, 0, 8, 7, 0], [0, 0, 7, 0, 4, 6, 2, 0, 5], [0, 0, 6, 2, 7, 0, 0, 0, 0]], [[1, 2, 3, 4, 8, 7, 5, 6, 9], [6, 4, 9, 1, 5, 2, 3, 8, 7], [5, 7, 8, 3, 6, 9, 1, 2, 4], [7, 3, 1, 6, 2, 4, 9, 5, 8], [9, 8, 5, 7, 1, 3, 6, 4, 2], [4, 6, 2, 5, 9, 8, 7, 1, 3], [2, 5, 4, 9, 3, 1, 8, 7, 6], [3, 1, 7, 8, 4, 6, 2, 9, 5], [8, 9, 6, 2, 7, 5, 4, 3, 1]]], [[[2, 0, 4, 0, 0, 0, 6, 7, 0], [6, 0, 0, 0, 4, 8, 0, 3, 0], [8, 1, 0, 0, 0, 7, 0, 0, 0], [0, 0, 2, 0, 9, 0, 8, 5, 0], [0, 6, 5, 8, 0, 1, 4, 0, 0], [3, 0, 0, 5, 2, 4, 7, 1, 6], [0, 2, 0, 0, 0, 0, 9, 6, 0], [4, 0, 6, 9, 0, 0, 3, 0, 0], [0, 0, 0, 0, 7, 0, 0, 0, 0]], [[2, 3, 4, 1, 5, 9, 6, 7, 8], [6, 5, 7, 2, 4, 8, 1, 3, 9], [8, 1, 9, 3, 6, 7, 5, 2, 4], [1, 4, 2, 7, 9, 6, 8, 5, 3], [7, 6, 5, 8, 3, 1, 4, 9, 2], [3, 9, 8, 5, 2, 4, 7, 1, 6], [5, 2, 1, 4, 8, 3, 9, 6, 7], [4, 7, 6, 9, 1, 2, 3, 8, 5], [9, 8, 3, 6, 7, 5, 2, 4, 1]]], [[[0, 0, 0, 0, 0, 9, 5, 8, 7], [7, 6, 4, 0, 5, 8, 0, 0, 0], [9, 0, 8, 0, 0, 7, 0, 0, 0], [4, 3, 0, 0, 0, 0, 0, 0, 0], [0, 0, 9, 0, 3, 4, 0, 0, 8], [0, 2, 5, 0, 9, 0, 0, 1, 0], [0, 0, 1, 0, 6, 0, 8, 7, 2], [3, 0, 2, 4, 7, 5, 9, 0, 0], [6, 9, 0, 0, 1, 2, 3, 0, 0]], [[2, 1, 3, 6, 4, 9, 5, 8, 7], [7, 6, 4, 1, 5, 8, 2, 3, 9], [9, 5, 8, 3, 2, 7, 1, 4, 6], [4, 3, 6, 2, 8, 1, 7, 9, 5], [1, 7, 9, 5, 3, 4, 6, 2, 8], [8, 2, 5, 7, 9, 6, 4, 1, 3], [5, 4, 1, 9, 6, 3, 8, 7, 2], [3, 8, 2, 4, 7, 5, 9, 6, 1], [6, 9, 7, 8, 1, 2, 3, 5, 4]]], [[[2, 5, 0, 4, 0, 8, 6, 0, 0], [1, 8, 0, 0, 2, 0, 0, 0, 0], [3, 9, 0, 0, 0, 6, 0, 7, 8], [4, 0, 1, 0, 8, 0, 7, 0, 0], [0, 2, 3, 0, 1, 0, 9, 0, 5], [5, 0, 0, 0, 0, 0, 1, 8, 0], [7, 1, 0, 0, 0, 9, 3, 0, 0], [0, 4, 0, 5, 6, 0, 0, 1, 0], [0, 0, 5, 8, 0, 1, 4, 9, 0]], [[2, 5, 7, 4, 9, 8, 6, 3, 1], [1, 8, 6, 3, 2, 7, 5, 4, 9], [3, 9, 4, 1, 5, 6, 2, 7, 8], [4, 6, 1, 9, 8, 5, 7, 2, 3], [8, 2, 3, 7, 1, 4, 9, 6, 5], [5, 7, 9, 6, 3, 2, 1, 8, 4], [7, 1, 8, 2, 4, 9, 3, 5, 6], [9, 4, 2, 5, 6, 3, 8, 1, 7], [6, 3, 5, 8, 7, 1, 4, 9, 2]]], [[[1, 0, 0, 0, 0, 9, 0, 0, 7], [0, 0, 8, 1, 7, 0, 0, 0, 9], [9, 0, 0, 2, 0, 0, 0, 6, 4], [2, 9, 0, 4, 1, 0, 7, 0, 8], [6, 0, 5, 0, 0, 3, 4, 9, 0], [0, 0, 0, 0, 9, 2, 3, 0, 0], [8, 0, 0, 3, 0, 0, 0, 0, 0], [0, 2, 1, 0, 0, 0, 9, 0, 5], [5, 0, 0, 0, 0, 0, 8, 7, 0]], [[1, 3, 2, 6, 4, 9, 5, 8, 7], [4, 6, 8, 1, 7, 5, 2, 3, 9], [9, 5, 7, 2, 3, 8, 1, 6, 4], [2, 9, 3, 4, 1, 6, 7, 5, 8], [6, 1, 5, 7, 8, 3, 4, 9, 2], [7, 8, 4, 5, 9, 2, 3, 1, 6], [8, 7, 9, 3, 5, 4, 6, 2, 1], [3, 2, 1, 8, 6, 7, 9, 4, 5], [5, 4, 6, 9, 2, 1, 8, 7, 3]]], [[[4, 0, 7, 1, 0, 3, 0, 0, 0], [6, 0, 0, 0, 0, 0, 0, 1, 7], [5, 0, 0, 8, 4, 0, 2, 0, 6], [0, 8, 2, 0, 3, 0, 6, 0, 0], [0, 0, 4, 6, 0, 0, 0, 0, 0], [7, 0, 6, 9, 0, 2, 1, 0, 3], [0, 7, 1, 5, 2, 9, 0, 0, 4], [0, 4, 0, 0, 1, 0, 7, 0, 9], [0, 0, 0, 4, 7, 8, 0, 0, 1]], [[4, 2, 7, 1, 6, 3, 9, 5, 8], [6, 3, 8, 2, 9, 5, 4, 1, 7], [5, 1, 9, 8, 4, 7, 2, 3, 6], [1, 8, 2, 7, 3, 4, 6, 9, 5], [3, 9, 4, 6, 5, 1, 8, 7, 2], [7, 5, 6, 9, 8, 2, 1, 4, 3], [8, 7, 1, 5, 2, 9, 3, 6, 4], [2, 4, 5, 3, 1, 6, 7, 8, 9], [9, 6, 3, 4, 7, 8, 5, 2, 1]]], [[[0, 0, 0, 0, 0, 3, 8, 0, 7], [1, 9, 0, 4, 5, 0, 3, 0, 6], [6, 0, 0, 2, 0, 9, 0, 4, 5], [0, 0, 4, 9, 6, 0, 0, 8, 0], [8, 1, 9, 0, 3, 0, 0, 0, 4], [0, 6, 3, 0, 0, 0, 0, 1, 0], [3, 5, 1, 0, 0, 4, 9, 0, 8], [4, 0, 0, 0, 0, 6, 0, 0, 0], [0, 7, 6, 0, 0, 0, 4, 0, 0]], [[2, 4, 5, 6, 1, 3, 8, 9, 7], [1, 9, 7, 4, 5, 8, 3, 2, 6], [6, 3, 8, 2, 7, 9, 1, 4, 5], [7, 2, 4, 9, 6, 1, 5, 8, 3], [8, 1, 9, 5, 3, 2, 6, 7, 4], [5, 6, 3, 8, 4, 7, 2, 1, 9], [3, 5, 1, 7, 2, 4, 9, 6, 8], [4, 8, 2, 3, 9, 6, 7, 5, 1], [9, 7, 6, 1, 8, 5, 4, 3, 2]]], [[[2, 0, 4, 7, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 5], [0, 0, 5, 0, 1, 0, 0, 0, 4], [4, 0, 0, 9, 0, 0, 6, 2, 7], [8, 2, 6, 3, 7, 0, 0, 0, 0], [0, 5, 9, 4, 0, 0, 3, 1, 8], [5, 4, 0, 1, 0, 9, 0, 0, 3], [0, 9, 0, 5, 2, 0, 8, 4, 1], [0, 8, 0, 0, 4, 7, 0, 9, 2]], [[2, 3, 4, 7, 9, 5, 1, 8, 6], [1, 6, 8, 2, 3, 4, 9, 7, 5], [9, 7, 5, 8, 1, 6, 2, 3, 4], [4, 1, 3, 9, 5, 8, 6, 2, 7], [8, 2, 6, 3, 7, 1, 4, 5, 9], [7, 5, 9, 4, 6, 2, 3, 1, 8], [5, 4, 2, 1, 8, 9, 7, 6, 3], [6, 9, 7, 5, 2, 3, 8, 4, 1], [3, 8, 1, 6, 4, 7, 5, 9, 2]]], [[[2, 0, 1, 8, 0, 0, 0, 7, 0], [0, 0, 0, 0, 7, 0, 6, 1, 0], [0, 0, 6, 1, 0, 0, 5, 0, 0], [7, 0, 2, 3, 0, 0, 4, 6, 0], [1, 0, 0, 7, 0, 4, 0, 3, 0], [8, 4, 3, 0, 0, 2, 1, 0, 0], [6, 0, 4, 5, 0, 7, 0, 0, 3], [0, 0, 0, 4, 1, 8, 0, 5, 6], [0, 0, 7, 0, 6, 3, 0, 4, 0]], [[2, 5, 1, 8, 4, 6, 3, 7, 9], [9, 3, 8, 2, 7, 5, 6, 1, 4], [4, 7, 6, 1, 3, 9, 5, 2, 8], [7, 9, 2, 3, 8, 1, 4, 6, 5], [1, 6, 5, 7, 9, 4, 8, 3, 2], [8, 4, 3, 6, 5, 2, 1, 9, 7], [6, 1, 4, 5, 2, 7, 9, 8, 3], [3, 2, 9, 4, 1, 8, 7, 5, 6], [5, 8, 7, 9, 6, 3, 2, 4, 1]]], [[[3, 0, 2, 0, 8, 7, 0, 9, 0], [6, 0, 4, 0, 0, 1, 0, 0, 5], [0, 0, 8, 0, 9, 0, 6, 0, 3], [5, 0, 0, 0, 7, 0, 0, 0, 0], [8, 4, 6, 3, 0, 9, 0, 0, 1], [0, 1, 0, 5, 0, 4, 2, 3, 8], [0, 8, 0, 9, 4, 6, 0, 1, 0], [7, 3, 1, 0, 0, 0, 0, 6, 0], [0, 0, 9, 0, 0, 0, 5, 0, 2]], [[3, 5, 2, 6, 8, 7, 1, 9, 4], [6, 9, 4, 2, 3, 1, 8, 7, 5], [1, 7, 8, 4, 9, 5, 6, 2, 3], [5, 2, 3, 1, 7, 8, 9, 4, 6], [8, 4, 6, 3, 2, 9, 7, 5, 1], [9, 1, 7, 5, 6, 4, 2, 3, 8], [2, 8, 5, 9, 4, 6, 3, 1, 7], [7, 3, 1, 8, 5, 2, 4, 6, 9], [4, 6, 9, 7, 1, 3, 5, 8, 2]]], [[[1, 0, 0, 0, 9, 0, 3, 7, 8], [8, 0, 0, 1, 0, 3, 0, 0, 0], [0, 0, 6, 0, 4, 8, 9, 0, 2], [0, 0, 0, 4, 0, 0, 6, 3, 0], [0, 0, 3, 0, 6, 0, 7, 0, 0], [5, 6, 7, 3, 0, 0, 1, 2, 0], [0, 3, 8, 0, 7, 0, 0, 4, 1], [0, 0, 2, 0, 1, 0, 8, 6, 3], [6, 1, 5, 0, 0, 4, 0, 0, 7]], [[1, 2, 4, 5, 9, 6, 3, 7, 8], [8, 7, 9, 1, 2, 3, 4, 5, 6], [3, 5, 6, 7, 4, 8, 9, 1, 2], [2, 8, 1, 4, 5, 7, 6, 3, 9], [4, 9, 3, 2, 6, 1, 7, 8, 5], [5, 6, 7, 3, 8, 9, 1, 2, 4], [9, 3, 8, 6, 7, 2, 5, 4, 1], [7, 4, 2, 9, 1, 5, 8, 6, 3], [6, 1, 5, 8, 3, 4, 2, 9, 7]]], [[[2, 0, 0, 3, 0, 8, 9, 1, 0], [6, 1, 8, 0, 0, 0, 3, 7, 0], [0, 9, 4, 0, 0, 7, 0, 0, 0], [0, 0, 0, 0, 0, 0, 8, 6, 0], [5, 8, 0, 2, 1, 6, 4, 0, 0], [0, 0, 6, 0, 0, 0, 1, 0, 0], [1, 0, 7, 0, 9, 0, 0, 0, 0], [8, 0, 0, 6, 0, 0, 5, 0, 2], [0, 6, 0, 4, 3, 0, 7, 8, 1]], [[2, 7, 5, 3, 4, 8, 9, 1, 6], [6, 1, 8, 5, 2, 9, 3, 7, 4], [3, 9, 4, 1, 6, 7, 2, 5, 8], [4, 2, 1, 7, 5, 3, 8, 6, 9], [5, 8, 9, 2, 1, 6, 4, 3, 7], [7, 3, 6, 9, 8, 4, 1, 2, 5], [1, 5, 7, 8, 9, 2, 6, 4, 3], [8, 4, 3, 6, 7, 1, 5, 9, 2], [9, 6, 2, 4, 3, 5, 7, 8, 1]]], [[[6, 4, 1, 0, 3, 8, 9, 7, 0], [0, 2, 0, 5, 0, 9, 0, 6, 4], [0, 5, 9, 0, 0, 0, 0, 3, 0], [0, 0, 4, 0, 0, 6, 0, 0, 7], [0, 6, 0, 0, 8, 0, 0, 0, 2], [0, 0, 0, 3, 0, 0, 6, 5, 0], [4, 0, 0, 0, 0, 5, 7, 0, 0], [5, 0, 0, 0, 0, 0, 4, 9, 1], [8, 9, 0, 7, 0, 0, 0, 0, 0]], [[6, 4, 1, 2, 3, 8, 9, 7, 5], [3, 2, 8, 5, 7, 9, 1, 6, 4], [7, 5, 9, 4, 6, 1, 2, 3, 8], [2, 3, 4, 9, 5, 6, 8, 1, 7], [9, 6, 5, 1, 8, 7, 3, 4, 2], [1, 8, 7, 3, 4, 2, 6, 5, 9], [4, 1, 2, 6, 9, 5, 7, 8, 3], [5, 7, 6, 8, 2, 3, 4, 9, 1], [8, 9, 3, 7, 1, 4, 5, 2, 6]]], [[[0, 0, 4, 3, 0, 0, 7, 0, 0], [0, 0, 6, 2, 0, 7, 0, 0, 0], [0, 0, 7, 9, 0, 1, 2, 0, 4], [2, 0, 1, 7, 3, 0, 9, 8, 5], [0, 7, 0, 0, 0, 2, 3, 0, 6], [6, 0, 0, 0, 5, 0, 1, 7, 2], [0, 0, 3, 8, 0, 4, 0, 0, 1], [0, 0, 2, 0, 7, 0, 0, 5, 3], [9, 6, 0, 5, 0, 3, 4, 0, 0]], [[1, 2, 4, 3, 8, 5, 7, 6, 9], [3, 9, 6, 2, 4, 7, 5, 1, 8], [5, 8, 7, 9, 6, 1, 2, 3, 4], [2, 4, 1, 7, 3, 6, 9, 8, 5], [8, 7, 5, 1, 9, 2, 3, 4, 6], [6, 3, 9, 4, 5, 8, 1, 7, 2], [7, 5, 3, 8, 2, 4, 6, 9, 1], [4, 1, 2, 6, 7, 9, 8, 5, 3], [9, 6, 8, 5, 1, 3, 4, 2, 7]]]]
        self.leveldata = self.loadleveldata()
        self.level = -1

        
        self.makegui()
    def makegui(self):
        # main menu
        ui.styleset(text_textcol = (40,40,60))
        ui.maketext(0,0,'Sudoku {logo}',100,anchor=('w/2','h/4'),center=True)
        ui.makebutton(0,0,'Sudoku',55,lambda: ui.movemenu('sudoku select','left'),anchor=('w/2','h/2'),center=True)

        ui.maketext(0,40,'Sudoku Level Select',60,'sudoku select',anchor=('w/2',0),center=True,backingdraw=True,layer=3,horizontalspacing=300,verticalspacing=20)

        # level select menu
        data = []
        for i,a in enumerate(self.levels):
            func = funcersl(self,i)
            playbutton = ui.makebutton(0,0,'Play',30,verticalspacing=6,command=func.func)
##            progress = ui.makeslider(0,0,200,32,containedslider=True,button=ui.makebutton(0,0,'',backingdraw=False,borderdraw=False,dragable=False,width=0,height=0),dragable=False,startp=random.randint(0,100),ID=f'progslider{i}',bounditems=[ui.maketext( ])
            progress = ui.maketext(0,0,'-%',30,ID=f'progslider{i}',textcenter=True)
            data.append([i+1,progress,playbutton])
        
        ui.maketable(0,100,data,['Level',''],'sudoku select',anchor=('w/2',0),objanchor=('w/2',0),boxwidth=[150,200,120],ID='sudokuleveltable')
        self.refreshleveltable()

        ui.makescroller(0,100,500,scrollbind=['sudokuleveltable'],anchor=('w',0),objanchor=('w',0),menu='sudoku select',maxp=500,pageheight=300)



        # sudoku grid
        ui.maketable(0,0,[],boxwidth=50,boxheight=50,scalesize=True,scaleby='vertical',anchor=('w/2','h/2'),center=True,menu='sudoku level',ID='sudoku grid')
        ui.maketext(0,-300,'Level: -',80,'sudoku level','sudoku level display',anchor=('w/2','h/2'),center=True,scaleby='vertical')
        ui.maketext(0,300,'-%',80,'sudoku level','sudoku progress display',anchor=('w/2','h/2'),center=True,scaleby='vertical',backingdraw=True)

        # clear button/pop up
        ui.makewindowedmenu(0,40,250,150,'clear confirm','sudoku level',anchor=('w/2',0),objanchor=('w/2',0))
        ui.makebutton(-180,300,'Clear Grid',35,lambda: ui.movemenu('clear confirm','down'),'sudoku level',anchor=('w/2','h/2'),center=True,scaleby='vertical',verticalspacing=8,horizontalspacing=8,maxwidth=100)
        ui.maketext(0,40,'Are You Sure?',40,'clear confirm',center=True,anchor=('w/2',0),backingcol=(47, 86, 179))
        ui.makebutton(-50,0,'No',40,ui.menuback,'clear confirm',anchor=('w/2','h/3*2'),center=True)
        ui.makebutton(50,0,'Yes',40,self.cleargrid,'clear confirm',anchor=('w/2','h/3*2'),center=True)

        # clue button/pop up
        ui.makebutton(180,300,'Get Clue',35,lambda: ui.movemenu('clues','down'),'sudoku level',anchor=('w/2','h/2'),center=True,scaleby='vertical',verticalspacing=8,horizontalspacing=8,maxwidth=100)
        ui.makewindowedmenu(0,40,250,140,'clues','sudoku level',anchor=('w/2',0),objanchor=('w/2',0))
        ui.maketext(15,15,'Show Wrong',32,'clues',maxwidth=110,backingcol=(47, 86, 179))
        ui.makebutton(105,25,'One',35,lambda: self.findwrong(1),'clues')
        ui.makebutton(180,25,'All',35,lambda: self.findwrong(1000),'clues')

        ui.maketext(20,75,'Get Clue',32,'clues',maxwidth=80,backingcol=(47, 86, 179))
        ui.makebutton(85,80,'Easy',35,lambda: self.findclue(True),'clues')
        ui.makebutton(165,80,'Hard',35,lambda: self.findclue(False),'clues')

    def makesudokutableinput(self,grid):
        trueg = grid
        grid = Sudoku.possible_map(grid)
        mini = int(len(grid)**0.5)
        textgrid = []
        for j,y in enumerate(grid):
            textgrid.append([])
            for i,x in enumerate(y):
                st = ''
                for a in x: st+=str(a)
                st = textcolfilter(st)
                backingcol = pyui.Style.defaults['col']
                if ((j//mini)*mini+i//mini)%2 == 0: backingcol = [backingcol[0],backingcol[1]+20,backingcol[2]]
                if len(x) == 1 and trueg[j][i]!=0:
                    textgrid[-1].append(ui.maketext(0,0,st,60,textcenter=True,backingcol=backingcol))
                else:
                    func = funcerus(self,i,j)
                    textgrid[-1].append(ui.maketextbox(0,0,command=func.func,textsize=60,chrlimit=1,backingcol=pyui.shiftcolor(backingcol,-8),col=backingcol,linelimit=1,textcenter=True,numsonly=True,imgdisplay=True,textcol=(43,43,43),commandifkey=True,bounditems=[ui.maketextbox(3,3,textsize=15,numsonly=True,lines=1,width=44,height=15,border=0,spacing=2,col=backingcol,backingdraw=False,borderdraw=False,selectbordersize=0,scalesize=True,scaleby='vertical')]))
        return textgrid

    def updatesudoku(self,x,y,updateall=True):
        box = ui.IDs['sudoku grid'].tableimages[y][x][1]
        box.chrlimit = 1
        box.text = box.text.replace('0','')
        if '"' in box.text:
            chrs = '123456789'
            if box.text[0] in chrs:
                box.text = box.text[0]
            elif box.text[-1] in chrs:
                box.text = box.text[-1]
        if len(box.text) == 0:
            box.bounditems[0].enabled = True
        else:
            box.bounditems[0].enabled = False
            if len(box.text) == 1:
                box.text = textcolfilter(box.text)
                box.typingcursor = -1
                box.chrlimit = len(box.text)
            else:
                box.text = ''
                box.bounditems[0].enabled = True
        if pyui.RECT in [type(a) for a in box.bounditems]:
            ui.delete(box.bounditems[[type(a) for a in box.bounditems].index(pyui.RECT)].ID)
        if updateall:
            self.updategrid()
    def updategrid(self):
        grid = []
        for y in ui.IDs['sudoku grid'].tableimages:
            grid.append([])
            for x in y:
                if x[1].text == '':
                    grid[-1].append(0)
                else:
                    grid[-1].append(int(x[1].text[2]))
        self.grid = grid
        self.leveldata[self.level][1] = grid
        if Sudoku.valid(grid) and Sudoku.checksolved(grid):
            self.solved()
        else:
            self.leveldata[self.level][0] = Sudoku.checksolveamount(grid,self.levels[self.level][0])
            ui.IDs['sudoku progress display'].text = f'{self.leveldata[self.level][0]}%'
            ui.IDs['sudoku progress display'].refresh(ui)
        self.refreshleveltable()

    def solved(self):
        self.leveldata[self.level][0] = 'Solved!'
        ui.IDs['sudoku progress display'].text = f'{self.leveldata[self.level][0]}'
        ui.IDs['sudoku progress display'].refresh(ui)
                    
    def refreshleveltable(self):
        fade = pyui.genfade([(255,0,0),(0,235,0)],101)
        table = ui.IDs['sudokuleveltable']
        for a in table.bounditems:
            if 'progslider' in a.ID:
                a.prog = self.leveldata[int(a.ID.removeprefix('progslider'))][0]
                if a.prog == 'Solved!':
                    a.text = a.prog
                    a.col = fade[-1]
                else:
                    a.prog = int(a.prog)
                    a.text = f'{a.prog}%'
                    a.col = fade[a.prog]
                a.refresh(ui)
        
    def opensudoku(self,level):
        self.level = level
        ui.movemenu('sudoku level','left')
        grid = ui.IDs['sudoku grid']
        grid.wipe(ui)
        grid.data = self.makesudokutableinput(self.levels[level][0])
        grid.boxwidth = 50
        grid.boxheight = 50
        grid.refresh(ui)
        ui.IDs['sudoku level display'].text = f'Level: {level+1}'
        ui.IDs['sudoku level display'].refresh(ui)
        ui.IDs['sudoku progress display'].text = f'{self.leveldata[level][0]}%'
        ui.IDs['sudoku progress display'].refresh(ui)
        for y,a in enumerate(grid.tableimages):
            for x,b in enumerate(a):
                if type(b[1]) == pyui.TEXTBOX:
                    if self.leveldata[level][1][y][x] != 0:
                        b[1].text = str(self.leveldata[level][1][y][x])
                        self.updatesudoku(x,y,False)
                        b[1].refresh(ui)
        self.updategrid()

    def cleargrid(self):
        grid = ui.IDs['sudoku grid']
        for y,a in enumerate(grid.tableimages):
            for x,b in enumerate(a):
                if type(b[1]) == pyui.TEXTBOX:
                    if self.leveldata[self.level][1][y][x] != 0:
                        b[1].text = '0'
                        self.updatesudoku(x,y,False)
                        b[1].refresh(ui)
        self.updategrid()

    def findclue(self,disptext):
        clues = Sudoku.clue(self.grid)
        if clues == []:
            txt = 'No Clues Found'
        else:
            clue = random.choice(clues)
            key = ['row','column','box']
            txt = f'A {clue[2]} can go in this {key[clue[3]]}'
            if clue[2] == 8:
                txt = txt.replace('A','An',1)
            for a in clue[4]:
                self.highlight(a[0],a[1],(20,220,10,70),5)
        if disptext:       
            self.makepopup(txt)
            
    def findwrong(self,limit):
        wrong = []
        for y,a in enumerate(self.grid):
            for x,b in enumerate(a):
                if b != 0 and b!=self.levels[self.level][1][y][x]:
                    wrong.append([x,y])
        random.shuffle(wrong)
        count = 0
        loops = 0
        while count<min(limit,len(wrong)):
            if self.highlight(wrong[count][0],wrong[count][1]):
                count+=1
            loops+=1
            if loops>60: break
        if count == 0:
            self.makepopup('No incorrect Values')
        ui.menuback()
            
    def makepopup(self,txt):
        ui.delete('sudoku pop up',False)
        ui.maketext(0,10,txt,45,'sudoku level',backingdraw=True,killtime=5,ID='sudoku pop up',anchor=('w/2',0),objanchor=('w/2',0))
    def highlight(self,x,y,glowcol=(240,40,40,90),killtime=30):
        obj = ui.IDs['sudoku grid'].tableimages[y][x][1]
        if not (pyui.RECT in [type(a) for a in obj.bounditems]):
            obj.binditem(ui.makerect(0,0,50,50,backingdraw=False,glow=2,glowcol=glowcol,killtime=killtime,scaleby='vertical'))
            obj.resetcords(ui)
            return True
        return False

    def loadleveldata(self):
        if not os.path.isfile(pyui.resourcepath('data.json')):
            data = {}
            for i,a in enumerate(self.levels):
                data[i] = [0,a[0],False]
            with open('data.json','w') as f:
                json.dump(data,f)
        with open('data.json','r') as f:
            out = json.load(f)
        data = {}
        for a in list(out):
            data[int(a)] = out[a]
        return data
    def storeleveldata(self):
        with open('data.json','w') as f:
            json.dump(self.leveldata,f)

main = Main()

while not done:
    pygameeventget = ui.loadtickdata()
    for event in pygameeventget:
        if event.type == pygame.QUIT:
            main.storeleveldata()
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if ui.activemenu == 'sudoku level':
                    main.storeleveldata()
                ui.menuback()
    screen.fill(pyui.Style.wallpapercol)
    
    ui.rendergui(screen)
    pygame.display.flip()
    clock.tick(60)                                               
pygame.quit()





















