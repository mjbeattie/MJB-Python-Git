# Matthew J. Beattie
# DSA 5970
# Finding Duplicates Assignment
# February 27, 2018
#!/usr/bin/python
# coding=utf-8

"""
Created on Mon Feb 26 19:57:34 2018

@author: mjbea
"""
import codecs
import re
from nltk import word_tokenize

def readthorn():
    """
        readthorn()
        Reads the discussion.thorn file into a string and then splits the string
        into a list of discussions.  The split is done by parsing on the thorn
        character.
    """
    # Read in the text file
    f = codecs.open("discussions.thorn", encoding='utf-8')
    allText = f.read()
    
    # Strip out special characters
    allText = re.sub('\\n',"",allText)
    allText = re.sub('\\t',"",allText)
    allText = re.sub('\"',"",allText)
    
    # Write the comments into a list of strings
    posts = re.split(u'\u00fe', allText)
    f.close()
    return posts


def stringtofile(string,filename):
    """
        stringtofile()
        Takes a string input and writes it to a file.
    """
    fileOut = codecs.open(filename, 'w', encoding='utf-8')
    print(string, file=fileOut)
    fileOut.close()
    return


def jaccarddist(list1, list2):
    """
        jaccarddist()
        Takes two lists of words and returns the Jaccard distance
    """
    s1 = set(list1)
    s2 = set(list2)
    return len(s1.intersection(s2))/len(s1.union(s2))
        
# Read posts into a list
posts = readthorn()

# Tokenize list into word lists and pass to jaccarddist to
# calculate the Jaccard index and store the results in a new list
output = []
for i in range(0,len(posts)-2):
    w1 = word_tokenize(posts[i])
    for j in range(i+1,len(posts)-1):
        w2 = word_tokenize(posts[j])
        dist = round(jaccarddist(w1,w2),4)
        item = [i, j, dist]
        output.append(item)
       
# Sort the list of Jaccard indices and print to standard out
output = sorted(output, key=lambda x: x[2], reverse=True)
for i in output:
    print(i[0], i[1], i[2])
        



