#the intial framework for a real-valued GA
#author: Charles Nicholson
#for ISE/DSA 5113

#need some python libraries
import copy
import math
from random import Random
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

savePath = 'c:/users/mjbea/OneDrive/ISE5113/Homework/Homework 5/'       #save path for files created

#to setup a random number generator, we will specify a "seed" value
seed = 5113
myPRNG = Random(seed)

lowerBound = -500  #bounds for Schwefel Function search space
upperBound = 500   #bounds for Schwefel Function search space

#you may change anything below this line that you wish to -----------------------------------------------------------------

#Student name(s):   Matthew J. Beattie
#Date:              May 4, 2017


def initializeGA():
    #set dimensions for Schwefel Function search space (should either be 2 or 200 for HM #5)
    global dimensions
    dimensions = int(input("Enter number of dimensions: ")) 
    
    #set size of GA population
    global populationSize
    populationSize = int(input("Enter population size: "))
    
    #set maximum number of Generations
    global Generations
    Generations = int(input("Enter maximum number of generations: "))
    
    #set cross over rate between chromosomes
    global crossOverRate
    crossOverRate = float(input("Enter cross over rate (0.0 - 1.0): "))
    
    #set mutation rate in chromosomes
    global mutationRate
    mutationRate = float(input("Enter mutation rate (0.0 - 1.0): "))
    
    #set tournament size for competition among chromosomes
    global tournamentSize
    tournamentSize = int(input("Enter tournament size (<" + str(populationSize) + "): "))
    
    #set stopping variance
    global stoppingVariance
    stoppingVariance = np.float64(input("Enter stopping variance (>0.0): "))
    
    #set printing criteria
    global outputInterval
    outputInterval = int(input("Enter output interval: "))
    global printToFile
    printToFile = str(input("Print to file? (y/n): "))
    
    #set plotting criteria
    global turnOnPlotter
    turnOnPlotter = str(input("Turn on plotter? (y/n): "))
    if turnOnPlotter == 'y':
        global plotterInterval
        plotterInterval = int(input("Enter plotter interval: "))
    return



#create an continuous valued chromosome 
def createChromosome(d, lBnd, uBnd):   
    x = []
    for i in range(d):
        x.append(myPRNG.uniform(lBnd,uBnd))     #creating a randomly located solution
        
    return x

#create initial population
def initializePopulation():                     #n is size of population; d is dimensions of chromosome
    population = []
    populationFitness = []
    
    for i in range(populationSize):
        population.append(createChromosome(dimensions,lowerBound, upperBound))
        populationFitness.append(evaluate(population[i]))
        
    tempZip = zip(population, populationFitness)
    popVals = sorted(tempZip, key=lambda tempZip: tempZip[1])
    
    #the return object is a sorted list of tuples: 
    #the first element of the tuple is the chromosome; the second element is the fitness value
    #for example:  popVals[0] is represents the best individual in the population
    #popVals[0] for a 2D problem might be  ([-70.2, 426.1], 483.3)  -- chromosome is the list [-70.2, 426.1] and the fitness is 483.3
    
    return popVals  


#plotting function for 2D population
def plotPopulation(population, title):
    if (len(population[0][0]) > 2):
        print("BYPASS PLOTTING:  Dimension larger than 2")
        return
    else:
        x = [Population[i][0][0] for i in range(populationSize)]
        y = [Population[i][0][1] for i in range(populationSize)]
        z = [Population[i][1] for i in range(populationSize)]
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(x,y,z, c='r', marker='o')
        ax.set_title(title)
        ax.set_xlabel("x-value")
        ax.set_ylabel("y-value")
        ax.set_zlabel("z-value")
        outputPlot = savePath + 'plotfile' + title + '.png'
        fig.savefig(outputPlot)
        plt.close(fig)
        return

#implement a linear crossover
def crossover(x1,x2):
    
    d = len(x1) #dimensions of solution
    
    #choose crossover point 
    
    #we will choose the smaller of the two [0:crossOverPt] and [crossOverPt:d] to be unchanged
    #the other portion be linear combo of the parents
        
    crossOverPt = myPRNG.randint(1,d-1) #notice I choose the crossover point so that at least 1 element of parent is copied
    
    beta = myPRNG.random()              #random number between 0 and 1
        
    #note: using numpy allows us to treat the lists as vectors
    #here we create the linear combination of the soltuions
    new1 = list(np.array(x1) - beta*(np.array(x1)-np.array(x2))) 
    new2 = list(np.array(x2) + beta*(np.array(x1)-np.array(x2)))
    
    #the crossover is then performed between the original solutions "x1" and "x2" and the "new1" and "new2" solutions
    if crossOverPt<d/2:    
        offspring1 = x1[0:crossOverPt] + new1[crossOverPt:d]  #note the "+" operator concatenates lists
        offspring2 = x2[0:crossOverPt] + new2[crossOverPt:d]
    else:
        offspring1 = new1[0:crossOverPt] + x1[crossOverPt:d]
        offspring2 = new2[0:crossOverPt] + x2[crossOverPt:d]        
    
    gamma = myPRNG.random()             #generate a random number to compare to crossover probability
    if (gamma <= crossOverRate):
        return offspring1, offspring2   #if gamma is within crossover probability return the new offspring1
    else:
        return x1, x2                   #otherwise return the copies of the parents as offspring
    

#function to evaluate the Schwefel Function for d dimensions
def evaluate(x):  
    val = 0
    d = len(x)
    for i in range(d):
        val = val + x[i]*math.sin(math.sqrt(abs(x[i])))
         
    val = 418.9829*d - val         
                    
    return val             
  

#function to provide the rank order of fitness values in a list
#not currently used in the algorithm, but provided in case you want to...
def rankOrder(anyList):
    
    rankOrdered = [0] * len(anyList)
    for i, x in enumerate(sorted(range(len(anyList)), key=lambda y: anyList[y])):  
        rankOrdered[x] = i     

    return rankOrdered

#performs tournament selection; k chromosomes are selected (with repeats allowed) and the best advances to the mating pool
#function returns the mating pool with size equal to the initial population
def tournamentSelection(pop,k):
    
    #randomly select k chromosomes; the best joins the mating pool
    matingPool = []
    
    while len(matingPool)<populationSize:
        
        ids = [myPRNG.randint(0,populationSize-1) for i in range(k)]
        competingIndividuals = [pop[i][1] for i in ids]
        bestID=ids[competingIndividuals.index(min(competingIndividuals))]
        matingPool.append(pop[bestID][0])

    return matingPool
    
#function to mutate solutions
def mutate(x):
    #mutate each element of the chromosome if random chance is below the mutation rate
    for i in range(len(x)):
        mutateNow = myPRNG.random()
        if mutateNow < mutationRate:

            #mutate the selected gene with a random valid value for x[i]
            newVal = myPRNG.uniform(lowerBound, upperBound)
            x[i] = newVal

    return x
        
            
    

    
def breeding(matingPool):
    #the parents will be the first two individuals, then next two, then next two and so on
    
    children = []
    childrenFitness = []
    for i in range(0,populationSize-1,2):
        child1,child2=crossover(matingPool[i],matingPool[i+1])
        
        child1=mutate(child1)
        child2=mutate(child2)
        
        children.append(child1)
        children.append(child2)
        
        childrenFitness.append(evaluate(child1))
        childrenFitness.append(evaluate(child2))
        
    tempZip = zip(children, childrenFitness)
    popVals = sorted(tempZip, key=lambda tempZip: tempZip[1])
        
    #the return object is a sorted list of tuples: 
    #the first element of the tuple is the chromosome; the second element is the fitness value
    #for example:  popVals[0] is represents the best individual in the population
    #popVals[0] for a 2D problem might be  ([-70.2, 426.1], 483.3)  -- chromosome is the list [-70.2, 426.1] and the fitness is 483.3
    
    return popVals


#insertion step
def insert(pop,kids):

    #combine the parents and offspring into one population of size 2*N
    totalPopulation = pop + kids
    
    #select the N best chromosomes from the total population
    totalPopulation = sorted(totalPopulation, key = lambda totalPopulation: totalPopulation[1])
    nextGen = totalPopulation[0:populationSize]
    return nextGen

    
#perform a simple summary on the population: returns the best chromosome fitness, the average population fitness, and the variance of the population fitness
def summaryFitness(pop):
    a=np.array(list(zip(*pop))[1])
    return np.min(a), np.mean(a), np.var(a)

#the best solution should always be the first element... if I coded everything correctly...
def bestSolutionInPopulation(pop):
    print (pop[0])
    
    

# ***************************************************************************************************    
#GA main code
initializeGA()

#opens an output file if required by the user
if (printToFile == 'y'):
    printTitle = savePath + "dim" + str(dimensions) + "pop" + str(populationSize) + "gen" + str(Generations) + "cross" + str(crossOverRate)    + "mut" + str(mutationRate)
    printTitle +=    "tour" + str(tournamentSize) + "var" + str(stoppingVariance) + ".txt"
    print(printTitle)
    f = open(printTitle, 'w')

Population = initializePopulation()
print(Population)

if turnOnPlotter == "y":
    plotPopulation(Population, "Initial Population Location")

currGeneration = 0

varVal = 1000


while (varVal > stoppingVariance) and (currGeneration < Generations):
    currGeneration += 1
    mates=tournamentSelection(Population,tournamentSize)
    Offspring = breeding(mates)
    Population = insert(Population, Offspring)
    
    minVal,meanVal,varVal=summaryFitness(Population)  #check out the population at each generation

    if (currGeneration % outputInterval == 0):                                     #output routine to show progress
        print("Current solution at generation " + str(currGeneration))
        bestSolutionInPopulation(Population)
        print("Fitness summary at generation " + str(currGeneration))
        print("Minimum f(x) = " + str(minVal) + " Mean f(x) = " + str(meanVal) + " Variance f(x) = " + str(varVal))
        print()

        if (printToFile == "y"):                                                   #sends output to file
            f.write("\n\nCurrent solution at generation " + str(currGeneration) + "\n")
            f.write(str(Population[0]))
            f.write("\nFitness summary at generation " + str(currGeneration))
            f.write("\nMinimum f(x) = " + str(minVal) + " Mean f(x) = " + str(meanVal) + " Variance f(x) = " + str(varVal))
        
    if (turnOnPlotter == "y") and ((currGeneration % plotterInterval == 0) or currGeneration == 1):         #plot population
        plotTitle = "Population of Generation " + str(currGeneration)
        plotPopulation(Population, plotTitle)
    

print("FINAL SOLUTION AT GENERATION " + str(currGeneration))
bestSolutionInPopulation(Population)
print("Minimum f(x) = " + str(minVal) + " Mean f(x) = " + str(meanVal) + " Variance f(x) = " + str(varVal))
if (printToFile == "y"):
    f.write("\n\nFINAL SOLUTION AT GENERATION " + str(currGeneration) + "\n")
    f.write(str(Population[0]))
    f.write("\nFitness summary at generation " + str(currGeneration))
    f.write("\nMinimum f(x) = " + str(minVal) + " Mean f(x) = " + str(meanVal) + " Variance f(x) = " + str(varVal))
    f.close()

if (turnOnPlotter == "y"):
    plotPopulation(Population, "Final Population Location")
    


