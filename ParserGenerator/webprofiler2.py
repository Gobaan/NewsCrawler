import urlparse, socket, urllib
import helper
import sys, re, itertools
import time
from collections import Counter
from selenium import selenium, webdriver


fb_pattern = '<fb:comments(?P<param>.*?)></fb:comments>'
fb_regex = re.compile(fb_pattern)
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
  with open('debug/%s.%s' % (parsed_url.netloc, i), 'w') as f:
    f.write(raw_json)


  uses_fb = fb_regex.search(sel.get_html_source())
  sel.stop()
  if uses_fb:
    default_args = {'origin': '[netloc]',
                    'width': '626', 
                    'locale': 'en_US',
                    'numposts': '10',
                    'href': '[URL]',
                    'relation': 'parent.parent',
                    'api_key': '242325202492798',  # may need to randomly change me
                    'channel_url': 'https://s-static.ak.fbcdn.net/connect/xd_proxy.php?version=3#cb=f37ac5583fdd422',
                    'transport': 'postmessage',
                    'sdk': 'joey'}
    default_args['href'] = url
    default_args['origin'] = parsed_url.netloc
    crafted_url = 'https://www.facebook.com/plugins/comments.php?' + urllib.urlencode(default_args)
    raw_json = '\n  "url":"%s",' % crafted_url


  def get_extension(url):
    parsed_url = urlparse.urlparse(url)
    ext = parsed_url.path.split('.')[-1]
    if '/' in ext: return 'None'
    return ext

  toFetch = [url for url in url_extractor.findall(raw_json)
    if get_extension(url) not in 
    frozenset(['css', 'gif', 'ico', 'jpg', 'png', 'swf', 'woff', 'xml'])]
  ## Filter urls
  ## Search interesting urls

  with open('debug/%s.%s' % (parsed_url.netloc, i), 'a') as f:
    f.write('\n' + '\n'.join(toFetch))

  results = helper.parallel_fetch(toFetch)

  with open('text/%s.%s' % (parsed_url.netloc, i), 'w') as f:
    for url in results:
      f.write(url)
      f.write('\n')
      f.write(results[url])
      f.write('\n-------\n')

  correct_urls = [url for url in results if
     sum([s in str(results[url]) for s in comments])]

  with open('results/%s.%s' % (parsed_url.netloc, i), 'w') as f:
    # Yahoo was the only one returned with multiple urls
    # but both urls had all the data soooo....
    if not correct_urls:
      f.write('Failed [possibly embeds parameters in request]')
    else:
      f.write(correct_urls[0])
      f.write('\n')
      f.write(results[correct_urls[0]])

