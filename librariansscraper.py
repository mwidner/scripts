'''
Created on Mar 7, 2013

@author: widner
'''
import urllib2
from bs4 import BeautifulSoup
import csv
from collections import namedtuple

path = '/Users/widner/Projects/ATSP/'
#soup = BeautifulSoup(urllib2.urlopen('http://library.stanford.edu/people/subject-librarians').read())
soup = BeautifulSoup(open(path + 'librarians.html').read())
Librarian = namedtuple('Librarian', 'subjects, name')
librarians = list()

table = soup.findAll('table', attrs = {'id' : 'datatable-1'})[0]

for row in table.findAll('tr'):
    for subjectList in row.findAll('td', attrs = {'class' : 'views-field-field-person-subjects'}):
        name = subjectList.findNextSibling('td',attrs = {'class': 'views-field-nothing-1'})
        print(name.string)
        for lists in subjectList.findAll('div', attrs = {'class' : 'item-list'}):
            for subject in lists.findAll('li'):
                pass
#    name = subjectList.find_next_sibling(attrs = {'class': 'views-field-nothing-1'})
#    print(name.string)
#    for col in row.findAll('td', attrs = {'class' : 'views-field-field-person-subjects'}):
#        for subjectList in col.findAll('div', attrs = {'class' : 'item-list'}):
#            for subject in subjectList.findAll('li'):
#                subjects.append(subject.string)
#    for col in row.findAll('td', attrs = {'class' : 'views-field-nothing-1'}):
#        name = col.find('strong').find('div').string
#    librarians.append(Librarian(subjects, name))
#        librarians.append(Librarian(div.string for div in col.findAll('div')))
           
print(librarians)   
#            