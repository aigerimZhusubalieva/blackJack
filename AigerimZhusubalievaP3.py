'''Aigerim Zhusubalieva, az2177
Assignment 3 - Reinforcement Learning
Artificial Intelligence, Fall 2022'''

import random

#randomly pick an event given the probability distribution
def chooseFromDist(p):
    pvalues = list(range(1, len(p)+1))
    r = random.choices(pvalues, p)
    return(r[0])

#simulate rolling N dice with N sides with equal probabilities
def rollDice(Ndice, Nsides):
    total = 0
    for i in range(Ndice):
        a = random.randint(1, Nsides)
        total += a
    return total

#pick the number of dice based on the current scores x,y and the learned knowledge
def chooseDice(losecount, wincount, Ndice, M, x, y):
    f = [None] * Ndice #array storing probability of winning given past winning/losing
    b = 0 #the value of J (number of rice to roll) with highest porb of winning
    g = 0 #sum over j excluding b
    T = 0 #total games that have gone through state x,y
    
    for j in range(Ndice):
        if(wincount[x][y][j]+losecount[x][y][j]==0):
            f[j] = 0.5
        else:
            f[j] = wincount[x][y][j]/(wincount[x][y][j]+losecount[x][y][j])
        g += f[j]
        if f[j] >= f[b]: 
            g -= f[j]
            if(b!=0):
                g += f[b]
            b = j
        T = wincount[x][y][j]+losecount[x][y][j]
    
    p = [None] * Ndice #array storing the probability distribution of rolling b or j dice
    p[b] = (T*f[b] + M)/(T*f[b]+Ndice*M) #calculate prob of b dice first
    
    for j in range(Ndice):
        if(j == b):
            continue
        else:
            p[j] = (1-p[b])*(T*f[j]+M)/(g*T+(Ndice-1)*M)
    
    return(chooseFromDist(p)) #choose how many die to roll give the probability distribution
    
#simulate playing one game
def playGame(Ndice, Nsides, Ltarget, Utarget, losecount, wincount, M):
    #progress of x and y
    x = 0
    y = 0
    #take turns
    turn = 1
    #store results of each step in the form [dice rolled, the result of that instance, total score]
    xResults = [[0, 0, 0]]
    yResults = [[0, 0, 0]]
    #keep playing before target is reached by either x or y
    while(xResults[x][2]<Ltarget and yResults[y][2]<Ltarget):
        if(turn):
            turn -=1
            x+=1
            row = []
            #pick how many dice to roll
            row.append(chooseDice(losecount, wincount, Ndice, M, xResults[x-1][2], yResults[y][2]))
            #roll them
            row.append(rollDice(row[0], Nsides))
            #update the total rscore
            row.append(xResults[x-1][2] + row[1])
            xResults.append(row)
        else:
            turn +=1
            y += 1
            row = []
            #pick how many dice to roll
            row.append(chooseDice(losecount, wincount, Ndice, M, x, y))
            #roll them
            row.append(rollDice(row[0], Nsides))
            #update the total rscore
            row.append(yResults[y-1][2] + row[1])
            yResults.append(row)
    
    if(Ltarget<=xResults[x][2]<=Utarget):
        # X wins

        #map xResults to wincount indices
        xlen = len(xResults)
        xlen = 2*xlen-3

        #update the values of losecount and wincount accordingly
        for i in range(xlen):
            if i%2==0:
                wincount[xResults[i//2][2]][yResults[i//2][2]][xResults[i//2+1][0]] += 1
            else:
                losecount[xResults[i//2+1][2]][yResults[i//2][2]][yResults[i//2+1][0]] += 1
    elif(Ltarget<=yResults[y][2]<=Utarget):
        # Y wins

        #map yResults to wincount indices
        ylen = len(yResults)
        ylen = 2*ylen-2

        #update the values of losecount and wincount accordingly
        for i in range(ylen):
            if i%2 == 0:
                losecount[xResults[i//2][2]][yResults[i//2][2]][xResults[i//2+1][0]] += 1
            else:
                wincount[xResults[i//2+1][2]][yResults[i//2][2]][yResults[i//2+1][0]] += 1
    elif(xResults[x][2]>Utarget):
        # X loses

        #map xResults to wincount indices
        xlen = len(xResults)
        xlen = 2*xlen-3

        #update the values of losecount and wincount accordingly
        for i in range(xlen):
            if i%2==0:
                losecount[xResults[i//2][2]][yResults[i//2][2]][xResults[i//2+1][0]] += 1
            else:
                wincount[xResults[i//2+1][2]][yResults[i//2][2]][yResults[i//2+1][0]] += 1
    elif(yResults[y][2]>Utarget):
        # Y loses

        #map yResults to wincount indices
        ylen = len(yResults)
        ylen = 2*ylen-2

        #update the values of losecount and wincount accordingly
        for i in range(ylen):
            if i%2 == 0:
                wincount[xResults[i//2][2]][yResults[i//2][2]][xResults[i//2+1][0]] += 1
            else:
                losecount[xResults[i//2+1][2]][yResults[i//2][2]][yResults[i//2+1][0]] += 1
    
    return(losecount, wincount)

#extract answers from matrices wincount and losecount
def extractAnswer(wincount, losecount):
    #store the best choice for each x,y state and the probability of winning for the best choice
    bestchoice = [[0 for j in range(Ltarget)] for i in range(Ltarget)]
    probbest = [[0 for j in range(Ltarget)] for i in range(Ltarget)]

    for x in range(len(wincount)):
        for y in range(len(wincount[x])):
            # find the best value of j and its probability probb
            bestj = 0
            probb = 0

            for j in range(len(wincount[x][y])):
                #check for denominator
                if((wincount[x][y][j]+losecount[x][y][j])!=0):
                    probj = wincount[x][y][j]/(wincount[x][y][j]+losecount[x][y][j])
                else: 
                    probj = 0
                if((wincount[x][y][bestj]+losecount[x][y][bestj])!=0):
                    probb = wincount[x][y][bestj]/(wincount[x][y][bestj]+losecount[x][y][bestj])
                if(probj>probb):
                    bestj = j
            #update the best choice and its probability of winning after running through all j for each x,y
            bestchoice[x][y] = bestj
            probbest[x][y] = probb
    
    #print the results
    print("\nPlay\n")
    for x in range(len(bestchoice)):
        for y in range(len(bestchoice[x])):
            print(bestchoice[y][x], end=' ')
        print('')
    
    print("\nProb\n")
    for x in range(len(probbest)):
        for y in range(len(probbest[x])):
            print("%.3f" % probbest[y][x], end=' ')
        print('')

#"main" function
def prog3(Ndice, Ltarget, Utarget, NGames, M):
    wincount = [[[0 for k in range(Ndice+1)] for j in range(Ltarget)] for i in range(Ltarget)]
    losecount = [[[0 for k in range(Ndice+1)] for j in range(Ltarget)] for i in range(Ltarget)]

    #play the game Ngames times
    for i in range(NGames):
        losecount, wincount = playGame(Ndice, Nsides, Ltarget, Utarget, losecount, wincount, M)
    
    extractAnswer(losecount, wincount)

#get the input and start the program
Ndice, Nsides, Ltarget, Utarget, M, NGames = input("Enter NDICE NSIDES LTARGET UTARGET M NGAMES Parameters: \n").split()
Nsides = int(Nsides)
Ltarget = int(Ltarget)
Utarget = int(Utarget)
Ndice = int(Ndice)
M = float(M)
NGames = int(NGames)
prog3(Ndice, Ltarget, Utarget, NGames, M)







