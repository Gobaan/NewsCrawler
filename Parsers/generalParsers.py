from jsonpath import jsonpath
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import json, re, collections
import helper
logger = helper.get_logger()

class Comment(object):
  def __init__(self, author, date, text):
    self.author = author
    self.date = date
    self.text = text

class JsonFailedException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)

class BeautifulSoupException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)

class Parser(object):
  def __init__(self):
    self.site = None

  def rename(self, url, site):
    return url

  def fetch_urls(self, url_site):
    newurl_url = {}
    for url, data in url_site.iteritems():
      try:
        newurl_url[self.rename(url, data)] = url
      except Exception, e:
        logger.error('Renaming Failed %s: %s', e, url)

    temp_urls = [url for url in newurl_url if url not in url_site]
    
    if not temp_urls:
      self.url_site = url_site
    else:
      newurl_site = helper.parallel_fetch(newurl_url)
      self.url_site = {url : newurl_site[newurl] for newurl, url in newurl_url.iteritems()}
      self.url_site.update({url:'' for url in url_site if url not in self.url_site})
        

  def process_urls(self):
    self.url_data = {} 
    for url, site in self.url_site.iteritems():
      self.url_data[url] = self.parse(url, site) 

  def parse_all(self, url_site):
    self.fetch_urls(url_site)
    self.process_urls()
    return self.url_data

  def parse(self, url, site):
    try:
      data = self.preprocess(site)
      data = self.custom_parse(data)
      data = self.postprocess(data)
      
    except Exception, e: 
      logger.error('Parse Failed %s : %s', url, e)
      return []

    return data

  # Strips out extra lines etc
  # Input: Stream of html or w.e
  # Output: Only lines and characters necessary of parsing
  def preprocess(self, data): 
    return data

  # Extracts actual useful data
  def custom_parse(self, data): raise 'Not Implemented'
 
  # Extracts actual useful data
  def postprocess(self, data_list): return data_list

class JsonParser(Parser):
  def __init__(self, paths=None):
    Parser.__init__(self)
    self.paths = paths

  def preprocess(self, json_data):
    data = json_data[json_data.find('{'):json_data.rfind('}') + 1]
    return Parser.preprocess(self, data)

  def custom_parse(self, data): 
    data = json.loads(data)
    messages = jsonpath(data, self.paths[0])

    if not messages: 
      raise JsonFailedException(self.paths[0])

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
  def __init__(self, strainer=None, tags=None, attrs=None):
    Parser.__init__(self)
    self.strainer = strainer
    self.tags = tags
    self.attrs = attrs

  #def postprocess_urls(self):
  #  articles = self.url_data.keys()
  #  source = self.url_data.values()
  #  cnt = collections.Counter()
  #  for site in source:
  #    cnt.update(set(site))
  #
  #  # If less than 10% of the other articles in the set contain a phrase, 
  #  # track it
  #  self.url_data = {url : itertools.chain(
  #    [line for line in self.url_data[url] 
  #     if cnt[line] <= 1 + len(source) / 10]) for url in articles}

  #def process_urls(self):
  #  HtmlParser.process_urls(self)
  #  self.postprocess_urls()

  def preprocess(self, data):
    html = ' '.join(re.split('<script.*?</script>', data, flags=re.DOTALL))
    return Parser.preprocess(self, html)

  def custom_parse(self, data):
    try:
      soup = BeautifulSoup(data, self.strainer,
          convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
      soup = soup.findAll(self.tags, self.attrs)
    except TypeError, e:
      raise BeautifulSoupException('Extracting Content %s', e)

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

def pipe(*list_of_func):
  def sequential_version(data):
    for func in list_of_func:
      data = func(data)
    return data
  return sequential_version
 
def make_startswith(string):
  def filter_start(data):
    return '\n'.join([line for line in data.split('\n') if line.startswith(string)])
  return filter_start

class IterativeParser(Parser):
  # Dispatcher, selects which parser to use
  def parse_all(self, url_site):
    raise 'Not Implemented'

