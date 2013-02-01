import sys, time, os, urlparse
import multiprocessing, string
from BeautifulSoup import BeautifulSoup, SoupStrainer
import helper
import allParsers
import datetime
import parseBlogs
from collections import namedtuple



logger = helper.get_logger()
#Uses Processing Python Module
#Found at: http://pypi.python.org/pypi/processing
WAITTIME = 10
SEARCH_URL = string.Template('''https://www.google.com/search?q=$query+site%3A$site&num=100&hl=en&lr=&prmd=imvnsulr&sa=X&ei=KlzpTp35Dsjs2QX51ujaCA&ved=0CA0QpwUoBg&source=lnt&tbs=cdr%3A1%2Ccd_min%3A$start_month%2F$start_day%2F$start_year%2Ccd_max%3A$end_month%2F$end_day%2F$end_year&start=$offset&tbm=&complete=0''')
ONE_DAY = datetime.timedelta(1)

SearchResult = namedtuple('SearchResult', ['link', 'title', 'date'])

def end_month(day):
  if day.month == 12:
    return datetime.datetime(day.year, 12, 31)
  return datetime.datetime(day.year, day.month + 1, 1) - ONE_DAY


def get_urls(result_page, site):
  urls = []
  soup = BeautifulSoup(result_page, SoupStrainer('li', {'class':'g'}))
  for s in soup:
    title, link, date, netloc = '', '', '', ''
    for child in s.findAll('a', {'class':'l'}):
      link = child['href']
      title = ''.join(child.findAll(text=True))
      netloc = urlparse.urlparse(link).netloc

    for child in s.findAll('span', {'class':'f std'}):
      date = ''.join(child.findAll(text=True))

    if site in netloc:
      urls += [SearchResult(link, title, date)]

  return urls

class Searcher(object):
  def __init__(self, searchTerm):
    self.searchTerm = searchTerm
    self.curlLock = multiprocessing.Lock()
    helper.set_lock(self.curlLock)
                                                                  
    self.sitelist = allParsers.mapper.keys()
    self.sitelist = ['www.nytimes.com']
    if not os.path.isdir('Results'):
      os.mkdir('Results')
    self.directory = 'Results/' + searchTerm 
    
    #Creates or clears all directories that are going to be used.
    if not os.path.isdir(self.directory):
      os.mkdir(self.directory)
    
    self.max_processes = 4

  def fetch(self, requests, suffix):
    misses = 0
    active_processes = []
    googleRawResults = helper.parallel_fetch(requests.values())
    logger.info(len(self.sitelist))
    for site in self.sitelist:
        data = googleRawResults[requests[site]]
        urls = get_urls(data, site)
        
        logger.info(site)
        logger.info(len(urls))
        if not urls:
          logger.warning('GOOGLE NOT RETURNING ANYTHING')
          logger.warning(requests[site])
                                                                           
          # Don't cache throttle page
          if os.path.isfile('cache/%s.cache' % hash(requests[site])) and \
            'solving the above CAPTCHA' in data or not data:
            os.remove('cache/%s.cache' % hash(requests[site]))
            logger.error('Throttled: Cache cleared')
                                                                           
          # Sleep on misses, so bad searches don't DOS google
          misses += 1
          continue
          
        t = multiprocessing.Process(None, parseBlogs.parseBlogs, site,
              (site,
               self.curlLock,
               urls,
               '%s/%s.%s' % 
                  (self.directory, site.replace('/', '_'), suffix),
               requests[site],
              )
            )
        t.url = requests[site]
        t.start()
                                                                           
        active_processes += [t]
        if self.max_processes <= len(active_processes):
          t = active_processes.pop(0)
          t.join(460)
          if t.is_alive():
            t.terminate()
            logger.error('Terminated Process %s' % t.url)
                                                                           
                                                                           
    for process in active_processes:
        process.join(600)
        process.terminate()

    return misses

  def make_params(self, start_day, last_day):
    params = {'query' : self.searchTerm, 
            'start_month' : start_day.month,
            'start_year' : start_day.year,
            'start_day': start_day.day,
            'end_month' : last_day.month,
            'end_year' : last_day.year,
            'end_day' : last_day.day,
            'offset' : 0,
           }
    return params

  def search_event(self, year, month, day):
    today = datetime.date.today()
    start_day = datetime.date(year, month, day)
    params = self.make_params(start_day, start_day)
    requests = {domain: SEARCH_URL.substitute(params, site=domain)
      for domain in self.sitelist}
    print requests.values()[0]
    misses = self.fetch(requests, '%s.%s.%s' % (start_day.day, start_day.month, start_day.year))
    time.sleep(misses * WAITTIME)

    start_day = start_day + ONE_DAY
    for i in xrange(4):
       last_day = start_day + ONE_DAY * 7
       if start_day > today: break
       params = self.make_params(start_day, last_day)
       requests = {domain: SEARCH_URL.substitute(params, site=domain)
         for domain in self.sitelist}
       print requests.values()[0]
       misses = self.fetch(requests, '%s.%s.%s' % (start_day.day, start_day.month, start_day.year))
       time.sleep(misses * WAITTIME)
       start_day = last_day + ONE_DAY

    last_day = datetime.date(year, month, day) - ONE_DAY
    for i in xrange(4):
       start_day = last_day - ONE_DAY * 7
       params = self.make_params(start_day, last_day)
       requests = {domain: SEARCH_URL.substitute(params, site=domain)
         for domain in self.sitelist}
       print requests.values()[0]
       misses = self.fetch(requests, '%s.%s.%s' % (start_day.day, start_day.month, start_day.year))
       time.sleep(misses * WAITTIME)
       last_day = start_day - ONE_DAY

    logger.info("done %s", self.searchTerm)

  def search_year(self, start_year, start_month = 1, increment = 2):
    for month in xrange(start_month, 12, increment + 1):
       today = datetime.date.today()
       start_day = datetime.date(start_year, month, 1)
       if month + increment > 12: month = 12 - increment
       last_day = end_month(datetime.date(start_year, month + increment, 1))
       if start_day > today: break
       params = self.make_params(start_day, last_day)
       requests = {domain: SEARCH_URL.substitute(params, site=domain)
         for domain in self.sitelist}
       print requests.values()[0]
       misses = self.fetch(requests, '%s.%s' % (month, start_year))
       time.sleep(misses * WAITTIME)
  
    logger.info("done %s", self.searchTerm)
  

if __name__ == '__main__':
  if len(sys.argv) > 1:
    query =  sys.argv[1:]
    searcher = Searcher(query[0])
    searcher.search_event(*query[1:])
  else:
    queries = (\
               #['Northern+Gateway+pipeline', 2011],
               #['GOP+Primary', 2011],
               #['Arab+Spring', 2011],
               #['Arab+Spring', 2010],
               #['SOPA', 2011],
               #['Libya', 2011],
               #['Iraq', 2011],
               #['Iran', 2011],
               #['North+Korea', 2011],
               #['George+Bush', 2004],
               #['John+Kerry', 2004],
               #['Sarah+Palin', 2008],
               #['John+McCain', 2008],
               #['Barack+Obama', 2008],
               #['Joe+Biden', 2008],
               #['Hillary+Clinton', 2008],
               #['GOP+Primary', 2008],
               #['GOP+Primary', 2000],
               #['GOP+Primary', 1996],
               #['GOP+Primary', 1992],
               #['Health+Care', 2011],
               #['Economy', 2011],
               #['Catholic', 2011],
               #['Piracy', 2011],
               #['Piracy', 2010],
               #['RIAA', 2011],
               #['Oil+Prices', 2011],
               #['Natural+Gas', 2011],
               #['Alternative+Energy', 2011],
               #['Alternative+Energy', 2010],
               #['BP', 2011],
               #['news', 2011],
               #['news', 2010],
               #['news', 2009],
               #['news', 2008],
               #['news', 2007],
               #['NYPD', 2011],
               #['Wall+Street', 2011],
               #['occupy+wall+street', 2011],
               #['STOCK+Act', 2011],
               #['Israel', 2011],
               #['Gay+Marriage', 2011],
               #['Facebook', 2011],
               #['Apple', 2011],
               #['Creationism', 2011],
               #['Intelligent+Design', 2011],
               #['Evolution', 2011],
               #['Intelligent+Design', 2011],
               #['Nuclear', 2011],
               #['Steve+Jobs', 2011],
               #['Mark+Zuckerberg', 2011],
               #['Larry+Page', 2011],
               #['Suicide', 2011],
               #['The+Pirate+Bay', 2011],
               #['Bankruptcy', 2011],
               #['Northern+Gateway+pipeline', 2012],
               #['GOP+Primary', 2012],
               #['Arab+Spring', 2012],
               #['SOPA', 2012],
               #['Libya', 2012],
               #['Iraq', 2012],
               #['Iran', 2012],
               #['North+Korea', 2012],
               #['George+Bush', 2012],
               #['John+Kerry', 2012],
               #['Sarah+Palin', 2012],
               #['John+McCain', 2012],
               #['Barack+Obama', 2012],
               #['Joe+Biden', 2012],
               #['Hillary+Clinton', 2012],
               #['GOP+Primary', 2012],
               #['Health+Care', 2012],
               #['Economy', 2012],
               #['Catholic', 2012],
               #['Piracy', 2012],
               #['RIAA', 2012],
               #['Oil+Prices', 2012],
               #['Natural+Gas', 2012],
               #['Alternative+Energy', 2012],
               #['BP', 2012],
               #['news', 2012],
               #['Wall+Street', 2012],
               #['occupy+wall+street', 2012],
               #['STOCK+Act', 2012],
               #['Israel', 2012],
               #['Gay+Marriage', 2012],
               #['Facebook', 2012],
               #['Apple', 2012],
               #['Creationism', 2012],
               #['Intelligent+Design', 2012],
               #['Evolution', 2012],
               #['Intelligent+Design', 2012],
               #['Nuclear', 2012],
               #['Steve+Jobs', 2012],
               #['Mark+Zuckerberg', 2012],
               #['Larry+Page', 2012],
               #['Suicide', 2012],
               #['The+Pirate+Bay', 2012],
               #['Bankruptcy', 2012],
               #['Israel+Iran+Bombing', 2012],
               #['clone+Dolly+sheep', 2006],
               #['Kony', 2012],
               #['Charlie+Sheen', 2011],
               #['Arab+Spring', 2012],
               #['ACTA', 2012],
               #['GOP+Primaries', 2012],
               #['Anonymous', 2012],
               #['Greece', 2012],
               #['SOPA', 2012],
               #['Israel+Bombing+Iran', 2012],
               #['Kobo+Vox', 2012],
               #['global+warming', 2012],
               #['Rick+Santorum', 2012],
               #['batman', 2012],
               #['dark+knight+rises', 2012],
               #['olympics', 2012],
               #['NASA', 2012],
               #['Steve+Jobs', 2012],
               #['Cars', 2012],
               # ['Justin+Bieber', 2012],
              )
  
    for query in queries:
      searcher = Searcher(query[0])
      searcher.search_event(query[1])

    queries = (('climate+change', (2012, 10, 24)),
               ('gun+control', (2012, 12, 14)),
               ('polling+accuracy', (2012, 11, 6)),
              )
    for query in queries:
      searcher = Searcher(query[0])
      searcher.search_event(*query[1])
