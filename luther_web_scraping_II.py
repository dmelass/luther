# Dara Elass

import urllib2
from bs4 import BeautifulSoup
import re
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import codecs

def convert_dollars_to_numbers(value):
    return int(value.replace('$','').replace(',',''))

def get_movie_name(soup):
    return soup.find("h1").text

def get_budget(soup):
    budget = soup.find('div',id = "summary").find('b',text = re.compile("Budget")).findNext('td').text
    return budget

def get_director(soup):
    director = soup.findAll('div',id = re.compile("cast"))[-1].find('td',text = re.compile("Director")).findNext('a').text
    return director
                 
def get_director_url(soup):
    director_url = soup.findAll('div',id = re.compile("cast"))[-1].find('td',text = re.compile("Director")).findNext('a')['href']
    return 'http://www.the-numbers.com'+director_url

def get_opening_wknd_gross(soup):
    opening_wknd_gross = soup.find('a',href = re.compile("/box-office-chart/weekend/")).findNext('td').findNext('td').text
    return opening_wknd_gross

# top 3 actor names
def get_actors_names(soup):
    actors = soup.find('div',id = re.compile("cast-and-crew")).findAll('a',href = re.compile("/person"))
    actor_names = []
    for i in range(3): # for top 3 only
         actor_names.append(actors[i].text)
    return actor_names

# top 3 actor urls
def get_actor_urls(soup):
    actors = soup.find('div',id = re.compile("cast-and-crew")).findAll('a',href = re.compile("/person"))
    actor_urls = []
    for i in range(3): # for top 3 only
         actor_urls.append('http://www.the-numbers.com'+actors[i]['href'])
    return actor_urls

def connect(url):
    page = urllib2.urlopen(url)
    return BeautifulSoup(page.read())

def get_director_domestic_gross(director_url): #get director gross for years in the training set
    soup = connect(director_url)
    grosses = []
    table_soup = soup.find('div',id = "technical")
    movies = table_soup.findAll('a')
    for movie in movies:
        release_date = movie.parent.find_previous_sibling('td').text
        year = int(release_date.split('/')[2])
        if year <= training_set_end_year:
            dom_gross = movie.parent.findNext('td').findNext('td').findNext('td').text
            dom_gross = dom_gross.replace('$','').replace(',','')
            grosses.append(int(dom_gross))
    dir_gross = sum(grosses)/len(grosses)
    return dir_gross

def get_actor_domestic_gross(actor_url): #get actor gross for years in the training set
    soup = connect(actor_url)
    grosses = []
    table_soup = soup.find('div',id = "acting")
    movies = table_soup.findAll('a')
    for movie in movies:
        release_date = movie.parent.find_previous_sibling('td').text
        year = int(release_date.split('/')[2])
        if year <= training_set_end_year:
            dom_gross = movie.parent.findNext('td').findNext('td').findNext('td').text
            dom_gross = dom_gross.replace('$','').replace(',','')
            grosses.append(int(dom_gross))
    act_gross = sum(grosses)/len(grosses)
    return act_gross
    
def get_movie_summary_information(movie_url): #used for testing purposes
    name = get_movie_name()
    budget = get_budget()
    director = get_director()
    opening_wknd = get_opening_wknd_gross()
    actors = get_actors_names()
    actor_urls = get_actor_urls()
    director_url = get_director_url()
    dir_gross = get_director_domestic_gross(director_url)
    actor_grosses = []
    for actor_url in actor_urls:
        actor_grosses.append(get_actor_domestic_gross(actor_url))
    print 'movie name:', name
    print 'budget:', budget
    print 'budget as integer:', convert_dollars_to_numbers(budget)
    print 'director:', director
    print 'director url:', director_url
    print 'opening weekend gross:', opening_wknd
    print 'opening weekend gross as integer:', convert_dollars_to_numbers(opening_wknd)
    print 'top 3 actors:', actors
    print 'top 3 actor urls:', actor_urls
    print 'director total domestic gross:', dir_gross
    print 'actor grosses:',actor_grosses

## define training/test set years
training_set_end_year = 2010
testing_set_beginning_year = training_set_end_year+1

#set up driver and website
action_movies_url = "http://www.the-numbers.com/movies/genre/Action"
action_movie_soup = connect(action_movies_url)

#get urls of all action movies from The Numbers
print 'getting action urls/dates'
urls = []
dates = []
for url in action_movie_soup.find('div',id = "page_filling_chart").findAll('a',href = re.compile("/movie/")):
    urls.append('http://www.the-numbers.com'+url['href'])

for date in action_movie_soup.find('div',id = "page_filling_chart").findAll('a',href = re.compile("/box-office-chart/daily/")):
    dates.append(date.text)

print 'got urls, number of urls:',len(urls)
print 'got dates, number od dates:',len(dates)
print 'starting csv'
import time
with codecs.open('action_movies.csv','w',encoding='ascii') as action_movies:
    a = csv.writer(action_movies)
    a.writerow([s.encode('utf-8') for s in ['Movie','Release Date','Budget','Opening Weekend','Director','Director Gross','Actors','Actor Grosses']])
    print 'wrote headers'
    for i,action_url in enumerate(urls):     
        print 'starting data on:', action_url
        print 'movie ',i,' of ', len(urls)
        movie_soup = connect(action_url)
        name = get_movie_name(movie_soup)
        print 'Name:',name
        date = dates[i]
        print 'Release Date:', date
        try:
            budget = convert_dollars_to_numbers(get_budget(movie_soup))
        except AttributeError:          
            budget = 'N/A'
        print 'Budget:', budget
        try:
            director = get_director(movie_soup)
        except AttributeError:
            director = 'N/A'
        print 'Director:', director
        try:
            director_url = get_director_url(movie_soup)
        except AttributeError:
            director_url = ''
        print director_url
        try:
            actors = get_actors_names(movie_soup)
        except IndexError:
            actors = []
        print 'Actors:',actors
        try:
            actor_urls = get_actor_urls(movie_soup)
        except IndexError:
            actor_urls = []
        print actor_urls
        try:
            dir_gross = get_director_domestic_gross(director_url)
        except ValueError:
            dir_gross = ''
        except AttributeError:
            dir_gross = ''
        except ZeroDivisionError:
            dir_gross = ''
        print 'Director Average Gross:', dir_gross
        try:
            opening_wknd = convert_dollars_to_numbers(get_opening_wknd_gross(movie_soup))
        except AttributeError:
            opening_wknd = 'N/A'
        except ValueError:
            opening_wknd = 'N/A'
        except:
            pass
        print 'Opening Wknd Gross:', opening_wknd
        actor_grosses = []
        try:
            for actor_url in actor_urls:
                actor_grosses.append(get_actor_domestic_gross(actor_url))
        except ZeroDivisionError:
            actor_grosses = []
        print 'Actor Average Gross:',actor_grosses
        data = [name, date, budget, opening_wknd, director, dir_gross, actors, actor_grosses]
        try:
            a.writerow([unicode(d).encode('ascii', 'ignore' ) for d in data])
        except:
            pass
        print 'wrote data for:', name
