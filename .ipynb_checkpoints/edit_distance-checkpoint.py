# Matthew J. Beattie
# DSA 5970
# Assignment 1
# February 11, 2018
#!/usr/bin/python
# coding=utf-8

""" editDist()
    This is the simplest version of the edit distance algorithm.  It
    recursively finds the distance between two strings.  Because it
    relies solely on recursion and doesn't store prior knowledge, it is
    very slow. """
def editDist(x, y):
    if len(x) == 0: return len(y)
    if len(y) == 0: return len(x)
    
    """ Recursion:  update current distance by calling distance
        for vertical, horizontal, and diagonal cells.  The edit
        value for each is 1 """
    delt = 1 if x[-1] != y[-1] else 0
    diag = edDistRecursive(x[:-1], y[:-1]) + delt 
    vert = edDistRecursive(x[:-1], y) + 1
    horz = edDistRecursive(x, y[:-1]) + 1
    return min(diag, vert, horz)

from numpy import zeros


""" distance()
    This version of the edit distance algorithm stores earlier calculated
    value into a distance matrix and calls those values rather than
    forcing recursion for every cell.  This results in a much faster
    execution time. """
def distance(x, y):
    """ Initialize distance matrix """
    D = zeros((len(x)+1, len(y)+1), dtype=int)
    D[0, 1:] = range(1, len(y)+1)
    D[1:, 0] = range(1, len(x)+1)
    
    """ Fill in distance matrix, updating the values of each cell along
        the way.  This avoids recursion. """
    for i in range(1, len(x)+1):
        for j in range(1, len(y)+1):
            delt = 1 if x[i-1] != y[j-1] else 0
            D[i, j] = min(D[i-1, j-1]+delt, D[i-1, j]+1, D[i, j-1]+1)
    return D[len(x), len(y)]


import argparse 
 
if __name__ == '__main__':     
    parser = argparse.ArgumentParser()     
    parser.add_argument("param1", type=str)     
    parser.add_argument("param2", type=str)     
    args = parser.parse_args()     
    if args.param1 and args.param2:      
        print("The edit distance between the two strings is: ",
              distance(args.param1, args.param2))
 #       print(editDistDP(args.param1, args.param2))     
    else:          
        print(distance("aa","bbb"))         
        print(distance("","")) 

