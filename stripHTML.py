'''
Created on Sep 25, 2012

@author: widner
'''

import nltk
import sys

def stripHTML():
    for file in sys.argv[1:]:
        try:            
            html = open(file).read()
            raw = nltk.clean_html(html)
            output = file[:file.find('/')]
            fout = open(output + '.txt', 'w')
            
            for line in raw.splitlines():
                if line.strip() == 'Filed Under: Digital Humanist Interview':
                    break 
                fout.write(line)
#                print(line)
            fout.close()
        except IOError:
            print('Cannot open', file)
        
def main():
    stripHTML()

main()