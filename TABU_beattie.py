#------------------------------------------------------------------------------
#TABU SEARCH WITH BEST IMPROVEMENT
#Student name:  Matt Beattie
#Date:          April 17, 2017


#need some python libraries
import copy
import random                   #NOTE:  I CHANGED THIS IN ORDER TO INCLUDE random.shuffle()
import numpy as np


#to setup a random number generator, we will specify a "seed" value
#need this for the random number generation -- do not change
seed = 5113
myPRNG = random.Random(seed)

#to get a random number between 0 and 1, use this:             myPRNG.random()
#to get a random number between lwrBnd and upprBnd, use this:  myPRNG.uniform(lwrBnd,upprBnd)
#to get a random integer between lwrBnd and upprBnd, use this: myPRNG.randint(lwrBnd,upprBnd)

#number of elements in a solution
n = 100

#create an "instance" for the knapsack problem
value = []
for i in range(0,n):
    value.append(myPRNG.uniform(10,100))
    
weights = []
for i in range(0,n):
    weights.append(myPRNG.uniform(5,20))
    
#define max weight for the knapsack
maxWeight = 5*n

#change anything you like below this line ------------------------------------

#monitor the number of solutions evaluated
solutionsChecked = 0
solutionFoundAt = 0

#function to evaluate a solution x
def evaluate(x):
          
    a=np.array(x)
    b=np.array(value)
    c=np.array(weights)
    
    totalValue = np.dot(a,b)            #compute the value of the knapsack selection
    totalWeight = np.dot(a,c)           #compute the weight value of the knapsack selection
    
    if totalWeight > maxWeight:         # return a value of -1 if the solution is infeasible to ensure it isn't chosen
        totalValue = -1

    return [totalValue, totalWeight]   #returns a list of both total value and total weight
          
       
#here is a simple function to create a neighborhood
#1-flip neighborhood of solution x         
def neighborhood(x):
    nbrhood = []     
    for i in range(0,n):
        nbrhood.append(x[:])
        if nbrhood[i][i] == 1:
            nbrhood[i][i] = 0
        else:
            nbrhood[i][i] = 1
    return nbrhood
          


#create the initial solution
# initial_solution
# arguments: the number of items, maximum capacity of the knapsack and the weights of the items to be added.
# returns: an initial feasible solution as a list
# It comes up with a random order of items and includes them in the knapsack until its capacity is reached.
def initial_solution(n, capacity, weights):
    orderOfWeights = list(range(0,n))                               # setup a list with elements 0 through n-1
    random.shuffle(orderOfWeights)                                  # shuffle the list into a random order
    
    currentWeight = 0
    x = [None] * n                                                  # create an empty solution x
    for i in range(0,n):                                            # add items according to the random order
        if (currentWeight + weights[orderOfWeights[i]]) < capacity:
            x[orderOfWeights[i]] = 1
            currentWeight = currentWeight + weights[orderOfWeights[i]]
        else:
            x[orderOfWeights[i]] = 0
    return x
    




#varaible to record the number of solutions evaluated
solutionsChecked = 0

# NOTE:  The function below chooses a good initial solution, but it doesn't work with 1-flip.  with
# 1-flip, every other solution will be suboptimal because it will violate weight or decrease the value.
# This complicated initial_solution should be used with 2-flip
#x_curr = initial_solution(n,maxWeight,weights)  #x_curr will hold the current solution 

# NOTE:  The simple initial solution, all zeroes, allows for a larger feasible set of neighbors
x_curr = [0] * n
x_best = x_curr[:]                              #x_best will hold the best solution 
f_curr = evaluate(x_curr)                       #f_curr will hold the evaluation of the current soluton 
print("Initial weight is ", f_curr[1])
print("Initial value is ", f_curr[0])
f_best = f_curr[:]

#setup memory vector and memory manipulation method --------------------
memory = [0] * n                                #set a tabu short term memory vector to store restrictions
tenure = 10                                     #set the number of iterations to prohibit a variable change

#decrementMemory
#arguments: n dimensional vector, memory, containing current iterations to restrict each elements
#decrementMemory() decrements each positive element of the memory vector by 1
def decrementMemory(memory):
    for i in range(0, len(memory)):
        if memory[i] > 0:
            memory[i] -= 1
    return memory

#addToMemory
#arguments:  new solution vector, current solution vector, memory vector, tenure
#addToMemory() compares the new soluton vector to the old one, and where a variable has changed,
#it sets that index of the memory variable equal to tenure
def addToMemory(newSolution, currSolution, memory, tenure):
    assert (len(newSolution) == len(currSolution)) and (len(newSolution) == len(memory)), "addToMemory(): Error in vector lengths"
    
    for i in range(0, len(newSolution)):
        if (newSolution[i] != currSolution[i]):
            memory[i] = tenure
    return memory


#tabuNeighborhood
#arguments: solution vector x for the knapsack problem, n dimensional tabu memory vector,
#and aspirationVal, which is a scalar potential optimum.
#tabuNeighborhood() creates a neighborhood of vector x that excludes solutions that have
#had recent variable flips unless they are potentially optimal
def tabuNeighborhood(x, memory, aspirationVal):
    assert (len(x) == len(memory)), "tabuNeighborhood(): Error in vector lengths"
    nbrhood = [] 
    tempVector = []
    for i in range(0,n):
        tempVector = x[:]
        if tempVector[i] == 1:                   #flip the ith element of the x vector
            tempVector[i] = 0
        else:
            tempVector[i] = 1
            
        #include solution in neighborhood if not tabu or if possibly optimal
        if (memory[i] == 0) or (evaluate(tempVector)[0] > aspirationVal):    
            nbrhood.append(tempVector[:])
    return nbrhood


#begin local search overall logic ----------------
done = 0
    
while done == 0:
            
    Neighborhood = tabuNeighborhood(x_curr, memory, f_curr[0])   #create a list of all neighbors in the neighborhood of x_curr

    for s in Neighborhood:                      #evaluate every member in the neighborhood of x_curr
        solutionsChecked = solutionsChecked + 1
        if evaluate(s)[0] > f_best[0]:   
            x_best = s[:]                                            #find the best member and keep track of that solution
            f_best = evaluate(s)[:]                                  #and store its evaluation 
            memory = decrementMemory(memory)                         #decrement current memory vector
            memory = addToMemory(x_best, x_curr, memory, tenure)     #add tenure to memory vector at flipped position
    
    if f_best == f_curr:                        #if there were no improving solutions in the neighborhood
        done = 1

    else:
        
        x_curr = x_best[:]                      #else: move to the neighbor solution and continue
        f_curr = f_best[:]                      #evalute the current solution
        
        print ("\nTotal number of solutions checked: ", solutionsChecked)
        print ("Best value found so far: ", f_best)        
    
print ("\nFinal number of solutions checked: ", solutionsChecked)
print ("Best value found: ", f_best[0])
print ("Weight is: ", f_best[1])
print ("Total number of items selected: ", np.sum(x_best))
print ("Best solution: ", x_best)
