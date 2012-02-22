import os, sys, re, math
from collections import Counter
import json
import nltk
import HTMLParser
import BeautifulSoup

def get_terms(text):
  #return [stemmer.stem(word) for word in nltk.word_tokenize(sentence)]
  return [word for sentence in nltk.sent_tokenize(text) 
          for word in nltk.word_tokenize(sentence)]

query_terms = [query.lower() for query in sys.argv[3:]]
folder = sys.argv[1]
target_filename = '_'.join([folder] + query_terms)

with open('models/%s.matched' % target_filename, 'r') as infile:
  target_model = json.load(infile)

try:
  with open('models/background.model', 'r') as infile:
    background_model = json.load(infile)
except IOError, e:
  with open('models/wiki.model', 'r') as infile:
    background_model = json.load(infile)

term_score = {}

for term in target_model['model']:
  try:
    bt = background_model['model'][term] / float(background_model['len'])
  except KeyError, e:
    bt = 1 / float(background_model['len'])
  mt = target_model['model'][term] / float(target_model['len'])
  term_score[term] = max(0, mt * math.log(mt / bt))

doc_regex = re.compile('<doc>(?P<text>.*?)</doc>', re.DOTALL)
url_regex = re.compile('<url>(?P<text>.*?)</url>', re.DOTALL)
article_regex = re.compile('<body>(?P<text>.*?)</body>', re.DOTALL)
comment_regex = re.compile('<text>(?P<text>.*?)</text>', re.DOTALL)
parser = HTMLParser.HTMLParser()
our_comments, their_comments = 0, 0 
target_comments = []
# Train a model using all the documents in the folder
for root, dirs, files in os.walk(folder):
  print root
  num_duplicates = 0
  for name in files:
    with open(os.path.join(root, name)) as infile:
      data = ''.join(infile.readlines())
      
    for doc_match in doc_regex.finditer(data):
      document = doc_match.group('text')
      article_match = article_regex.search(document)
      try:
        article = article_match.group('text').lower()
      except Exception, e:
        print document
        raise
      url = url_regex.search(document).group('text')
      selector = sum([query in article for query in query_terms]) == \
          len(query_terms)

      for comment_match in comment_regex.finditer(document): 
        text = comment_match.group('text')
        soup = BeautifulSoup.BeautifulSoup(text, fromEncoding = 'utf-8',
          convertEntities=BeautifulSoup.BeautifulStoneSoup.HTML_ENTITIES)
        comment = ' '.join(soup.findAll(text = True))#.encode('utf-8')
        if selector:
          our_comments += 1
          target_comments += [comment]
        else:
          their_comments += 1

missing_terms = 0

def get_terms(comment):
  global missing_terms
  #return [stemmer.stem(word) for word in nltk.word_tokenize(sentence)]
  terms = set([word for sentence in nltk.sent_tokenize(comment)
      for word in nltk.word_tokenize(sentence)])
  known_terms = [term for term in terms if term in term_score]
  #if unknown_terms:
  #  print [term.encode('utf-8', 'ignore') for term in unknown_terms]
  missing_terms += len(terms) - len(known_terms)
  return known_terms

decorated_comments = [(comment, set(get_terms(comment))) for comment in target_comments]
print missing_terms

def get_score_fn(delta = 40):
  def score((comment, terms)):
    return sum([term_score[term] for term in terms]) / (len(terms) + delta)
  return score

sorter = get_score_fn()
for i in xrange(10):
  decorated_comments.sort(key = sorter)
  best_comment = decorated_comments.pop()
  for term in best_comment[1]:
    term_score[term] = 0
  print best_comment[0].strip().encode('utf-8')
  print ''
  print '--------'

