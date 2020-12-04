# Matthew J. Beattie
# DSA 5970
# Norman PD Assignment
# February 25, 2018
#!/usr/bin/python
# coding=utf-8

"""
main.py
Shell program for the Norman PD data scrubbing assignment.  Calls routines from
normanpd.py to parse text from the Norman arrests pdf datasheet.

Created on Sun Feb 25 21:47:29 2018

@author: mjbea
"""
import argparse

#import normanpd
from normanpd import normanpd

def main(url):

    print("Starting main...")
    print("Passed URL is", url)

    # Copy the Norman PD pdf file into the local drive for reference
    testfile = normanpd.FetchIncidents(url)
    print("Fetched incidents")
    testfileout = open('normanpd.pdf', 'wb')
    testfileout.write(testfile)
    testfileout.close()

    # Extract data and parse into a list of records suitable for a database
    print("Parsing...")
    dbRecords = normanpd.ParseArrests(url)
    
    # Check the integrity of the list to ensure all records have the same number
    # of fields and that any date fields occur in the same place
    print("Checking data records integrity...")
    print(normanpd.RecordLengthIntegrity(dbRecords))
    print(normanpd.DateFieldsIntegrity(dbRecords))
    
    # Create database
    print("Creating database in SQLite...")
    normanpd.CreateDB()
    
    # Insert arrest data into database
    print("Populating Arrests table...")
    normanpd.PopulateDB(dbRecords)
    
    # Print status
    print("Showing database status...")
    normanpd.Status()
	
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--arrests", type=str, required=True, help="The arrest summary url.",default="http://normanpd.normanok.gov/filebrowser_download/657/2018-02-13%20Daily%20Arrest%20Summary.pdf")
    
    args = parser.parse_args()
    if args.arrests:
        print(args.arrests)
        main(args.arrests)

