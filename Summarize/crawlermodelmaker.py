import os, sys, re
from collections import Counter
import json
import nltk
import BeautifulSoup

def get_terms(text):
  #return [stemmer.stem(word) for word in nltk.word_tokenize(sentence)]
  return [word for sentence in nltk.sent_tokenize(text) 
          for word in nltk.word_tokenize(sentence)]

folder = sys.argv[1]
query_terms = [query.lower() for query in sys.argv[2:]]
#Share seen_urls files for a given query
seenfile = 'models/%s.seen.json' % '_'.join(query_terms)
filename = '_'.join([folder] + query_terms)
model1 = Counter()
model2 = Counter()

seen_urls = {}
if os.path.isfile(seenfile):
  with open(seenfile, 'r') as fp:
    seen_urls = json.load(fp)

doc_regex = re.compile('<doc>(?P<text>.*?)</doc>', re.DOTALL)
url_regex = re.compile('<url>(?P<text>.*?)</url>', re.DOTALL)
article_regex = re.compile('<body>(?P<text>.*?)</body>', re.DOTALL)
comment_regex = re.compile('<text>(?P<text>.*?)</text>', re.DOTALL)
our_comments, their_comments = 0, 0 
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
      if url in seen_urls: 
        num_duplicates += 1
        continue
      seen_urls[url] = 0
      selector = sum([query in article for query in query_terms]) == \
          len(query_terms)

      for comment_match in comment_regex.finditer(document): 
        text = comment_match.group('text')
        soup = BeautifulSoup.BeautifulSoup(text, fromEncoding = 'utf-8',
          convertEntities=BeautifulSoup.BeautifulStoneSoup.HTML_ENTITIES)
        comment = ' '.join(soup.findAll(text = True))
        if selector:
          model1.update(set(get_terms(comment)))
          our_comments += 1
        else:
          model2.update(set(get_terms(comment)))
          their_comments += 1

print 'Number of duplicates:', num_duplicates

print our_comments, their_comments
with open('models/%s.matched' % filename, 'w') as output:
  json.dump({'model': model1, 'len': our_comments}, output)

with open('models/%s.unmatched' % filename, 'w') as output:
  json.dump({'model': model2, 'len': their_comments}, output)
  
with open(seenfile, 'w') as fp:
  json.dump(seen_urls, fp)
