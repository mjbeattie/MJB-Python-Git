# Matthew J. Beattie
# DSA 5970
# Assignment 1
# February 4, 2018
#!/usr/bin/python
# coding=utf-8
# ^^ because https://www.python.org/dev/peps/pep-0263/

from __future__ import division

import codecs
import json
import nltk
import os
import xmltodict
from bs4 import BeautifulSoup
from nltk import sent_tokenize
from nltk import word_tokenize

# It is okay to include tokenization and symbols in the average word size count.
# Use the Thorn character (þ) to separate the fields
# Be sure to include coding=utf-8 to the first or second line

# All the output can be printed to the screen

# Note, when printing to a non-unicode terminal or using linux to write to a file
# http://stackoverflow.com/questions/4545661/unicodedecodeerror-when-redirecting-to-file

# You may need to download a corpus in nltk using the nltk.download() command.
# If you are having trouble completing feel free to post a message on the forum.

# Usage: PYTHONIOENCODING=UTF-8 python3 process-data.py > output.txt

def question1():
    fileOut = codecs.open('twitter_parse.csv', 'w', encoding='utf-8')
    with codecs.open("twitter.txt", encoding='utf-8') as f:
        testOut = f.read()
        sentenceNum = 0
        sentences = sent_tokenize(testOut)
        for sentItem in sentences:
            sentenceNum += 1
            sentItem = sentItem.strip()
            sentItem = sentItem.replace("    ", "")
            wordItem = word_tokenize(sentItem)
            wordItem=[w for w in wordItem if w.isalpha()]
            totalLetters = 0
            for w in wordItem:
                totalLetters += len(w)
            avgWordLength = (round(totalLetters/len(wordItem),2) if len(wordItem) > 0 else 0)
            print(sentenceNum, u'\u00de', sentItem, u'\u00de', avgWordLength, sep="", file=fileOut)
    fileOut.close()
    f.close()

def question2():
    fileOut = codecs.open('twitter_parse.xml', 'w', encoding='utf-8')
    print('<document><sentences>', file=fileOut)
    with codecs.open('twitter.txt', encoding='utf-8') as f:
        testOut = f.read()
        sentenceNum = 0
        sentences = sent_tokenize(testOut)
        for sentItem in sentences:
            sentenceNum += 1
            sentItem = sentItem.strip()
            sentItem = sentItem.replace("    ", "")
            wordItem = word_tokenize(sentItem)
            wordItem=[w for w in wordItem if w.isalpha()]
            totalLetters = 0
            for w in wordItem:
                totalLetters += len(w)
            avgWordLength = (round(totalLetters/len(wordItem),2) if len(wordItem) > 0 else 0)
            print('<sentence id=\"', sentenceNum, '\"><text>', sentItem, '</text><avg>',
                  avgWordLength, '</avg></sentence>', sep="", file=fileOut)
    print('</sentences></document>', file=fileOut)
    fileOut.close()
    f.close()
    
    # Convert xml file to pretty format via BeautifulSoup
    fileOut = codecs.open('twitter_pretty_parse.xml', 'w', encoding='utf-8')
    with codecs.open('twitter_parse.xml', 'r', encoding='utf-8') as f:
        handler = f.read()
        soup = BeautifulSoup(handler)
        print(soup.prettify(), file=fileOut)
    fileOut.close()
    f.close()


def question3():
    fileOut = codecs.open('twitter_parse.json', 'w', encoding='utf-8')
    with codecs.open('twitter_pretty_parse.xml', 'r', encoding='utf-8') as f:
        handler = f.read()
        xmlIn = xmltodict.parse(handler)
        print(json.dumps(xmlIn), file=fileOut)
    f.close()
    fileOut.close()

        

if __name__ == '__main__':
    question1()
    question2()
    question3()