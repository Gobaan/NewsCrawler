from jsonpath import jsonpath
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from string import Template
import json, re, collections, time
import helper
from types import FunctionType, MethodType
logger = helper.get_logger()

class Comment(object):
  def __init__(self, author, date, text):
    self.author = author
    self.date = date
    self.text = text

  def __hash__(self):
    return hash(self.text)

  def __eq__(self, other):
    return (self.author == other.author and self.date == other.date 
       and self.text == other.text)

class JSONFailedException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)

class BeautifulSoupException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)

class Parser(object):
  def __init__(self, **params):
    self.site = None
    self.max_iterations = 1
    self.starting = ""
    for key in params:
      if type(params[key]) == FunctionType:
        params[key] = MethodType(params[key], self)
      setattr(self, key, params[key])

  def rename(self, url, site):
    return Template(url)
  
  def set_template_urls(self):
    self.url_template = {}
    for url, site in self.url_site.iteritems():
      try:
        self.url_template[url] = self.rename(url, site)
      except Exception, e:
        logger.error('Renaming Failed %s: %s', e, url)

  def getNextUrls(self, iteration):
    return {url : self.url_template[url].safe_substitute(iteration=iteration) 
        for url in self.found 
        if url in self.url_template #and len(self.url_data[url]) % self.iterate == 0
      }
  
  def process_urls(self):
    for url, site in self.url_site.iteritems():
      self.url_data[url] += self.parse(url, site) 

  def parse_all(self, url_site):
    self.url_site = url_site
    self.set_template_urls()
    self.url_data = {url:[] for url in url_site}
    
    self.found = set(url_site.keys())
    iteration = 1
    for iteration in xrange(1, self.max_iterations + 1):
      url_next = self.getNextUrls(iteration)
      if not url_next: break
      if iteration > 1: time.sleep(10)
      nexturl_site = helper.parallel_fetch(url_next.values())
      self.url_site = {url : nexturl_site[newurl] for url, newurl in url_next.iteritems()}
      self.mapping = {url : newurl for url, newurl in url_next.iteritems()}
      self.found = set()
      self.process_urls()
      logger.info('iteration %s complete', iteration)
      logger.info('%s uncompleted', len(self.found))

    if self.max_iterations > 1 and iteration == self.max_iterations:
      logger.error('Iterated %s times, possible infinite loop', iteration)

    return self.url_data

  def parse(self, url, site):
    try:
      data = self.filter(site)
      data = self.preprocess(data)
      data = self.custom_parse(data)
      data = self.postprocess(data)
    except Exception, e: 
      if url not in self.mapping: self.mapping[url] = url
      target_url = self.mapping[url]
      logger.error('Parse Failed %s - %s : %s', target_url, hash(target_url), e)
      if url != target_url:
        logger.error('Originally %s - %s : %s', url, hash(url), e)
      return []     

    if len(data) == 0:
      return []

    if data[0] in self.url_data[url]: 
      logger.debug('Duplicate Comments: %s', url)
      return []

    self.found.update([url])
    return data

  def filter(self, data):
    return '\n'.join([line for line in data.split('\n') 
      if line.startswith(self.starting)])


  # Strips out extra lines etc
  # Input: Stream of html or w.e
  # Output: Only lines and characters necessary of parsing
  def preprocess(self, data): 
    return data

  # Extracts actual useful data
  def custom_parse(self, data): raise 'Not Implemented'
 
  # Extracts actual useful data
  def postprocess(self, data_list): return data_list

class JSONParser(Parser):
  def __init__(self, **params):
    self.paths = None
    Parser.__init__(self, **params)

  def preprocess(self, json_data):
    data = json_data[json_data.find('{'):json_data.rfind('}') + 1]
    return Parser.preprocess(self, data)

  def custom_parse(self, data): 
    data = json.loads(data)
    messages = jsonpath(data, self.paths[0])

    if not messages: 
      raise JSONFailedException(self.paths[0])

    return  [Comment('Not Implemented', 'Not Implemented', text) for text in messages]

  # Cleans out tags and entities from json
  def postprocess(self, data_list):
    for comment in data_list:
      soup = BeautifulSoup(comment.text, 
          convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
      comment.text = ' '.join(soup.findAll(text=True))
    return data_list

class DummyParser(Parser): 
  def custom_parse(self, data):
    return []

class HtmlParser(Parser): 
  def __init__(self, **params):
    self.strainer = None
    self.targets = None
    Parser.__init__(self, **params)

  def preprocess(self, data):
    html = ' '.join(re.split('<script.*?</script>', data, flags=re.DOTALL))
    return Parser.preprocess(self, html)

  def custom_parse(self, data):
    try:
      soup = BeautifulSoup(data, self.strainer,
          convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
      soup = soup.findAll(self.targets.name, self.targets.attrs)
    except TypeError, e:
      raise BeautifulSoupException('Extracting Content %s' % e)

    data = [Comment('Not Implemented', 'Not Implemented', ' '.join(s.findAll(text=True))) for s in soup]
    return data

class EscapedHtmlParser(HtmlParser):
  def preprocess(self, data):
    html = data.decode("string-escape").replace('\/','/')
    return HtmlParser.preprocess(self, html)

class AsyncHtmlParser(EscapedHtmlParser):
  def preprocess(self, data):
    html = data[data.find('\'') + 1:data.rfind('\'')]
    return EscapedHtmlParser.preprocess(self, html)

class IterativeParser(Parser):
  def __init__(self, **params):
    self.dispatchers = []
    Parser.__init__(self, **params)

  # Dispatcher, selects which parser to use
  def parse_all(self, url_site):
    rest_urls = url_site
    results = {}
    for selector, parser in self.dispatchers:
      target_urls  = {url:url_site[url] for url in rest_urls 
        if selector(url)}
      rest_urls = {url:url_site[url] for url in rest_urls 
        if url not in target_urls}
      results.update(parser.parse_all(target_urls))
    return results

def check_any_attr(text):
  def check_attrs(name, attrs):
    return name == 'div' and text in [attr[1] for attr in attrs]
  return check_attrs
