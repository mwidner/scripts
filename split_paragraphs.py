'''
Takes a list of HTML-formatted documents in a CSV file with a | delimiter
breaks the documents into paragraph chunks (by the <p> tag)
and writes them as files for topic modelling input

Mike Widner <mikewidner@stanford.edu>
February 2014
'''
import sys
import csv
import os
from bs4 import BeautifulSoup

MIN_LENGTH=600	# minimum characters in paragraph to save it

csv.field_size_limit(sys.maxsize) # Otherwise CSV chokes on the big text fields

out_dir = os.path.dirname(os.path.realpath(__file__)) + '/documents'
if not os.path.exists(out_dir):
	os.mkdir(out_dir)

reader = csv.DictReader(open(sys.argv[1], "r"), delimiter="|", quoting=csv.QUOTE_ALL)
for row in reader:
	doc_dir = out_dir + "/" + row['slug']
	if not os.path.exists(doc_dir):
		os.mkdir(doc_dir)
	paras = BeautifulSoup(row['text']).find_all("p")
	i = 0
	for para in paras:
		if para.string and len(para.string) >= MIN_LENGTH:
			fout = open(doc_dir + "/para" + str(i), "w", encoding="utf8")
			fout.write(para.string + "\n")
			i += 1
			fout.close()