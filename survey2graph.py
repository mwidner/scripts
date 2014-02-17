#!/usr/bin/env python
'''
A script to read in CSV results from a survey of people
Generates network graphs from responses
Edges are between people with the same answers to the same questions
Or, if bi-modal option selected, between answer and person
Creates multiple networks: one per question, then one per question group
Reads a configuration file with column headers, sections, weights
Uses a lot of global variables, defined in main()

Created on May 3, 2013

@author: Michael Widner <mikewidner@stanford.edu>
'''

import csv
import networkx as nx
import os.path
import errno
from optparse import OptionParser
from configobj import ConfigObj

# initializes lists of questions and answers
def _init_list(question, answer):
    try:
        who_answered[question][answer] = list()
    except KeyError:
        who_answered[question] = dict()

def get_weight(question):
    weights = {question: WEIGHT[section][question] for section in WEIGHT.keys() 
               for question in WEIGHT[section]}
    try:
        w = weights[question]['weight']
    except KeyError:
        w = DEFAULT_WEIGHT
    return(w)

# Builds lists of names of people with the same answer to the same question
def link_name_to_answer(question, answer, name):
    # append names to the list for the given answer; skip empties  
    answer = answer.title().strip()
    name = name.title().strip()
    if not question.isspace() or not answer.isspace():
        try:
            who_answered[question][answer].append(name)
        except KeyError:
            _init_list(question, answer)
            who_answered[question][answer] = [name]
            
def parse_data(filename):
    reader = csv.DictReader(open(filename, 'rU'), quoting=csv.QUOTE_MINIMAL)
    answers_by_person = {row[NAME].strip(): row for row in reader}
    for name in answers_by_person:
        # We only graph questions listed in the config file
        for question in [question for section in WEIGHT.keys() 
                         for question in WEIGHT[section].keys()]: 
            answers = answers_by_person[name][question]
            # is the answer csv? 
            # relies on data being clean enough that no answers have commas
            if (answers.find(',') != -1):
                try:
                    for answer_list in list(csv.reader([answers])):
                        for answer in answer_list:
                            link_name_to_answer(question, answer, name)
                except csv.Error as exception:
                    print "ERROR: Please clean your data --", exception
                    exit(1)
            else:
                link_name_to_answer(question, 
                                    answers_by_person[name][question], 
                                    name)
    return(answers_by_person)   

def get_label(question, answer, loose = False):
    label = ''
    if not loose:
        for section in WEIGHT.keys():
            if question in WEIGHT[section]:
                try:
                    if WEIGHT[section][question]['label'] == 'key':
                        label = question
                except KeyError:
                    label = answer
                else:
                    label = question
    return(label)

# Adds edges between names and answers
# Makes each answer also a node
def add_bimodal_edges(G, question):
    G.add_edges_from([(answer, name) for answer in who_answered[question].keys()
                      for name in who_answered[question][answer]],
                     weight = get_weight(question),
                     label = get_label(question, answer))

# Takes a list of names and their answers, generates edges among all of them
# Edges are for answers in common per question
def add_unimodal_edges(G, question):
    for answer in who_answered[question]:
        # Logic here assumes that all person nodes already added
        if len(who_answered[question][answer]) == 1:
            if options.loose and not answer in G.nodes():
                # technically bi-modal here
                G.add_edge(who_answered[question][answer].pop(),
                           answer,
                           viz={'size': DEFAULT_SIZE},
                           weight=get_weight(question))
            elif answer in G.nodes():
                G.add_edge(who_answered[question][answer].pop(), 
                           answer,
                           Title=get_label(question, answer),
                           weight=get_weight(question))
        elif len(who_answered[question][answer]) > 1:
            cur_name = who_answered[question][answer].pop(0)
            G.add_edges_from(
                             [(cur_name, name) 
                              for name in who_answered[question][answer]],
                              weight=get_weight(question), 
                              Title=get_label(question, answer))
            # Hooray for recursion! Link all our names together
            add_unimodal_edges(G, question)  

def make_graph(section = False, question = False, G = False):
    if not G:
        G = nx.Graph()
        G.add_nodes_from([(name.title(), 
                           dict(viz={'size': SIZE[answers_by_person[name][SIZE_KEY]]})) 
                           for name in answers_by_person])
    if section:
        for question in WEIGHT[section]:
            make_graph(False, question, G)    
    if question:
        if options.bimodal:
            add_bimodal_edges(G, question)
        else:
            add_unimodal_edges(G, question)
    return(G)

# Generates a network graph by making edges for common answers
# Only looks at the answers passed in, not all
def write_graph(section, question = False):
    if not question:
        G = make_graph(section)
    else:
        G = make_graph(False, question)
    if not options.dry_run:
        if not options.output:
            options.output = os.path.dirname(options.csvfile)
        graphfile = options.output + '/' + section.replace(' ', '_')
        if question:
            graphfile += '-' + question.replace(' ', '_')
        graphfile += '.gexf'
        try:
            nx.write_gexf(G, graphfile)
            if options.verbose:
                print "Saved graph:", graphfile
        except UnicodeDecodeError:
            print 'Error: non-ASCII characters; cannot write', section

# parses the cmd-line options
def parse_options():
    parser = OptionParser(usage = "Usage: %prog -c configuration.ini -i input.csv <options>")
    parser.add_option('-i', '--input', 
                      dest = 'csvfile', 
                      help = 'Select a CSV file that contains survey results', 
                      metavar = 'FILE')
    parser.add_option('-c', '--config', 
                      dest = 'configfile', 
                      help = 'Select a configuration file to set edge weights', 
                      metavar = "FILE")
    parser.add_option('-l', '--loose_ends',
                      dest = 'loose',
                      action = 'store_true',
                      default = False,
                      help = 'Should we show answers with only one respondent?')
    parser.add_option('-d', '--dry_run',
                      help = 'Perform a dry run; do not write GEXFs (default: False)',
                      dest = 'dry_run',
                      action = 'store_true',
                      default = False)
    parser.add_option('-v', '--verbose',
                      help = 'Verbose mode (default: False)',
                      dest = 'verbose',
                      action = 'store_true',
                      default = False)
    parser.add_option('-o', '--output',
                      help = 'Output directory (default: same as for --input)',
                      dest = 'output')
    parser.add_option('-b', '--bimodal',
                      help = 'Create a bimodal network (default: False)',
                      action = 'store_true',
                      dest = 'bimodal')
     
    (options, args) = parser.parse_args()
    if not options.csvfile or not options.configfile or len(args):
        print(parser.print_help())
        exit(1)
    if options.output and not os.path.exists(options.output):
        try:
            os.makedirs(options.output)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                print 'Error creating output directory', options.output
                exit(1)
    return(options)

def main():
    global options
    options = parse_options()
    config = ConfigObj(options.configfile)
    global NAME
    global SIZE
    global SIZE_KEY
    global WEIGHT
    global DEFAULT_SIZE
    global DEFAULT_WEIGHT
    try:
        NAME = config['NAME']
        SIZE = config['SIZE']
        SIZE_KEY = config['SIZE_KEY']
        DEFAULT_SIZE = config['DEFAULT_SIZE']
        WEIGHT = config['WEIGHT']
        DEFAULT_WEIGHT = config['DEFAULT_WEIGHT']
    except KeyError as err:
        print "ERROR: Value not found in configuration file for", err
        exit(1)

    global who_answered         # the complete list of answers
    who_answered = dict()    
    global answers_by_person    # used in make_graph()
    answers_by_person = parse_data(options.csvfile)
   
    for section in WEIGHT:
        write_graph(section)
        for question in WEIGHT[section]:
            write_graph(section, question)

if __name__ == "__main__":
    main()  