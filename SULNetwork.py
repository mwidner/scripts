#!/usr/bin/env python
'''
This script takes in a CSV file listing SUL staff->faculty working relationships
It outputs a GEXF file, named after the input, to generate a graph. ATSes, librarians, and faculty all receive a different color

Created on Mar 6, 2013

@author: Michael Widner <mikewidner@stanford.edu>
'''

import csv
import networkx as nx
from optparse import OptionParser
#import gspread

# make this into a separate script to run as a cron job for the survey
#def get_google_spreadsheet():
#    # go get the spreadsheet, download as CSv, the parse as usual
#    gc = gspread.login('thedude@abid.es', 'password')
#
#    # Open a worksheet from spreadsheet with one shot
#    wks = gc.open("Where is the money Lebowski?").sheet1
#
#    wks.update_acell('B2', "it's down there somewhere, let me take another look.")
#    list_of_lists = wks.get_all_values()


def main():
    parser = OptionParser(usage = "usage: %prog -f DATA.csv")
    parser.add_option("-e", dest = "edges_indirect", default = False, help = "Use target nodes as edges between sources")
#    parser.add_option("-s", "--size", dest = "size", default = "12pt", help = "12pt is default")
#    parser.add_option("-c", "--color", dest = "color", default = "000000", help = "Provide color as a hex color (or else). Default is 000000")
#    parser.add_option("-t", "--target-color", dest="target_color", default = "333333", help = "Color of the target nodes/edges")
#    parser.add_option("-z", "--target-size", dest="target_size", default = "10pt", help = "Size of the target nodes/edges")
    parser.add_option("-f", "--file", dest = "inputCSV", help = "Input a CSV FILE; expects .csv at the end", metavar = "FILE")
    parser.add_option("-g", "--gspread", dest = "gspread", help = "Retrieve data from Google spreadsheet")
#    parser.add

    (options, args) = parser.parse_args()
    
    if options.inputCSV == None and options.gspread == None:
        print("I need some data.")
        quit(1)
    if options.gspread and options.inputCSV:
        print("File input and Google Spreadsheet input options are incompatible. Choose one.")
        quit(1)

    G = nx.Graph()
    ATSes = {'Michael Widner', 'Jason Heppler', 'Vijoy Abraham', 'Nicole Coleman', 'Claudia Engel', 'Carlos Seligo', 'Ken Romeo'}
    with open(options.inputCSV, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for (staff, faculty_list) in [(row.pop(0), row.pop()) for row in reader]:
            staff = staff.strip()

            if staff in ATSes:
                G.add_node(staff, viz={'color': {'a': 1, 'r': 255, 'b': 0, 'g': 0}, 'size': 10})
            else:
                G.add_node(staff, viz={'color': {'a': 1, 'r': 0, 'b': 0, 'g': 255}, 'size': 10})

            for faculty in faculty_list.split(','):
                faculty = faculty.strip()
                G.add_node(faculty, viz={'color': {'a': 1, 'r': 0, 'b': 255, 'g': 0}, 'size': 10})
                G.add_edge(staff, faculty)
#    inputCSV.replace('.csv', '.gexf')
    if options.inputCSV:
        outfile = options.inputCSV.replace('.csv', '.gexf')
    else:
        outfile = options.gspread + '.gexf'
    nx.write_gexf(G, outfile)     

    
if __name__ == "__main__":
    main()