# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import nltk, re, pprint
from nltk import word_tokenize
from urllib import request

url = "http://www.gutenberg.org/files/2554/2554-0.txt"
response = request.urlopen(url)
raw = response.read().decode('utf8')
type(raw)
len(raw)
raw[:75]

tokens = word_tokenize(raw)


f = open('/users/mjbea/onedrive/GitHub/MJB-Python-Git/testfile.txt')
type(f)
raw = f.read()
type(raw)
print(raw)

rawTokens = word_tokenize(raw)

currSearch = re.findall(r"\$[1-4]\d\.\d\d", raw)
currSearch

currSearch = re.findall(r"\(\d{3}\)\d{3}\-\d{4}", raw)
currSearch

currSearch = re.findall(r"[\w+.+-]+@[\w]+\.edu", raw)
currSearch

currSearch = re.findall(r"\w+\smarried\s\w+", raw)
currSearch

currSearch = re.findall(r"201\.168\.[0-255]\.[0-255]", raw)
currSearch

for wordCheck in rawTokens:
    currSearch = re.search(r"\$[1-9][0-9].[0-9][0-9]", wordCheck)
    print(currSearch)


