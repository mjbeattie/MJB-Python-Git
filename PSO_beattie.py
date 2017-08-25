#the intial framework for a particle swarm optimization for Schwefel minimization problem
#author: Matthew J. Beattie
#for ISE/DSA 5113


#need some python libraries
import copy
import math
from random import Random
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

import time                                                             #start a CPU clock
start = time.time()

savePath = 'c:/users/mjbea/OneDrive/ISE5113/Homework/Homework 5/'       #save path for files created


#to setup a random number generator, we will specify a "seed" value
seed = 12345
myPRNG = Random(seed)

#to get a random number between 0 and 1, write call this:             myPRNG.random()
#to get a random number between lwrBnd and upprBnd, write call this:  myPRNG.uniform(lwrBnd,upprBnd)
#to get a random integer between lwrBnd and upprBnd, write call this: myPRNG.randint(lwrBnd,upprBnd)

lowerBound = -500  #bounds for Schwefel Function search space
upperBound = 500   #bounds for Schwefel Function search space

# use Python classes to setup the PSO algorithm ************************************************

# additional parameters set for this particular problem ****************************************
boundaryPenalty = 100000

kappa = 1.0
phibar = 2.05
phi = 2*phibar

chi = float(2*kappa/(phi-2 + (phi*phi-4*phi)**(1/2.0)))

def getPhi(randomGenerator):
    lowerPhi = 0
    upperPhi = phibar
    return randomGenerator.uniform(lowerPhi, upperPhi)

def initializePSO():
    #set dimensions for Schwefel Function search space (should either be 2 or 200 for HM #5)
    global dimensions
    global method
    dimensions = int(input("Enter number of dimensions: ")) 
    method = str(input("Enter method (simple, ring, steep, gradient): "))
    
    #set size of GA population
    global swarmCount
    swarmCount = int(input("Enter swarm size: "))
    
    #set maximum number of Generations
    global Generations
    Generations = int(input("Enter maximum number of generations: "))
    
    global maxVelocity
    maxVelocity = float(input("Enter maximum velocity (float): "))
    
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


# The Particle class creates a generic PSO particle.  The changes in the algorithm are due to changes made to
# the updateVelocity() method, where inertia, etc. can be added
class Particle:
    def __init__(self, numDimensions, lowerBound, upperBound):
        
        #INITIALIZE ATTRIBUTES OF PARTICLE.  INCLUDES POSITION, VELOCITY, VALUE, NEIGHBORHOOD, GRADIENT, ETC.
        self.position = []                                                  #current position x
        self.velocity = []                                                  #velocity at current position
        self.bestPosition = []                                              #best position in particle memory
        self.value = None                                                   #f(x) at current position
        self.bestValue = None                                               #best remembered f(x)
        self.lowerBound = lowerBound                                        #lower boundary of x_i
        self.upperBound = upperBound                                        #upper boundary of x_i
        self.midpoint = (upperBound - lowerBound)/2 + lowerBound            #midpoint between boundaries
        self.speedbump = 0                                                  #flag for when Max Velocity is surpassed
        self.safespeed = 0                                                  #flag for safe velocity calculations
        self.neighborhood = None                                            #neighborhood for global best position
        self.ringNeighbors = None                                           #ring neighbors
        
        #TUNING PARAMETERS
        self.gradientStep = 1.0                                             #step for gradient calculation
        self.leapSize = maxVelocity/2                                       #leap for gradient of steep movement
        
        #INITIATE POSITION AND VELOCITY
        for i in range(numDimensions):
            self.position.append(myPRNG.uniform(lowerBound,upperBound))
            self.velocity.append(myPRNG.gauss(0,0.1))
            self.bestPosition.append(self.position[i])
            
        #INITIATE BEST VALUE AND POSITION
        self.value = self.evaluate(self.position)
        self.bestValue = self.value
        self.bestPosition = self.position
        test = self.steepestDescent()
            
    def getBestValue(self):
        return self.bestValue
    
    def getBestPosition(self):
        return self.bestPosition
    
    
    
    
    #simpleUpdateVelocity() uses the basic PSO velocity update routine including self and swarm knowledge
    #of best solutions to determine direction.  Maximum veloicty is a parameter sent by the calling method
    #to limit the speed of movement
    def simpleUpdateVelocity(self, maxVelocity):
        g = self.neighborhood.getGlobalBestPosition()                           #find best global neighbor in swarm
        for i in range(len(self.velocity)):
            self.velocity[i] += chi*(getPhi(myPRNG) * (self.bestPosition[i] - self.position[i]) + getPhi(myPRNG) * (g[i] - self.position[i]))
            if abs(self.velocity[i]) > maxVelocity:
                self.velocity[i] = myPRNG.gauss(maxVelocity/2,0.1)              #if maxVelocity is surpassed, create random velocity
                self.speedbump += 1
            else:
                self.safespeed += 1
        return
    
    
    #ringUpdateVelocity() replaces global swarm knowledge with a restricted neighborhood consisting of the 
    #nearest neighbors in N dimensions
    def ringUpdateVelocity(self, maxVelocity):                                  
        if self.ringNeighbors[0].bestValue < self.ringNeighbors[1].bestValue:
            index = 0
        else:
            index = 1
        g = self.ringNeighbors[index].bestPosition
        for i in range(len(self.velocity)):
            self.velocity[i] += chi*(getPhi(myPRNG) * (self.bestPosition[i] - self.position[i]) + getPhi(myPRNG) * (g[i] - self.position[i]))
            if abs(self.velocity[i]) > maxVelocity:
                self.velocity[i] = myPRNG.gauss(maxVelocity/2,0.1)              #if maxVelocity is surpassed, create random velocity
                self.speedbump += 1
            else:
                self.safespeed += 1
        return
                
                
    #steepDescentVelocity() replaces the best memorized position direction with the direction of steepest descent
    #in one of the N dimensions
    def steepDescentVelocity(self, maxVelocity):
        g = self.neighborhood.getGlobalBestPosition()                           #find best global neighbor in swarm
        steep = self.steepestDescent();
        for i in range(len(self.velocity)):
            if i == steep:
                self.velocity[i] += chi*(getPhi(myPRNG) * self.leapSize + getPhi(myPRNG) * (g[i] - self.position[i]))
            else:
                self.velocity[i] += chi*(getPhi(myPRNG) * (g[i] - self.position[i]))
            if abs(self.velocity[i]) > maxVelocity:
                self.velocity[i] = myPRNG.gauss(maxVelocity/2,0.1)              #if maxVelocity is surpassed, create random velocity
                self.speedbump += 1
            else:
                self.safespeed += 1
        return
    
    
    #gradientVelocity() replaces the best memorized position direction with the direction of declining
    #f(x) in all dimensions i in N.
    def gradientVelocity(self, maxVelocity):
        g = self.neighborhood.getGlobalBestPosition()
        dir = self.gradient()
        for i in range(len(self.velocity)):
            if dir[i] < 0:                                              #ensure local move is in direction of decreasing gradient
                move = 1
            else:
                move = -1
            self.velocity[i] += chi*(2*getPhi(myPRNG) * move*self.leapSize + getPhi(myPRNG) * (g[i] - self.position[i]))
            
            if abs(self.velocity[i]) > maxVelocity:
                self.velocity[i] = myPRNG.gauss(maxVelocity/2,0.1)      #if maxVelocity is surpassed, create random velocity       
                self.speedbump += 1
            else:
                self.safespeed += 1
        return

    
    #updatePosition() moves the particle according to the called velocity calculation function.  If the particle
    #passes over boundaries, it is called back to a point between the boundary and the midway point between
    #the low and high boundaries in that dimension
    def updatePosition(self):
        for i in range(len(self.velocity)):
            self.position[i] += self.velocity[i]
            if (self.position[i] > self.upperBound):                            #if position is infeasible reset between bound and midpoint
                self.position[i] = myPRNG.uniform(self.midpoint, self.upperBound)
            elif (self.position[i] < self.lowerBound):
                self.position[i] = myPRNG.uniform(self.lowerBound, self.midpoint)
        self.value = self.evaluate(self.position)
        if self.value < self.bestValue:
            self.bestPosition = self.position
            self.bestValue = self.value
        return
    
    
    #updateParticle() first calls a velocity updating method to find the size of the next move.
    #It then uses the new velocity vector to move the particle.  The velocity updating method
    #must be chosen manually before compilation.
    def updateParticle(self, method):                          #update particle by setting velocity and addition to position
        if (method == "simple"):
            self.simpleUpdateVelocity(maxVelocity)
        elif (method == "ring"):
            self.ringUpdateVelocity(maxVelocity)
        elif (method == "steep"):
            self.steepDescentVelocity(maxVelocity)
        else:
            self.gradientVelocity(maxVelocity)
        self.updatePosition()
        return
    

    #updateBestPosition() can be used by a calling method to explicitly set particle best position memory
    def setBestPosition(self, newPosition):
        self.bestPosition = newPosition

    
    #setValue() can be used by a calling method to explicitly set particle best value
    def setValue(self, value):
        self.value = value
        if (self.bestValue == None) or (value > self.bestValue):
            self.bestValue = value
        return
    

    #printParticle() prints out basic particle attributes
    def printParticle(self):
        print("Best position is: " + str(self.bestPosition) + " Best value is: " + str(self.bestValue))
        print("Current position is: " + str(self.position) + " Current value is: " + str(self.value))
        print("Current velocity is: " + str(self.velocity))
        print("Member of neighborhood: " + self.neighborhood.name)
        print("Global best position is: " + str(self.neighborhood.globalBestPosition) + " Global best value is: " + str(self.neighborhood.globalBestValue) + "\n")
        return

   
    #steepestDescent() evaluates the gradient of the particle at its current position and returns the direction
    #to move as that of the steepest descent
    def steepestDescent(self):
        steepestDescent = 0
        gradient = self.gradient()
        for i in range(len(gradient)):
            if i == 0:                                                                  #check for steep descent in dim i
                steepestDescent = 0
            elif gradient[i] < gradient[i-1]:
                steepestDescent = i
        return i                                                                        #return dim of steepest descent


    #gradient() calculates and returns the gradient at current particle position.  It uses the
    #particle tuning parameter gradientStep for the dx component of df(x)/dx
    def gradient(self):
        gradient = []
        newPosition = self.position
        for i in range(len(self.position)):
            newPosition[i] += self.gradientStep                                              #move a step in the ith direction
            gradient.append((self.evaluate(newPosition) - self.value)/self.gradientStep)     #calculate df(x)/d(x_i)
            newPosition[i] -= self.gradientStep
        return gradient


    def evaluate(self, x):          
        val = 0
        d = len(x)
        for i in range(d):
            val = val + x[i]*math.sin(math.sqrt(abs(x[i])))
        val = 418.9829*d - val         
        return val      

    #END CLASS PARTICLE


# The Swarm class is a set of PSO particles.  The class includes methods for updating, printing, etc.        
class Swarm:
    def __init__(self, name, dim, swarmSize):                          #initialize the swarm, setting null values to bests
        self.name = name
        self.dim = dim
        self.swarmSize = swarmSize
        self.particles = []
        self.globalBestPosition = []
        self.globalBestValue = 1e10
        self.speedbump = 0
        self.safespeed = 0
        for i in range(self.swarmSize):
            p = Particle(dimensions, lowerBound, upperBound)
            self.addParticle(p)
        self.buildRings()

    def getName(self):
        return self.name
    
    def getGlobalBestValue(self):
        return self.globalBestValue
    
    def setGlobalBestValue(self, g):
        self.globalBestValue = g
        return
        
    def getGlobalBestPosition(self):
        return self.globalBestPosition
    
    def setGlobalBestPosition(self, g):
        self.globalBestPosition = []
        for i in range(len(g)):
            self.globalBestPosition.append(g[i])
        return
    
    def addParticle(self, newParticle):                             #adds a particle to the swarm
        self.particles.append(newParticle)
        if self.getGlobalBestValue == None:                         #if first particle, set best values of swarm
            self.setGlobalBestValue(newParticle.getBestValue())
            self.setGlobalBestPosition(newParticle.getBestPosition())
        elif newParticle.getBestValue() < self.getGlobalBestValue():          #if particle is better, set best values of swarm
            self.setGlobalBestValue(newParticle.getBestValue())
            self.setGlobalBestPosition(newParticle.getBestPosition())
        newParticle.neighborhood = self
        return
    
    #buildRings() sets rings based upon the creation sequence of particles.  This may not be correct as it
    #may need to be updated to build rings based upon closest neighbors in any generation
    def buildRings(self):                                           #build ring topology neighbors for each particle
        for i in range(self.swarmSize):
            if i == 0:
                self.particles[i].ringNeighbors = [self.particles[self.swarmSize - 1], self.particles[i+1]]
            elif i == (self.swarmSize-1):
                self.particles[i].ringNeighbors = [self.particles[i-1], self.particles[0]]
            else:
                self.particles[i].ringNeighbors = [self.particles[i-1], self.particles[i+1]]
        return
    
    
    def updateSwarm(self, method):                                          #update swarm by updating all particles
        self.speedbump = 0
        self.safespeed = 0
        for i in range(self.swarmSize):
            self.particles[i].updateParticle(method)                        #reset global bests with new information
            self.speedbump += self.particles[i].speedbump                   #count the number of times Max Velocity passed
            self.safespeed += self.particles[i].safespeed
            if self.particles[i].getBestValue() < self.getGlobalBestValue():
                self.setGlobalBestValue(self.particles[i].getBestValue())
                self.setGlobalBestPosition(self.particles[i].getBestPosition())
        
    
    def printSwarm(self, currGeneration):                                           #print out particles in the swarm
        print("PRINTING SWARM: " + self.name)
        print("Global best position: " + str(self.globalBestPosition) + " Global best value: " + str(self.globalBestValue) + "\n")
        for i in range(self.swarmSize):
            self.particles[i].printParticle()
        return

    def writeSwarm(self, currGeneration, file):
        for i in range(self.swarmSize):
            file.write(str(currGeneration) + ";" + str(i) + ";" + str(self.particles[i].position) + ";" + str(self.particles[i].velocity) + ";" + str(self.particles[i].value) + "\n")
        return
    

    def plotSwarm(self, title):                                     #plotting function for 2D swarm
        if (self.dim > 2):
            print("BYPASS PLOTTING:  Dimension larger than 2")
            return
        else:
            x = [self.particles[i].position[0] for i in range(s.swarmSize)]
            y = [self.particles[i].position[1] for i in range(s.swarmSize)]
            z = [self.particles[i].value for i in range(s.swarmSize)]
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(x,y,z, c='r', marker='o')
            ax.set_title(title)
            ax.set_xlabel("x1-value")
            ax.set_ylabel("x2-value")
            ax.set_zlabel("f(x)")
            outputPlot = savePath + 'plotfile' + title + '.png'
            fig.savefig(outputPlot)
            plt.close(fig)
            return

    # END CLASS SWARM

# *********** MAIN *************
initializePSO()

if (printToFile == 'y'):
    printTitle = str(input("Enter title of output file: "))
    printTitle = savePath + printTitle + ".txt"
    f = open(printTitle, 'w')
    f.write("Generation;Particle;p;v;f(p)\n")

#initialize swarm

print("Initializing swarm")
s = Swarm("TESTSWARM", dimensions, swarmCount)

varVal = 100000                                             #initialize algorithm stopping counters
currGeneration = 0
lastBest = s.globalBestValue

if (printToFile == 'y'):                                        #write first swarm to file
    s.writeSwarm(currGeneration, f)

bestGeneration = 0
    
while (varVal > stoppingVariance) and (currGeneration < Generations):
    currGeneration += 1
    s.updateSwarm(method)
    if s.globalBestValue < lastBest:
        bestGeneration = currGeneration
#    varVal = lastBest - s.globalBestValue
    lastBest = s.globalBestValue

    if (currGeneration % outputInterval == 0):                                     #output routine to show progress
        print("GENERATION: " + str(currGeneration))
        print("Global best position: " + str(s.globalBestPosition))
        print("Global best value: " + str(s.globalBestValue))
        print("Improvement in move: " + str(varVal) + "\n")

        if (printToFile == "y"):                                                   #sends output to file
            s.writeSwarm(currGeneration, f)
            
    if (turnOnPlotter == "y") and (currGeneration <= 3):         #plot population
        plotTitle = "Swarm of Generation " + str(currGeneration)
        s.plotSwarm(plotTitle)

print("FINAL SOLUTION AT GENERATION " + str(bestGeneration))
print("Global best position: " + str(s.globalBestPosition))
print("Global best value: " + str(s.globalBestValue))
print("Improvement in move: " + str(varVal) + "\n")
print("Maximum velocity surpassed: " + str(s.speedbump) + " times")
print("Safe velocity was calculated: " + str(s.safespeed) + " times")

if (printToFile == "y"):                                                   #sends output to file
    f.close()        

end = time.time()

print("TOTAL CPU TIME USED WAS " + str(end-start))


 
    

