import sys, time, os, urlparse
import multiprocessing, string
from BeautifulSoup import BeautifulSoup, SoupStrainer
import helper
import allParsers
import datetime
import parseBlogs

logger = helper.get_logger()
#Uses Processing Python Module
#Found at: http://pypi.python.org/pypi/processing
WAITTIME = 10
SEARCH_URL = string.Template('''https://www.google.com/search?q=$query+site%3A$site&num=100&hl=en&lr=&prmd=imvnsulr&sa=X&ei=KlzpTp35Dsjs2QX51ujaCA&ved=0CA0QpwUoBg&source=lnt&tbs=cdr%3A1%2Ccd_min%3A$start_month%2F1%2F$start_year%2Ccd_max%3A$end_month%2F30%2F$end_year&start=$offset&tbm=&complete=0''')

def get_urls(result_page, site):
  urls = []
  soup = BeautifulSoup(result_page, SoupStrainer('a'))
  for s in soup.findAll('a'):
    try:
      link = s['href']
    except KeyError:
      continue
    netloc = urlparse.urlparse(link).netloc
    if site in netloc: 
      urls += [link]

  return urls

def blogSearch(searchTerm, start_year, start_month = 1, increment = 2):
    curlLock = multiprocessing.Lock()
    helper.set_lock(curlLock)

    sitelist = allParsers.mapper.keys()
    sitelist = [site for site in sitelist if 'cnn.com' in site]
    if not os.path.isdir('Results'):
      os.mkdir('Results')
    directory = 'Results/' + searchTerm 
    
    #Creates or clears all directories that are going to be used.
    if not os.path.isdir(directory):
      os.mkdir(directory)
    
    #Establish Connection to Bing.
    # Need to lock on io before doing this
    max_processes = 4
    active_processes = []
    for month in xrange(start_month, 12, increment + 1):
       today = datetime.date.today()
       if datetime.date(start_year, month, 1) > today: break
       misses = 0
       params = {'query' : searchTerm, 
                 'start_month' : month,
                 'start_year' : start_year,
                 'end_month' : month + increment,
                 'end_year' : start_year,
                 'offset' : 0
                }

       requests = {domain: SEARCH_URL.substitute(params, site=domain)
         for domain in sitelist}
       googleRawResults = helper.parallel_fetch(requests.values())
       logger.info(len(sitelist))
       for site in sitelist:
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
                  curlLock,
                  urls,
                  '%s/%s.%s.%s' % 
                     (directory, site.replace('/', '_'), month, start_year),
                  requests[site],
                 )
               )
           t.url = requests[site]
           t.start()

           active_processes += [t]
           if max_processes <= len(active_processes):
             t = active_processes.pop(0)
             t.join(460)
             if t.is_alive():
               t.terminate()
               logger.error('Terminated Process %s' % t.url)


       for process in active_processes:
           process.join(600)
           process.terminate()

       time.sleep(misses * WAITTIME)

    logger.info("done %s", searchTerm)


if __name__ == '__main__' and len(sys.argv) > 1:
  blogSearch(sys.argv[1:])
