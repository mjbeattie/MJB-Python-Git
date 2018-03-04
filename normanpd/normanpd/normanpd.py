# Matthew J. Beattie
# DSA 5970
# Norman PD Assignment
# February 25, 2018
#!/usr/bin/python
# coding=utf-8

"""
normanpd.py
Contains functions for accessing data from the Norman, OK Police Department
arrest report, which is stored as a PDF.  Extracts data and transforms to
text with multiple functions.  Parses the text into an SQLLITE DB.

Created on Sun Feb 25 21:47:29 2018

@author: mjbea
"""

import re

def FetchIncidents(url):
    """ fetchincidents()
        Accesses the Norman PD arrest summary and using urllib
        reads it into a data object.
    """
    import urllib.request
#    print("Looking for", url)
#    url='http://normanpd.normanok.gov/filebrowser_download/657/2018-02-20%20Daily%20Arrest%Summary.pdf'

    data = urllib.request.urlopen(url).read()
    return data

def ExtractIncidents(url):
    """ extractincidents()
        Calls fetchincidents() to create a urllib data object containing
        Norman PD PDF data.  Writes a temporary file to disk to store the
        information during processing.  Uses PyPDF2.PdfFileReader to
        extract text from the data object and returns one page of text.
    """
    import tempfile
    import PyPDF2
    dataIn = FetchIncidents(url)
    fp = tempfile.TemporaryFile()

    # Write the pdf data to a temp file
    fp.write(dataIn)

    # Set the curser of the file back to the begining
    fp.seek(0)

    # Read the PDF
    pdfReader = PyPDF2.PdfFileReader(fp)
    pdfReader.getNumPages()
    
    # Get the first page
    page1 = pdfReader.getPage(0).extractText()
    
    fp.close()
    return page1


def ParseArrests(url):   
    """ ParseArrests() 
        Performs the bulk of the work in parsing the Norman PD police data.
        It takes in an address to the online PDF, converts to raw text data and searches for patterns
        identified by examining actual arrest records.  The output is a list that can be
        stored in json or DB format by other routines.
    """
    # Load Norman PD PDF into raw text data
    rawText = ExtractIncidents(url)
    
    # Strips the header and footer of the report, leaving the rows
    rawText2 = re.sub("Arrest.*Officer\\n", "", rawText, flags=re.DOTALL)
    rawText2 = re.sub(";\\nNORMAN POLICE.*\(Public\)\\n", "", rawText2, flags=re.DOTALL)   #Works for most
    # Required for 2/13:
    rawText2 = re.sub(";\\nDaily Arrest Activity.*NORMAN POLICE DEPARTMENT\\n","", rawText2, flags=re.DOTALL)
    
    # Splits the data into rows, using the last character in the last PD data field, which is ";"
    rows = re.split(";", rawText2)
    
    # Reads the text data into a vector of data records, where each element of the
    # record is the content of a data field
    records = []
    counter = 0
    for r in rows:
        fields = re.findall(".*", r)
        fields = [f for f in fields if f != '']         # Skips blanks created by extra newlines
        records.append(fields)
        
    # The list of states will be used to check for valid state codes when parsing the 
    # new records data structure.
    states = {
            'AK': 'Alaska',
            'AL': 'Alabama',
            'AR': 'Arkansas',
            'AS': 'American Samoa',
            'AZ': 'Arizona',
            'CA': 'California',
            'CO': 'Colorado',
            'CT': 'Connecticut',
            'DC': 'District of Columbia',
            'DE': 'Delaware',
            'FL': 'Florida',
            'GA': 'Georgia',
            'GU': 'Guam',
            'HI': 'Hawaii',
            'IA': 'Iowa',
            'ID': 'Idaho',
            'IL': 'Illinois',
            'IN': 'Indiana',
            'KS': 'Kansas',
            'KY': 'Kentucky',
            'LA': 'Louisiana',
            'MA': 'Massachusetts',
            'MD': 'Maryland',
            'ME': 'Maine',
            'MI': 'Michigan',
            'MN': 'Minnesota',
            'MO': 'Missouri',
            'MP': 'Northern Mariana Islands',
            'MS': 'Mississippi',
            'MT': 'Montana',
            'NA': 'National',
            'NC': 'North Carolina',
            'ND': 'North Dakota',
            'NE': 'Nebraska',
            'NH': 'New Hampshire',
            'NJ': 'New Jersey',
            'NM': 'New Mexico',
            'NV': 'Nevada',
            'NY': 'New York',
            'OH': 'Ohio',
            'OK': 'Oklahoma',
            'OR': 'Oregon',
            'PA': 'Pennsylvania',
            'PR': 'Puerto Rico',
            'RI': 'Rhode Island',
            'SC': 'South Carolina',
            'SD': 'South Dakota',
            'TN': 'Tennessee',
            'TX': 'Texas',
            'UT': 'Utah',
            'VA': 'Virginia',
            'VI': 'Virgin Islands',
            'VT': 'Vermont',
            'WA': 'Washington',
            'WI': 'Wisconsin',
            'WV': 'West Virginia',
            'WY': 'Wyoming'
    }
    
    
    dbRecords = []                      # This will be our list to convert into a database
    counter = 0
    for i in records:
        # Initialize the variables
        dbRecords.append(0)             # Create a blank for the first record
        r1 = records[counter]           # Create a temp record equal to the first list in records[]
        r2 = []                         # Create a temp record to be used to write to dbRecords
        counter2 = 0
    
        # Iterate through the items in records
        for j in r1:
            """ Check for HOMELESS or UNKNOWN, in which case the Norman PD has assigned an
                address of Norman, OK, but has left zipcode blank.  Replace zipcode with '00000'.
            """
            if (counter2==6 and (re.search("HOMELESS", r1[counter2], flags=re.DOTALL)!=None or 
                                 re.search("UNKNOWN", r1[counter2], flags=re.DOTALL)!=None)):
                r1.append(0)
                r1[11]=r1[10]
                r1[10]=r1[9]
                r1[9]="00000"
                
            """ Check for a missing state value.  Note that this will not be a NULL value, instead
                the parsed PDF will be missing a field.  So we need to add a field to the end of 
                the read-in record, shift the record values, and add a NULL state equal to "NN" """
            if counter2==8 and (r1[counter2] not in states):
                r1.append(0)
                for k in range(len(r1)-1,counter2,-1):
                    r1[k]=r1[k-1]
                r1[counter2]="NN"
    
            r2.append(0)                # Append a new record to r2 to store next block of r1 fields
    
            """Check for multiline fields.  In the Norman PD PDF, these have spaces  or hyphens at the end
                of broken lines.  If a multiline is found, add the next two fields from r1 to the
                current field in r1.  Continue until r1 doesn't have a space at the end.  One weakness
                approach is that is concatenates multiple people as one if present. """
            if ((re.search("\s$", r1[counter2], flags=re.DOTALL)!=None) or 
                (re.search("-$", r1[counter2], flags=re.DOTALL)!=None)):
                multiline=True
                while (multiline==True):
                    r2[counter2]=(r1[counter2]+r1[counter2+1])
                    del r1[counter2+1]
                    if re.search("\s$", r2[counter2], flags=re.DOTALL)!=None:
                        multiline=True
                    else:
                        multiline=False
            else:
                r2[counter2]=r1[counter2]
            counter2 += 1
    
        # Write the temporary record r2 to the current record value for r1
        dbRecords[counter]=r2
        counter += 1
    return dbRecords
  


def RecordLengthIntegrity(recordList):
    """ RecordLengthIntegrity()
        Counts the number of fields in a list of records.  If the number
        of fields for all records is not equal, the function returns False,
        else it returns True.  For diagnostics, it can print the fields.  This
        is commented out during normal operation.
    """
    for i in range(1, len(recordList)) :
#        print(i, len(dbRecords[i]))                     
        if (len(recordList[i]) != len(recordList[i-1])):
            print("Record at ", i, "has invalid length")
            return(False)
    return(True)
        

def DateFieldsIntegrity(recordList):
    """ DateFieldsIntegrity()
        Checks the record list to ensure that if a record contains a date
        field, it is in the same location as fields in the other records.
    """
    dateStr = []
    for i in range(0, len(recordList)) :
        r1 = recordList[i]
        r2 = []
        for j in range(0, len(r1)) :
            if (re.search("1?[0-9]\/[1-3]?[0-9]\/[0-9]{4}\s[1-2]?[0-9]\:[0-5][0-9]", r1[j]) 
            or re.search("1?[0-9]\/[1-3]?[0-9]\/[0-9]{4}", r1[j])):
                r2.append(1)
            else:
                r2.append(0)
        dateStr.append(r2)
        if i > 0 :
            if (dateStr[i] != dateStr[i-1]) and i > 0:
                print("Record at ", i, "has invalid length")
                return(False)
    return(True)
    

def CreateDB():
    """ CreateDB()
        Creates an SQLite database to store the records read in from the Norman PD arrest file.
        Takes a list of records produced by other normanpd.* routines.
    """
    import sqlite3 as lite
    import sys
    
    try:
        con = lite.connect('normanpd.db')
        cur = con.cursor()  
    
        cur.execute("DROP TABLE IF EXISTS Arrests")
        comString = "CREATE TABLE Arrests(arrest_time TEXT,arrest_number TEXT,arrest_location TEXT,offense TEXT,arrestee_name TEXT,arrestee_birthday TEXT,arrestee_address TEXT,status TEXT,officer TEXT)"

        cur.execute(comString)
        con.commit()
        con.close()
        
    except lite.Error as e:
        if con:
            con.rollback()
        print("Error %s:",e.args[0])
        sys.exit(1)
        
    finally:
        if con:
            con.close() 



def PopulateDB(recordList):
    """ PopulateDB()
        Stores the records read in from a Norman PD arrest list into an SQLite DB.
    """
    import sqlite3 as lite
    import sys
    
    try:
        con = lite.connect('normanpd.db')
        cur = con.cursor() 
        
        for currRec in recordList:
            at=currRec[0]
            an=currRec[1]
            al=currRec[2]
            of=currRec[3]
            name=currRec[4]
            bday=currRec[5]
            addr=currRec[6] + ", " + currRec[7] + ", " + currRec[8] + " " + currRec[9]
            st=currRec[10]
            cop=currRec[11]
            comString="INSERT INTO Arrests VALUES('"+at+"','"+an+"','"+al+"','"+of+"','"+name+"','"+bday+"','"+addr+"','"+st+"','"+cop+"')"
            cur.execute(comString)
            con.commit()
        con.close()
        
    except lite.Error as e:
        if con:
            con.rollback()
        print("Error %s:",e.args[0])
        sys.exit(1)
        
    finally:
        if con:
            con.close() 



def Status():
    """ Status()
        Prints the row count and first five rows of the Arrests table in the normanpd
        database to standard out.
    """
    import sqlite3 as lite
    import sys
    
    try:
        # Print out the number of rows in the Arrests table using SQL
        con = lite.connect('normanpd.db')
        cur = con.cursor() 
        comString="SELECT count(*) from Arrests"
        cur.execute(comString)
        data=cur.fetchall()
        output=data[0]
        print("The number of rows in the Arrests table is", output[0])
        
        # Read the rows in Arrests into an array and print out the first five
        # elements separated by the thorn character
        comString="SELECT * from Arrests"
        cur.execute(comString)
        data=cur.fetchall()
        stopNum=min(5,len(data))
        outString=""
        for i in range(0,stopNum):
            currRec=data[i]
            for j in range(0,len(currRec)-2):
                outString+=currRec[j]+u'\u00de'
            outString+=currRec[len(currRec)-1]+'\n'
            
        print(outString)
        con.close()
        
    except lite.Error as e:
        if con:
            con.rollback()
        print("Error %s:",e.args[0])
        sys.exit(1)
        
    finally:
        if con:
            con.close() 



 
    
        


    