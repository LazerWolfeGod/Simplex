import pygame,math,random,sys,os,copy,json
import PyUI as pyui
pygame.init()
screenw = 1200
screenh = 900
screen = pygame.display.set_mode((screenw, screenh),pygame.RESIZABLE)
ui = pyui.UI()
done = False
clock = pygame.time.Clock()
ui.styleload_brown()

def maketableau(strs,primary='P',maximise=True):
    constants='abcdefghijklmnopqrstuvwyxzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    slack='rstupq'
    slackindex = 0
    var = []
    tableau = []
    equations = []
    for s in strs:
        ns = s.replace('+',' ').replace('-',' -')#.replace('=',' = ').replace('<',' < ').replace('>',' > ')
        if '<' in ns:
            ns = ns.replace('<',' '+slack[slackindex]+'=')
            slackindex+=1
        for ch in ns:
            try:
                if not ch in ' =-<>'+primary:
                    int(ch)
            except:
                if not ch in var:
                    var.append(ch)
        if primary in ns: main = ns
        else: equations.append(ns)
    equations.append(main)
    var.append('Value')
    tableau.append(var)
    for eq in equations:
        sep = eq.split('=')
        items = [[i[:-1],i[-1]] for i in sep[0].split()]+[[('-'+i[:-1]).replace('--','+'),i[-1]] for i in sep[1].split()]
        row = [0 for a in range(len(var))]
        for i in items:
            if i[1] != primary:
                if not i[1] in var:
                    row[-1] = -int(i[0]+i[1])
                else:
                    if i[0] == '': const = 1
                    elif i[0] == '-': const = -1
                    else: const = int(i[0])
                    row[var.index(i[1])] = const
        tableau.append(row)
    
    return tableau
        
def simplex(tableau):
    print('Iteration')
    ui.IDs['main table'].row_append([ui.maketable(0,0,[[int(x) if x%1==0 else round(float(x),2) for x in y] for y in tableau[1:]],
                                                  tableau[0],boxwidth=[60 if a<len(tableau[0])-1 else 80 for a in range(len(tableau[0]))])])
    tableau = copy.deepcopy(tableau)
    vals = tableau.pop(0)
    pivot_column = tableau[-1].index(min(tableau[-1]))
    if tableau[-1][pivot_column]<0:
        theta = []
        for r in range(len(tableau)-1):
            if tableau[r][pivot_column] == 0 or tableau[r][-1]/tableau[r][pivot_column]<0:
                theta.append(float('inf'))
            else: theta.append(tableau[r][-1]/tableau[r][pivot_column])
        pivot_row = theta.index(min(theta))
        rowoper = []
        for y in range(len(tableau)):
            if y != pivot_row:
                rowoper.append((tableau[y],-tableau[y][pivot_column]/tableau[pivot_row][pivot_column],tableau[pivot_row]))
            else:
                rowoper.append(([0 for a in range(len(tableau[y]))],1/tableau[y][pivot_column],tableau[y]))
        ntable = []
        for r in rowoper:
            ntable.append([r[0][i]+r[1]*r[2][i] for i in range(len(r[0]))])

        return simplex([vals]+ntable)        

    output = {}
    for col in range(len(tableau[0])-1):
        one = -1
        for y in range(len(tableau)):
            if tableau[y][col] in [0,1]:
                if tableau[y][col] == 1 and one!=-1:
                    output[vals[col]] = 0
                    break
                elif tableau[y][col] == 1:
                    one = y
            else:
                output[vals[col]] = 0
                break
        if not vals[col] in output:
            output[vals[col]] = tableau[one][-1]

    st = ''
    st2 = ''
    stimportant = ''
    for a in output:
        if str(output[a])[-2:] == '.0': output[a] = int(output[a])
        if output[a]!=0:
            st+=f'{a}={round(output[a],3)}, '
            if 'p' in a:
                stimportant+=f'{a}={round(output[a],3)}, '
        else: st2+=f'{a}={round(output[a],3)}, '
    st2.removesuffix(', ')
    print('Players =',stimportant)
    print('Values = '+st+'\nZeros = '+st2+f'\nProfit = {round(tableau[-1][-1],3)}')
    ui.IDs['main table'].row_append([ui.maketext(0,0,st+'\n'+st2+f'\nProfit={round(tableau[-1][-1],3)}',maxwidth=ui.screenw-40)])
    
    return tableau 

def playertableau():
    with open('dummydata.json','r') as f:
        players = json.load(f)[:8]
    budget = 2000
    table = []
    # Main equations
    table.append([a['cost'] for a in players]+[budget])
    for a in range(len(players)):
        table.append([0 for b in range(len(players))]+[1])
        table[-1][a] = 1
    
    # Add slack
    slacknum = len(table)
    for b in range(len(table)):
        for s in range(slacknum):
            if s!=b: table[b].insert(-1,0)
            else: table[b].insert(-1,1)
            
    # Player limit to 15
    table.append([1 for a in range(len(players))]+[0 for a in range(slacknum)]+[15])
    
    # Profit function
    table.append([-a['composite'] for a in players]+[0])
    while len(table[-1])<len(table[0]):
        table[-1].insert(-1,0)
    table.insert(0,['p'+str(b) for b in range(len(players))]+['s'+str(a) for a in range(slacknum)]+['Values'])

    return table


    

ui.makescrollertable(20,20,[],ID='main table',pageheight='h-20',scalesize=False)

##tableau = maketableau(['P=10x+12y+8z','2x+2y<5','5x+3y+4z<15'])
##print(tableau)
tableau = playertableau()#maketableau(['P=3x+4y-5z','2x-3y+2z<4','x+2y+4z<8','y-z<6'])
simplex(tableau)

    

while not done:
    for event in ui.loadtickdata():
        if event.type == pygame.QUIT:
            done = True
    screen.fill(pyui.Style.wallpapercol)
    
    ui.rendergui(screen)
    pygame.display.flip()
    clock.tick(60)                                               
pygame.quit() 
