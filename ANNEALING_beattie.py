#------------------------------------------------------------------------------
#LOCAL SEARCH WITH FIRST IMPROVEMENT AND SIMULATED ANNEALING
#Student name:  Matt Beattie
#Date:          April 17, 2017


#need some python libraries
import copy
import random                   #NOTE:  I CHANGED THIS IN ORDER TO INCLUDE random.shuffle()
import numpy as np
import math


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
    

# setTemp
# arguments: integer j = iteration of algorithm, integer r = decay parameter, double maxT = maximum temp
# this method returns a temperature using Spears's factor
def setTemp(j,r,maxT):
    return (maxT * math.exp(-j*r))
    

# annealChoice
# arguments:  double newEval, double currEval, double currT
# this boolean method returns true if a random value is less than the annealing factor
def annealChoice(newEval, currEval, currT):
    testVal = random.random()
    annealVal = math.exp((newEval - currEval)/currT)
    if testVal < annealVal:
        return True
    else:
        return False



#variable to record the number of solutions evaluated
solutionsChecked = 0

# NOTE:  The function below chooses a good initial solution, but it doesn't work with 1-flip.  with
# 1-flip, every other solution will be suboptimal because it will violate weight or decrease the value.
# This complicated initial_solution should be used with 2-flip
x_curr = initial_solution(n,maxWeight,weights)  #x_curr will hold the current solution 

# NOTE:  The simple initial solution, all zeroes, allows for a larger feasible set of neighbors
#x_curr = [0] * n
x_best = x_curr[:]                                  #x_best will hold the best solution 
f_curr = evaluate(x_curr)                           #f_curr will hold the evaluation of the current soluton 
print("Initial weight is ", f_curr[1])
print("Initial value is ", f_curr[0])
f_best = f_curr[:]



#set Simulated Annealing parameters ----------------
MAX_T = 100
MIN_T = 1
j = 0
r = 0
done = 0
    
#conduct annealing iterations
T = MAX_T
while T > MIN_T:
            
    Neighborhood = neighborhood(x_curr)   #create a list of all neighbors in the neighborhood of x_curr
    
#The choice to move to a new solution is positive if the new solution is better than the current one
#(using the first improvement decision block) or if a random choice is made that is less than the annealing parameter
    newSolution = False
    index = 0
    MAX_ITER = len(Neighborhood)
    while newSolution is False and index < MAX_ITER:
        s = Neighborhood[index]
        newEval = evaluate(s)[:]
        solutionsChecked = solutionsChecked + 1
        if newEval[0] > f_best[0]:
            x_best = s[:]
            f_best = newEval[:]
            newSolution = True

        elif (annealChoice(newEval[0], f_best[0], T) is True and newEval[0] != -1):
            x_best = s[:]
            f_best = newEval[:]
            newSolution = True
        else:
            index = index + 1
    
    
    j += 1
    r = 1/n
    T = setTemp(j,r,MAX_T)

    x_curr = x_best[:]         #else: move to the neighbor solution and continue
    f_curr = f_best[:]         #evalute the current solution
        
    print ("\nTotal number of solutions checked: ", solutionsChecked)
    print ("Best value found so far: ", f_best) 
    
print ("\nFinal number of solutions checked: ", solutionsChecked)
print ("Best value found: ", f_best[0])
print ("Weight is: ", f_best[1])
print ("Total number of items selected: ", np.sum(x_best))
print ("Best solution: ", x_best)
