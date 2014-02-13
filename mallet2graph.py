'''
Takes topic model output and converts it into a Gexf file, which Gephi can read
Assumes that your topic model input was a corpus where each document was split into chunks
and that each chunk lives in a subdirectory for the parent document
Expects the standard Mallet output of doc-topics.txt and topic-keys.txt

Mike Widner <mikewidner@stanford.edu>
February 2014
@author: widner
'''

import csv
import os
from optparse import OptionParser
import networkx as nx

def parse_options():
    parser = OptionParser(usage='Usage: %prog -d doc-topics.txt -t topic-keys.txt -o output')
    parser.add_option('-d', '--doc-topics',
                      dest = 'doc_topics',
                      metavar = 'FILE',
                      help = 'The doc-topics.txt MALLET output')
    parser.add_option('-o', '--out',
                      dest = 'out',
                      metavar = 'FILE',
                      help = 'Output file')
    parser.add_option('-t', '--topic-keys',
                      dest = 'topics',
                      metavar = 'FILE',
                      help = 'The topic-keys.txt MALLET output')

    options, args = parser.parse_args()
    if options.doc_topics is None or options.topics is None or options.out is None:
        print(parser.print_help())
        exit(-1)
    return(options)

def split_doc_chunk(doc):
  '''
  Returns the document name and the chunk name
  '''
  doc = doc.replace('file:', '', 1) # strip any leading "file:" string
  doc, chunk = os.path.split(doc)
  doc = doc.rsplit('/', 1)[1]       # Note: assumes *nix-style path delimiters
  return(doc, chunk)

def calc_edge_weights(doc_topic_weights, doc_name, chunk_name, weights):
  '''
  Determines the edge weights for each document-topic link
  We assume that a document's edge weight to a topic should be whatever
  the highest weight is for any chunk of that document
  '''
  while len(weights) >= 2:
    # grab pairs of items
    tid = weights.pop(0)
    weight = float(weights.pop(0))
    if doc_name in doc_topic_weights.keys():
      if tid in doc_topic_weights[doc_name].keys():
        cur_weight = doc_topic_weights[doc_name][tid]
        if cur_weight < weight:
          doc_topic_weights[doc_name][tid] = weight
      else:
        doc_topic_weights[doc_name][tid] = weight
    else:
      doc_topic_weights[doc_name] = dict()
      doc_topic_weights[doc_name][tid] = weight
  return(doc_topic_weights)

def main():
  options = parse_options()
  topics = csv.reader(open(options.topics, 'r'), delimiter='\t')
  weights = csv.reader(open(options.doc_topics, 'r'), delimiter='\t')
  doc_topic_weights = dict()
  next(weights, None) # skip first line, which is a poorly-formatted header
  for weight in weights:
    doc_name, chunk_name = split_doc_chunk(weight[1])
    doc_topic_weights = calc_edge_weights(doc_topic_weights, doc_name, chunk_name, weight[2:])
  
  G = nx.Graph()
  G.add_nodes_from([doc for doc in doc_topic_weights.keys()])
  for topic in topics:
    G.add_node(topic[0], label=topic[2], viz={'size': topic[1]}) # size by topic weight
    for doc in doc_topic_weights.keys():
      for tid in doc_topic_weights[doc].keys():
        if tid == topic[0]:
          G.add_edge(tid, doc, weight=doc_topic_weights[doc][tid])

  try:
    nx.write_gexf(G, options.out)
  except Exception as err:
    print("Could not write graphfile", options.out, err)

if __name__ == '__main__':
    main()