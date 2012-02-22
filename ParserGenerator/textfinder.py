import urlparse, socket, urllib
import helper
import sys, re, itertools
import time
from collections import Counter
from selenium import selenium, webdriver
from BeautifulSoup import BeautifulSoup, SoupStrainer


# Currently fails when Request headers contain parameters, but this only
# Happened in one case (wsj) and was easily resolvable with debug info
# So ignore it for now. btw TODO

url_extractor = re.compile('\n  "url":"(.*)",')
browser = '*googlechrome'

with open('urls.txt') as f:
  process = lambda line: line.strip().split('|')
  url_comments = [(process(line)[0], process(line)[1:]) for line in f]

for (url, comments), i in zip(url_comments, itertools.count()):
  if url.startswith('#'): continue
  if len(comments) > 3:
    print 'Warning inconsistent length', url, comments
  parsed_url = urlparse.urlparse(url)
  site = parsed_url.scheme + '://' + parsed_url.netloc
  path = url[url.find(parsed_url.path):]
  
  sel = selenium('127.0.0.1', 4444, browser, site)
  
  try:
      sel.start('captureNetworkTraffic=true')
  except socket.error:
      print 'ERROR - can not start the selenium-rc driver. is your selenium server running?'
      sys.exit(1)
  print site, path     
  sel.set_timeout(300000) # minutes
  try:
    sel.open(path)
  except Exception, e:
    with open('debug/%s.%s' % (parsed_url.netloc, i), 'w') as f:
      f.write(str(e))
    print 'Failed', e
    sel.stop()
    continue

  #if 'abc' in line: # Ajax messes up selenium, write smth generic later
  #time.sleep(60)
  sel.wait_for_page_to_load(60000)
  raw_json = sel.captureNetworkTraffic('json')

  text = sel.get_body_text()
  html = sel.get_html_source()
  sel.stop()
  strainer = SoupStrainer('p')
  soup = BeautifulSoup(text, strainer)
  print '\n------------\n'.join(soup.findAll(text=True))

  soup = BeautifulSoup(html, strainer)
  print '\n------------\n'.join(soup.findAll(text=True))

