import pycurl
from time import time 
import os, uuid
import urlparse

import logging
FORMAT = "%(asctime)-15s %(levelname)s | %(filename)s : %(lineno)d : %(processName)s - %(message)s"
DATE_FORMAT = '%m/%d %H:%M:%S'
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt=DATE_FORMAT)
logger = logging.getLogger('parsers')
fh = logging.FileHandler('parsers.log')
fh.setLevel(logging.INFO)
fh.setFormatter(logging.Formatter(FORMAT))
logger.addHandler(fh)

def get_logger(): 
  return logger

if not os.path.isdir('cache'):
  os.mkdir('cache')
# Set the singleton lock
lock = None

def set_lock(newlock):
  global lock
  lock = newlock

def process_wrapper (url, outputs):
  outputs[url] = []
  def store(buf):
    outputs[url] += [buf]
  return store

def parallel_fetch(urls, cache=True, clear=False):
  """ 
  Given a set of URLs fetches all of them in parallel and returns
  all the responses at once. We cannot process them in parallel
  because the data is returned as a partial buffer
  """

  for url in urls:
    path = 'cache/%s.cache' % hash(url)
    if clear and not 'google.com' in url and os.path.isfile(path):
      os.remove(path)


  responses = {}
  for url in urls:
    if not cache or not os.path.isfile('cache/%s.cache' % hash(url)):
      continue
    with open('cache/%s.cache' % hash(url), 'rb') as cache_file:
      responses[url] = cache_file.read()
  
  m = pycurl.CurlMulti()
  urls = set(urls) - set(responses)
  logger.info('fetching %s', len(urls))
  try:
    if lock: lock.acquire()
  except EOFError:
    logger.critical('THE LOCK IS DEAD, THIS MEANS THE MAIN PROGRAM TERMINATED UNEXPECTEDLY')
    raise
  handles = []
  for link in urls:
    c = pycurl.Curl()
    c.setopt(pycurl.URL, link.encode('utf-8'))
    c.setopt(pycurl.MAXREDIRS, 50)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.CONNECTTIMEOUT, 60)
    c.setopt(pycurl.TIMEOUT, 600)
    c.setopt(pycurl.NOSIGNAL, 1)
    c.setopt(pycurl.WRITEFUNCTION, process_wrapper(link, responses))
    c.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.77 Safari/535.7')
    c.setopt(pycurl.COOKIEFILE, 'cookie.txt')

    c.link = link
    handles += [c]
    m.add_handle(c)

  num_processed = 0
  start = time()
  #This busy loops? with some blocking TODO: Find out if there is a better way 
  while num_processed < len(urls):
    while 1:
      ret, num_handles = m.perform()
      if not ret == pycurl.E_CALL_MULTI_PERFORM: break

    num_q = 1
    while num_q:
      num_q, ok_list, err_list = m.info_read()
      for c in ok_list:
        m.remove_handle(c)
        c.close()
        handles.remove(c)

      for c, errno, errmsg in err_list:
        responses[c.link] = ['Failed', str(c.link), str(errno), str(errmsg)]
        m.remove_handle(c)
        c.close()
        handles.remove(c)
      num_processed += len(ok_list) + len(err_list)

    m.select(60)
    if time() - start > 60:
      logger.error('Timeout: processing domain %s', list(urls)[0])
      logger.debug([url for url in urls if not responses[url]])
      break
  if lock: lock.release()

  for url in responses:
    responses[url] = ''.join(responses[url])
    if not cache or os.path.isfile('cache/%s.cache' % hash(url)): continue
    with open('cache/%s.cache' % hash(url), 'wb') as cache_file:  
      cache_file.write(responses[url])

  return responses
