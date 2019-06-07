#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#  Tool to transform a Kicad .csv Bill-of-Materials file
#    into a markdown table for Github
#  28-05-2019
#  Copyright 2019
#  v1.0.0.0 : initial script
##########################################################

import argparse
import sys
import os

# helper to set up the argument parser
def setupArgParser():
    description = '''
    Markdown BOM generator
    ----------------------
    This tool generates a GitHub bill-of-materials markdown table
    based on a .csv-file exported from Kicad.\n
    Components are listed alphabetically.
    Consecutive denominators are grouped to minify the list (R1,R2,R3,R4,R5 -> R1-5).
    '''
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('inputfile', help='bill-of-materials .csv-file from Kicad', nargs='*')
    parser.add_argument('-o', '--outputfile', help='markdown file containing the generated BOM-table to publish on Github', nargs='*'))

    return parser

# helper to clean combined designators
def simplifyNameList(names):
    nameList = names.split(",")
    num = ["0","1","2","3","4","5","6","7","8","9"]
    numList = []
    if (len(nameList) > 1):
        for entry in nameList:
            i = 0
            alphaPart = True
            while (alphaPart):
                if (entry[i] in num):
                    alphaPart = False
                i += 1
            i -= 1
            denominator = entry[:i]
            numList.append(int(entry[i:]))
        numList.sort()
        minList = denominator

        minList += minifyNumList(numList)

        return minList
    else :
        return names

# helper to group consecutive designators
#  two consecutive denominators will also make a group
def minifyNumList(numList):
    minList = ""
    while (len(numList) > 0):
        if (len(numList) == 1):
            minList += str(numList.pop(0))
        elif (len(numList) == 2):
            oneButLast = numList.pop(0)
            veryLast = numList.pop(0)
            if ((veryLast - oneButLast ) == 1):
                minList = minList + str(oneButLast) + "-" + str(veryLast)
            else:
                minList = minList + str(oneButLast) + "," + str(veryLast)
        elif (len(numList) > 2):
            first = numList.pop(0)
            if ((numList[0] - first) > 1):
                minList = minList + str(first) + ","
            else:
                i = 0
                while ((i < len(numList)) and ((numList[i] - first) == (i + 1))):
                    i += 1
                if (i < 1):
                    minList = minList + str(first) + ","
                else:
                    last = ""
                    while (i > 0):
                        last = str(numList.pop(0))
                        i -= 1
                    minList = minList + str(first) + "-" + last + ","
    minList = minList.rstrip(",")
    return minList

# main procedure to generate the md-table
def generateBOM():
    parser = setupArgParser()
    args = parser.parse_args()
    csvInFile = ' '.join(args.inputfile)

    try:
        if os.path.isfile(csvInFile):

            try:
                mdOutFile = ' '.join(args.outputfile)
            except:
                mdOutFile = csvInFile.rstrip(".csv") + ".md"

            print "Generating markdown bill-of-materials table to publish on Github."
            print "input file  : " + csvInFile
            print "output file : " + mdOutFile

            # get BOM from .csv-file
            with open(csvInFile) as f:
                bomLines = f.readlines()
            f.close()

            bomList = {}
            bomTable =  " Part | Value | Package | Quantity \n"
            bomTable += " ---- | ----- | ------- | -------- \n"
            bomArrayList = []

            for record in bomLines:
                data = record.split(";")
                if (data[0] != '"Id"'):
                    component = {}
                    component['designator'] = simplifyNameList(data[1].strip('\"'))
                    component['package'] = data[2].strip('\"')
                    component['quantity'] = data[3]
                    component['designation'] = data[4].strip('\"')
                    component['reference'] = data[5].strip('\"')
                    bomList[data[0]] = component
                    bomLine = " " + component['designator'] + " | " + component['designation'] + " | " + component['package'] + " | " + component['quantity'] + " \n"
                    bomArrayList.append(bomLine)

            bomArrayList.sort()

            for line in bomArrayList:
                bomTable += line

            f = open(mdOutFile,'w')
            f.write(bomTable)
            f.close()

            print "Done."
        else:
            print "Input-file not found !\nType : \"{0} -h\" for help on how to use this tool".format(__file__)
    except:
        print "Error processing your request !!\nType : \"{0} -h\" for help on how to use this tool\n{1}".format(__file__,sys.exc_info())

if __name__ == '__main__':
    generateBOM()
